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
    __slots__ = ('_called')

    # catch all
    event_filters = {'*' : list()}

    def handle_event(self, shotgun, log, event):
        assert shotgun and log
        assert isinstance(event, DictObject)

        self._called = True

    # -------------------------
    ## @name Test Interface
    # @{

    def make_assertion(self):
        """Verify our state"""
        assert self._called

    ## -- End Test Interface -- @}

# end class TestEventEnginePlugin
