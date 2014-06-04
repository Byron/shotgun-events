#-*-coding:utf-8-*-
"""
@package sgevents.tests.test_engine
@brief tess for sgevents.engine

@author Sebastian Thiel
@copyright [MIT License](http://www.opensource.org/licenses/mit-license.php)
"""
__all__ = []

import os
import socket

import bapp

from .base import (EventsTestCase,
                   with_plugin_application)

from bshotgun.tests import (ReadOnlyTestSQLProxyShotgunConnection,
                            ShotgunTestDatabase)
from butility.tests import with_rw_directory
from bapp.tests import with_application
from butility import (LazyMixin,
                      load_files,
                      Path)

from mock import Mock

# try * import
from sgevents import *


# ==============================================================================
## @name Utilities
# ------------------------------------------------------------------------------
## @{

class EventsReadOnlyTestSQLProxyShotgunConnection(ReadOnlyTestSQLProxyShotgunConnection, LazyMixin):
    """A connnection made to work for shotgun events"""
    __slots__ = ('next_event_id', 
                 'next_exception',
                 '_records')

    # magic values, dependent on actual dataase
    # NOTE: if broken, just use sql to find smallest id
    first_event_id = 11237

    def __init__(self, *args, **kwargs):
        super(EventsReadOnlyTestSQLProxyShotgunConnection, self).__init__(*args, **kwargs)
        self.next_event_id = self.first_event_id
        self.next_exception = None

        obj = Mock()
        obj.find = Mock(side_effect=self.next_event_list)
        self._proxy = obj

    def _set_cache_(self, name):
        if name == '_records':
            self._records = ShotgunTestDatabase().records('EventLogEntry')
        else:
            super(EventsReadOnlyTestSQLProxyShotgunConnection, self)._set_cache_(name)
        # end


    # make this this works
    set_session_uuid = Mock()

    @classmethod
    def is_ci_mode(cls):
        """@return True if we are running on travis"""
        return 'CI' in os.environ

    def has_database(self):
        """@return pretends we have one, in case we are in CI mode"""
        if self.is_ci_mode():
            return True
        return super(EventsReadOnlyTestSQLProxyShotgunConnection, self).has_database()

    # -------------------------
    ## @name Interface
    # @{

    def next_event(self, *args, **kwargs):
        """@return EventLogEntry"""
        if self.next_exception:
            exc = self.next_exception
            self.next_exception = None
            raise exc
        # end raise on demand

        if self.is_ci_mode():
            res = self._records[self.next_event_id - self.first_event_id]
        else:
            res = self.find_one('EventLogEntry', [('id', 'is', self.next_event_id)])
        # end 
        self.next_event_id += 1
        return res

    def next_event_list(self, *args, **kwargs):
        """As next_event(), but returns a list"""
        return [self.next_event()]

    ## -- End Interface -- @}
        

# end class EventsReadOnlyTestSQLProxyShotgunConnection

## -- End Utilities -- @}



class EngineTestCase(EventsTestCase):
    __slots__ = ()

    @with_plugin_application
    @with_rw_directory
    def test_base(self, rw_dir):
        sg = EventsReadOnlyTestSQLProxyShotgunConnection()

        # make sure the first attempt to fetch fails (branch without journal file)
        sg.next_exception = socket.error
        engine = EventEngine(sg)

        assert engine._plugin_context is not None, "should have found at least one plugin"

        engine._process_events()

        test_plugin = engine._iter_plugins().next()
        test_plugin.make_assertion()

        engine._load_event_id_data()
        engine._load_event_id_data(), "duplicate calls are fine"

        sg.next_exception = socket.error
        engine._process_events()
        sg.next_exception = EnvironmentError
        self.failUnlessRaises(EnvironmentError, engine._process_events)

        # try threaded mode
        engine.start()
        engine.stop_and_join()

        # trash pickle file and see how it recovers
        journal = engine._journal_path()
        journal.write_bytes("hello")
        engine._load_event_id_data()

        test_plugin.next_exception = ValueError
        engine._process_events()
        test_plugin.make_assertion()

        # Test event skipping
        sg.next_event_id += 10
        engine._process_events()
        engine._process_events()
        sg.next_event_id -= 8
        engine._process_events()
        sg.next_event_id -= 8
        engine._process_events()

        test_plugin.event_filters = {} # this means all events
        sg.next_event_id += 16
        engine._process_events()
        test_plugin.make_assertion()

        # selected events
        test_plugin.event_filters = {'Shotgun_Shot_Change' : ['sg_cut_in']}
        engine._process_events()

    @with_application(from_file=__file__)
    @with_rw_directory
    def test_plugins(self, rw_dir):
        """load all known plugins and dispatch some events"""
        def raiser(py_file, mod_name):
            raise AssertionError("loading of plugin '%s' failed")
        # end 

        prev_dir = os.getcwd()
        bapp.main().context().push('example plugins')

        plugin_path = Path(__file__).dirname().dirname() / 'plugins'
        examples_path = plugin_path.dirname().dirname().dirname() / 'examples'

        for path in (plugin_path, examples_path):
            assert path.isdir()
            assert load_files(path, on_error=raiser)
        # end for each path to load plugins from

        try:
            os.chdir(rw_dir)
            sg = EventsReadOnlyTestSQLProxyShotgunConnection()
            engine = EventEngine(sg)

            for eid in range(1, 1000, 100):
                sg.next_event_id = sg.first_event_id + eid
                engine._process_events()
            # end 
        finally:
            os.chdir(prev_dir)
        # end reset cwd

# end class EngineTestCase
