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
from datetime import (datetime,
                      timedelta)

from butility import abstractmethod


class EventEnginePlugin(object):
    """Implements the command pattern to allow the EventEngine to process events based on pre-filtered events
    """

    __slots__ = ('_log',
                 '_sg',
                 '_active',
                 '_last_event_id',
                 '_backlog'
                 )


    # -------------------------
    ## @name Subclass Interface
    # @{

    ## To be set in subclass, matching this format
    # dict('APPLICATION_ENTITYTYPE_ACTION', attributes|None), 
    # see https://github.com/shotgunsoftware/python-api/wiki/Event-Types for more information
    event_filters = None
    
    ## -- End Subclass Interface -- @}


    def __init__(self, sg, log):
        """
        @param sg a shotgun connection instance
        @param log a logger instance to use
        """
        self._active = True
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
        assert self.is_active(), "shold be active when engine calls us"
        if self._can_process_event(event):
            self._log.debug('Dispatching event %d to callback %s.', event['id'], str(self))

            # set session_uuid for UI updates
            self._sg.set_session_uuid(event['session_uuid'])
            try:
                self.handle_event(self._sg, self._log, event)
            except Exception:
                msg = 'An error occured processing an event in callback %s'
                self._log.critical(msg, str(self), exc_info=True)
                self._active = False
            # end log errors
        else:
            self._log.debug("Ignored event '%s' as it didn't match our filters", event.event_type)
        # end

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

    def _event_filters(self):
        """@return our configured event filters
        @note subclasses can implement this to support variable filters"""
        assert self.event_filters is not None, 'event_filters class member must be set'
        return self.event_filters

    def _can_process_event(self, event):
        """@return True if the given event matches our event_fitlers"""
        event_filters = self._event_filters()
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

    ## -- End Callback Logic -- @}


    # ------------------------------
    ## @name Event Engine Interface
    # @{

    def set_event_id(self, id):
        """Sets our last known event ID to the given one, usually right after we have been loaded"""
        self._last_event_id = id
    
    def set_state(self, state):
        """Sets the previously persisted state, as returned by state()"""
        if isinstance(state, tuple):
            self._last_event_id, self._backlog = state
        else:
            raise ValueError('Unknown state type: %s.' % type(state))
        # end handle state type

    def state(self):
        """@return your internal state as defined by you entirely.
        Must remain compatible to set_state()"""
        return (self._last_event_id, self._backlog)

    def state_key(self):
        """@return a unique key identifying the state we return, for storage in a dict.
        It must most uniquely identify our state, as it should remain associated with this plugin type"""
        return str(self)

    def next_unprocessed_event_id(self):
        if self._last_event_id:
            next_id = self._last_event_id + 1
        else:
            next_id = None
        # end 

        now = datetime.now()
        for k, v in self._backlog.items():
            if v < now:
                self._log.warning('Timeout elapsed on backlog event id %d.', k)
                del(self._backlog[k])
            elif next_id is None or k < next_id:
                next_id = k
            # end 
        # end for each entry in backlog

        return next_id

    def is_active(self):
        """
        Is the current plugin active. Only active plugins will be run

        @return: True if this plugin's callbacks should be run, False otherwise.
        @rtype: I{bool}
        """
        return self._active

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


    # -------------------------
    ## @name Subclass Interface
    # @{
    
    @abstractmethod
    def handle_event(self, shotgun, log, event):
        """Perform an operation on the given event
        @param shotgun a ShotgunConnection for querying additional data
        @param event a DictObject of the event entity representing the event in question
        """
        raise NotImplementedError("to be implemented in subclass")

    ## -- End Subclass Interface -- @}

# end class EventEnginePlugin

