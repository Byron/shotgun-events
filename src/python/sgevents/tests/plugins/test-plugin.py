#-*-coding:utf-8-*-
"""
@package sgevents.tests.plugins
@brief contains implementations of test plugins

@author Sebastian Thiel
@copyright [MIT License](http://www.opensource.org/licenses/mit-license.php)
"""
__all__ = []

import bapp
from sgevents import EventEnginePlugin
from butility import DictObject


class TestEventEnginePlugin(EventEnginePlugin, bapp.plugin_type()):
    """just verify it's being called"""
    __slots__ = ('_called', 'next_exception')

    # catch all
    event_filters = {'*' : list()}

    def __init__(self, *args, **kwargs):
        super(TestEventEnginePlugin, self).__init__(*args, **kwargs)
        self.next_exception = None
        

    def handle_event(self, shotgun, log, event):
        assert shotgun and log
        assert isinstance(event, DictObject)

        if self.next_exception:
            exc = self.next_exception
            self.next_exception = None
            raise exc
        # end 

        self._called = True

    # -------------------------
    ## @name Test Interface
    # @{

    def make_assertion(self):
        """Verify our state, and reset ourselves"""
        assert self._called

        self._called = False
        self._active = True

    ## -- End Test Interface -- @}

# end class TestEventEnginePlugin
