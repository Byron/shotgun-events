#-*-coding:utf-8-*-
"""
@package sgevents.tests.plugins
@brief contains implementations of test plugins

@author Sebastian Thiel
@copyright [MIT License](http://www.opensource.org/licenses/mit-license.php)
"""
__all__ = []

import bapp
from sgevents import (EventEnginePlugin,
                      with_global_event_application)
from butility import DictObject


class TestEventEnginePlugin(EventEnginePlugin, bapp.plugin_type()):
    """just verify it's being called"""
    __slots__ = ('_called', 'next_exception', '_application_called')

    # catch all
    event_filters = {'*' : list()}

    def __init__(self, *args, **kwargs):
        super(TestEventEnginePlugin, self).__init__(*args, **kwargs)
        self.next_exception = None
        

    @with_global_event_application
    def handle_event(self, shotgun, log, event):
        assert shotgun and log
        assert isinstance(event, DictObject)

        if self.next_exception:
            exc = self.next_exception
            self.next_exception = None
            raise exc
        # end 

        self._called = True

    def event_application(self, shotgun, log, event):
        self._application_called = True
        return super(TestEventEnginePlugin, self).event_application(shotgun, log, event)

    # -------------------------
    ## @name Test Interface
    # @{

    def make_assertion(self):
        """Verify our state, and reset ourselves"""
        assert self._called
        assert self._application_called

        self._application_called = self._called = False
        self._active = True

    ## -- End Test Interface -- @}

# end class TestEventEnginePlugin
