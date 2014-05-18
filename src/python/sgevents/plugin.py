#-*-coding:utf-8-*-
"""
@package sgevents.plugin
@brief Keeps base for EventEngine plugins

@author Sebastian Thiel
@copyright [MIT License](http://www.opensource.org/licenses/mit-license.php)
"""
__all__ = ['EventEnginePlugin']

import os
import logging
from collections import namedtuple
from datetime import (datetime,
                      timedelta)


class EventEnginePlugin(object):
    """Implements the command pattern to allow the EventEngine to process events based on pre-filtered events
    """

    __slots__ = ('log',
                 '_sg',
                 '_active',
                 '_last_event_id',
                 '_callbacks'          # list of Callback tuples [callback, event_filters]
                 )

    ## We keep this type simple and do all the processing in the plugin, allowing subtypes to override 
    # behaviour more easily
    CallbackType = namedtuple('Callback', ('callable', 'event_filters'))


    def __init__(self, sg,log):
        """
        @param sg a shotgun connection instance
        @param log a logger instance to use
        """
        self._active = True
        self._callbacks = []
        self._last_event_id = None
        self._backlog = {}

        # Setup the plugin's logger
        self._sg = sg
        self._log = log

    def __str__(self):
        """Provide the name of the plugin when it is cast as string"""
        return self.plugin_name()

    def _process(self, event):
        """run through all callbacks and process them.
        Disable ourselves on failure
        @return True on success"""
        for callback in self._callbacks:
            if self._can_process_callback(callback, event):
                self._log.debug('Dispatching event %d to callback %s.', event['id'], self._callback_name(callback))
                self._active |= self._process_callback(callback, event)
                # even if one fails, we keep going with the remainder of the plugin, do as much as we can
            else:
                msg = 'Skipping inactive callback %s in plugin.'
                self._log.debug(msg, str(callback))
        # end for each callback

        return self._active

    def _update_last_event_id(self, event_id):
        if self._last_event_id is not None and event_id > self._last_event_id + 1:
            expiration = datetime.now() + timedelta(minutes=5)
            for skipped_id in range(self._last_event_id + 1, event_id):
                self._log.debug('Adding event id %d to backlog.', skipped_id)
                self._backlog[skipped_id] = expiration
            # for each skipped id
        # end if there is an event gap / we missed events
        self._last_event_id = event_id


    # -------------------------
    ## @name Callback Logic
    # @{

    def _can_process_callback(self, callback, event_filters, event):
        if not event_filters:
            return True

        if '*' in event_filters:
            event_type = '*'
        else:
            event_type = event['event_type']
            if event_type not in event_filters:
                return False
            # end
        # end 

        attributes = event_filters[event_type]
        if not attributes or '*' in attributes:
            return True

        return event['attribute_name'] and event['attribute_name'] in attributes

    def _callback_name(self, callback):
        """@return a nice name for the given callback"""
        if hasattr(callback, '__name__'):
            return callback.__name__
        elif hasattr(callback, '__class__') and hasattr(callback, '__call__'):
            return '%s_%s' % (callback.__class__.__name__, hex(id(callback)))
        return str(callback)

    def _process_callback(self, callback, event):
        """
        Process an event with the callback.

        If an error occurs, it will be logged appropriately.

        @return True if the callback succeeded
        """
        # set session_uuid for UI updates
        self._sg.set_session_uuid(event['session_uuid'])
        try:
            callback.callable(self._sg, self._log, event)
            return True
        except Exception:
            msg = 'An error occured processing an event in callback %s'
            self._log.critical(msg, self._callback_name(callback), exc_info=True)
            return False
        # end log errors

    
    ## -- End Callback Logic -- @}


    # ------------------------------
    ## @name Event Engine Interface
    # @{
    
    def set_state(self, state):
        if isinstance(state, tuple):
            self._last_event_id, self._backlog = state
        else:
            raise ValueError('Unknown state type: %s.' % type(state))

    def state(self):
        return (self._last_event_id, self._backlog)

    def next_unprocessed_event_id(self):
        if self._last_event_id:
            nextId = self._last_event_id + 1
        else:
            nextId = None
        # end 

        now = datetime.now()
        for k, v in self._backlog.items():
            if v < now:
                self._log.warning('Timeout elapsed on backlog event id %d.', k)
                del(self._backlog[k])
            elif nextId is None or k < nextId:
                nextId = k
            # end 
        # end for each entry in backlog

        return nextId

    def is_active(self):
        """
        Is the current plugin active. Should it's callbacks be run?

        @return: True if this plugin's callbacks should be run, False otherwise.
        @rtype: I{bool}
        """
        return self._active

    def register_callback(self, callback, match_events=None):
        """Register a callback in the plugin."""
        self._callbacks.append(self.CallbackType(callback, match_events))
        return self

    def process(self, event):
        if event['id'] in self._backlog:
            if self._process(event):
                del(self._backlog[event['id']])
                self._update_last_event_id(event['id'])
        elif self._last_event_id is not None and event['id'] <= self._last_event_id:
            msg = 'Event %d is too old. Last event processed was (%d).'
            self._log.debug(msg, event['id'], self._last_event_id)
        else:
            if self._process(event):
                self._update_last_event_id(event['id'])
        # end handle event id

        return self._active


    ## -- End Interface -- @}

# end class EventEnginePlugin

