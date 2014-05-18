#-*-coding:utf-8-*-
"""
@package sgevents.tests.test_engine
@brief tess for sgevents.engine

@author Sebastian Thiel
@copyright [MIT License](http://www.opensource.org/licenses/mit-license.php)
"""
__all__ = []

from .base import EventsTestCaseBase

from bshotgun.tests import ReadOnlyTestSQLProxyShotgunConnection

# try * import
from sgevents import *


# ==============================================================================
## @name Utilities
# ------------------------------------------------------------------------------
## @{

class EventsReadOnlyTestSQLProxyShotgunConnection(ReadOnlyTestSQLProxyShotgunConnection):
    """A connnection made to work for shotgun events"""
    __slots__ = ()

    # magic values, dependent on actual dataase
    # NOTE: if broken, just use sql to find smallest id
    first_event_id = 11237

# end class EventsReadOnlyTestSQLProxyShotgunConnection

## -- End Utilities -- @}



class EngineTestCase(EventsTestCaseBase):
    __slots__ = ()


    def test_base(self):
        sg = EventsReadOnlyTestSQLProxyShotgunConnection()
        engine = EventEngine(sg)

# end class EngineTestCase
