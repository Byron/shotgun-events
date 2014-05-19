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
    __slots__ = ()

    event_filters = dict(Shotgun_Shot_Change = list(),
                         Shotgun_Shot_New = list(),
                         Shotgun_Shot_Retirement = list(),
                         Shotgun_Shot_Revival = list())

    def handle_event(self, shotgun, log, event):
        assert shotgun and log
        assert isinstance(event, DictObject)

# end class TestEventEnginePlugin
