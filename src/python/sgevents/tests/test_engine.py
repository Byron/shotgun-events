#-*-coding:utf-8-*-
"""
@package sgevents.tests.test_engine
@brief tess for sgevents.engine

@author Sebastian Thiel
@copyright [MIT License](http://www.opensource.org/licenses/mit-license.php)
"""
__all__ = []

from .base import (EventsTestCaseBase,
                   with_plugin_application)

from bshotgun.tests import ReadOnlyTestSQLProxyShotgunConnection
from butility.tests import with_rw_directory

from mock import Mock

# try * import
from sgevents import *


# ==============================================================================
## @name Utilities
# ------------------------------------------------------------------------------
## @{

class EventsReadOnlyTestSQLProxyShotgunConnection(ReadOnlyTestSQLProxyShotgunConnection):
    """A connnection made to work for shotgun events"""
    __slots__ = ('_current_event_id')

    # magic values, dependent on actual dataase
    # NOTE: if broken, just use sql to find smallest id
    first_event_id = 11237

    def __init__(self, *args, **kwargs):
        super(EventsReadOnlyTestSQLProxyShotgunConnection, self).__init__(*args, **kwargs)
        self._current_event_id = self.first_event_id

        obj = Mock()
        obj.find = Mock(side_effect=self.next_event_list)
        self._proxy = obj


    set_session_uuid = Mock()

    # -------------------------
    ## @name Interface
    # @{

    def next_event(self, *args, **kwargs):
        """@return EventLogEntry"""
        res = self.find_one('EventLogEntry', [('id', 'is', self._current_event_id)])
        self._current_event_id += 1
        return res

    def next_event_list(self, *args, **kwargs):
        """As next_event(), but returns a list"""
        return [self.next_event()]

    ## -- End Interface -- @}
        

# end class EventsReadOnlyTestSQLProxyShotgunConnection

## -- End Utilities -- @}



class EngineTestCase(EventsTestCaseBase):
    __slots__ = ()

    @with_plugin_application
    @with_rw_directory
    def test_base(self, rw_dir):
        sg = EventsReadOnlyTestSQLProxyShotgunConnection()
        engine = EventEngine(sg)

        assert engine._plugin_context is not None, "should have found at least one plugin"

        engine._process_events()

        test_plugin = engine._iter_plugins().next()
        test_plugin.make_assertion()



# end class EngineTestCase
