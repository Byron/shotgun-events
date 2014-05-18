#-*-coding:utf-8-*-
"""
@package sgevents.plugin
@brief Keeps base for EventEngine plugins

@author Sebastian Thiel
@copyright [MIT License](http://www.opensource.org/licenses/mit-license.php)
"""
__all__ = []

import os
import weakref


class EventEnginePluginCollection(object):
    """
    A group of plugin files in a location on the disk.
    """
    def __init__(self, engine, path):
        if not os.path.isdir(path):
            raise ValueError('Invalid path: %s' % path)

        self._engine = weakref.proxy(engine)
        self.path = path
        self._plugins = {}
        self._stateData = {}

    def set_state(self, state):
        if isinstance(state, int):
            for plugin in self:
                plugin.set_state(state)
                self._stateData[plugin.name()] = plugin.state()
        else:
            self._stateData = state
            for plugin in self:
                pluginState = self._stateData.get(plugin.name())
                if pluginState:
                    plugin.set_state(pluginState)

    def state(self):
        for plugin in self:
            self._stateData[plugin.name()] = plugin.state()
        return self._stateData

    def next_unprocessed_event_id(self):
        eId = None
        for plugin in self:
            if not plugin.is_active():
                continue

            newId = plugin.next_unprocessed_event_id()
            if newId is not None and (eId is None or newId < eId):
                eId = newId
        return eId

    def process(self, event):
        for plugin in self:
            if plugin.is_active():
                plugin.process(event)
            else:
                plugin.logger.debug('Skipping: inactive.')

    def load(self):
        """
        Load plugins from disk.

        General behavior:
        - Loop on all paths.
        - Find all valid .py plugin files.
        - Loop on all plugin files.
        - For any new plugins, load them, otherwise, refresh them.
        """
        newPlugins = {}

        for basename in os.listdir(self.path):
            if not basename.endswith('.py') or basename.startswith('.'):
                continue

            if basename in self._plugins:
                newPlugins[basename] = self._plugins[basename]
            else:
                newPlugins[basename] = EventEnginePlugin(self._engine, os.path.join(self.path, basename))

            newPlugins[basename].load()

        self._plugins = newPlugins

    def __iter__(self):
        for basename in sorted(self._plugins.keys()):
            yield self._plugins[basename]



class EventEnginePlugin(object):
    """
    The plugin class represents a file on disk which contains one or more
    callbacks.
    """
    def __init__(self, engine, path):
        """
        @param engine: The engine that instanciated this plugin.
        @type engine: L{EventEngine}
        @param path: The path of the plugin file to load.
        @type path: I{str}

        @raise ValueError: If the path to the plugin is not a valid file.
        """
        self._engine = weakref.proxy(engine)
        self._path = path

        if not os.path.isfile(path):
            raise ValueError('The path to the plugin is not a valid file - %s.' % path)

        self._pluginName = os.path.splitext(os.path.split(self._path)[1])[0]
        self._active = True
        self._callbacks = []
        self._mtime = None
        self._lastEventId = None
        self._backlog = {}

        # Setup the plugin's logger
        self.logger = logging.getLogger('plugin.' + self.name())
        self.logger.config = self._engine.config
        self._engine.set_emails_on_logger(self.logger, True)
        self.logger.setLevel(self._engine.config.getLogLevel())
        if self._engine.config.getLogMode() == 1:
            set_file_path_on_logger(self.logger, self._engine.config.getLogFile('plugin.' + self.name()))

    def name(self):
        return self._pluginName

    def set_state(self, state):
        if isinstance(state, int):
            self._lastEventId = state
        elif isinstance(state, types.TupleType):
            self._lastEventId, self._backlog = state
        else:
            raise ValueError('Unknown state type: %s.' % type(state))

    def state(self):
        return (self._lastEventId, self._backlog)

    def next_unprocessed_event_id(self):
        if self._lastEventId:
            nextId = self._lastEventId + 1
        else:
            nextId = None

        now = datetime.datetime.now()
        for k in self._backlog.keys():
            v = self._backlog[k]
            if v < now:
                self.logger.warning('Timeout elapsed on backlog event id %d.', k)
                del(self._backlog[k])
            elif nextId is None or k < nextId:
                nextId = k

        return nextId

    def is_active(self):
        """
        Is the current plugin active. Should it's callbacks be run?

        @return: True if this plugin's callbacks should be run, False otherwise.
        @rtype: I{bool}
        """
        return self._active

    def set_emails(self, *emails):
        """
        Set the email addresses to whom this plugin should send errors.

        @param emails: See L{LogFactory.getLogger}'s emails argument for info.
        @type emails: A I{list}/I{tuple} of email addresses or I{bool}.
        """
        self._engine.set_emails_on_logger(self.logger, emails)

    def load(self):
        """
        Load/Reload the plugin and all its callbacks.

        If a plugin has never been loaded it will be loaded normally. If the
        plugin has been loaded before it will be reloaded only if the file has
        been modified on disk. In this event callbacks will all be cleared and
        reloaded.

        General behavior:
        - Try to load the source of the plugin.
        - Try to find a function called registerCallbacks in the file.
        - Try to run the registration function.

        At every step along the way, if any error occurs the whole plugin will
        be deactivated and the function will return.
        """
        # Check file mtime
        mtime = os.path.getmtime(self._path)
        if self._mtime is None:
            self._engine.log.info('Loading plugin at %s' % self._path)
        elif self._mtime < mtime:
            self._engine.log.info('Reloading plugin at %s' % self._path)
        else:
            # The mtime of file is equal or older. We don't need to do anything.
            return

        # Reset values
        self._mtime = mtime
        self._callbacks = []
        self._active = True

        try:
            plugin = imp.load_source(self._pluginName, self._path)
        except:
            self._active = False
            self.logger.error('Could not load the plugin at %s.\n\n%s', self._path, traceback.format_exc())
            return

        regFunc = getattr(plugin, 'registerCallbacks', None)
        if isinstance(regFunc, types.FunctionType):
            try:
                regFunc(Registrar(self))
            except:
                self._engine.log.critical('Error running register callback function from plugin at %s.\n\n%s', self._path, traceback.format_exc())
                self._active = False
        else:
            self._engine.log.critical('Did not find a registerCallbacks function in plugin at %s.', self._path)
            self._active = False

    def register_callback(self, sgScriptName, sgScriptKey, callback, matchEvents=None, args=None):
        """
        Register a callback in the plugin.
        """
        global sg
        sgConnection = sg.Shotgun(self._engine.config.getShotgunURL(), sgScriptName, sgScriptKey)
        self._callbacks.append(Callback(callback, self, self._engine, sgConnection, matchEvents, args))

    def process(self, event):
        if event['id'] in self._backlog:
            if self._process(event):
                del(self._backlog[event['id']])
                self._update_last_event_id(event['id'])
        elif self._lastEventId is not None and event['id'] <= self._lastEventId:
            msg = 'Event %d is too old. Last event processed was (%d).'
            self.logger.debug(msg, event['id'], self._lastEventId)
        else:
            if self._process(event):
                self._update_last_event_id(event['id'])

        return self._active

    def _process(self, event):
        for callback in self:
            if callback.is_active():
                if callback.can_process(event):
                    msg = 'Dispatching event %d to callback %s.'
                    self.logger.debug(msg, event['id'], str(callback))
                    if not callback.process(event):
                        # A callback in the plugin failed. Deactivate the whole
                        # plugin.
                        self._active = False
                        break
            else:
                msg = 'Skipping inactive callback %s in plugin.'
                self.logger.debug(msg, str(callback))

        return self._active

    def _update_last_event_id(self, eventId):
        if self._lastEventId is not None and eventId > self._lastEventId + 1:
            expiration = datetime.datetime.now() + datetime.timedelta(minutes=5)
            for skippedId in range(self._lastEventId + 1, eventId):
                self.logger.debug('Adding event id %d to backlog.', skippedId)
                self._backlog[skippedId] = expiration
        self._lastEventId = eventId

    def __iter__(self):
        """
        A plugin is iterable and will iterate over all its L{Callback} objects.
        """
        return self._callbacks.__iter__()

    def __str__(self):
        """
        Provide the name of the plugin when it is cast as string.

        @return: The name of the plugin.
        @rtype: I{str}
        """
        return self.name()




class Registrar(object):
    """
    See public API docs in docs folder.
    """
    def __init__(self, plugin):
        """
        Wrap a plugin so it can be passed to a user.
        """
        self._plugin = plugin
        self._allowed = ['logger', 'set_emails', 'register_callback']

    def __getattr__(self, name):
        if name in self._allowed:
            return getattr(self._plugin, name)
        raise AttributeError("type object '%s' has no attribute '%s'" % (type(self).__name__, name))


class Callback(object):
    """
    A part of a plugin that can be called to process a Shotgun event.
    """

    def __init__(self, callback, plugin, engine, shotgun, matchEvents=None, args=None):
        """
        @param callback: The function to run when a Shotgun event occurs.
        @type callback: A function object.
        @param engine: The engine that will dispatch to this callback.
        @type engine: L{EventEngine}.
        @param shotgun: The Shotgun instance that will be used to communicate
            with your Shotgun server.
        @type shotgun: L{sg.Shotgun}
        @param logger: An object to log messages with.
        @type logger: I{logging.Logger}
        @param matchEvents: The event filter to match events against befor invoking callback.
        @type matchEvents: dict
        @param args: Any datastructure you would like to be passed to your
            callback function. Defaults to None.
        @type args: Any object.

        @raise TypeError: If the callback is not a callable object.
        """
        if not callable(callback):
            raise TypeError('The callback must be a callable object (function, method or callable class instance).')

        self._name = None
        self._shotgun = shotgun
        self._callback = callback
        self._engine = weakref.proxy(engine)
        self._logger = None
        self._matchEvents = matchEvents
        self._args = args
        self._active = True

        # Find a name for this object
        if hasattr(callback, '__name__'):
            self._name = callback.__name__
        elif hasattr(callback, '__class__') and hasattr(callback, '__call__'):
            self._name = '%s_%s' % (callback.__class__.__name__, hex(id(callback)))
        else:
            raise ValueError('register_callback should be called with a function or a callable object instance as callback argument.')

        # TODO: Get rid of this protected member access
        self._logger = logging.getLogger(plugin.logger.name + '.' + self._name)
        self._logger.config = self._engine.config

    def can_process(self, event):
        if not self._matchEvents:
            return True

        if '*' in self._matchEvents:
            eventType = '*'
        else:
            eventType = event['event_type']
            if eventType not in self._matchEvents:
                return False

        attributes = self._matchEvents[eventType]

        if attributes is None or '*' in attributes:
            return True

        if event['attribute_name'] and event['attribute_name'] in attributes:
            return True

        return False

    def process(self, event):
        """
        Process an event with the callback object supplied on initialization.

        If an error occurs, it will be logged appropriately and the callback
        will be deactivated.

        @param event: The Shotgun event to process.
        @type event: I{dict}
        """
        # set session_uuid for UI updates
        self._shotgun.set_session_uuid(event['session_uuid'])

        try:
            self._callback(self._shotgun, self._logger, event, self._args)
        except:
            # Get the local variables of the frame of our plugin
            tb = sys.exc_info()[2]
            stack = []
            while tb:
                stack.append(tb.tb_frame)
                tb = tb.tb_next

            msg = 'An error occured processing an event.\n\n%s\n\nLocal variables at outer most frame in plugin:\n\n%s'
            self._logger.critical(msg, traceback.format_exc(), pprint.pformat(stack[1].f_locals))
            self._active = False

        return self._active

    def is_active(self):
        """
        Check if this callback is active, i.e. if events should be passed to it
        for processing.

        @return: True if this callback should process events, False otherwise.
        @rtype: I{bool}
        """
        return self._active

    def __str__(self):
        """
        The name of the callback.

        @return: The name of the callback
        @rtype: I{str}
        """
        return self._name

