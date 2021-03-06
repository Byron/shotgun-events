#-*-coding:utf-8-*-
"""
@package sgevents.tests.base
@brief tools for testing

@author Sebastian Thiel
@copyright [GNU Lesser General Public License](https://www.gnu.org/licenses/lgpl.html)
"""
__all__ = ['with_plugin_application', 'EventsTestCase']

from functools import wraps

from butility import Path
from bprocess.tests import PluginLoadingProcessAwareApplication
from bapp.tests import with_application
from bapp.tests import preserve_application
from bshotgun.tests import ShotgunTestCase


# ==============================================================================
## @name Decorators
# ------------------------------------------------------------------------------
## @{

def with_plugin_application(fun):
    """Load plugins, and don't breakout of the test sandbox"""
    return with_application(from_file=__file__, application_type=PluginLoadingProcessAwareApplication, 
                            package_name='shotgun-events')(fun)

## -- End Decorators -- @}



# ==============================================================================
## @name Types
# ------------------------------------------------------------------------------
## @{

## -- End Types -- @}


class EventsTestCase(ShotgunTestCase):
    """Supports reasonable fixture paths"""
    __slots__ = ()


# end class EventsTestCase
