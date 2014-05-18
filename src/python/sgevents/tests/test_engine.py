#-*-coding:utf-8-*-
"""
@package sgevents.tests.test_engine
@brief tess for sgevents.engine

@author Sebastian Thiel
@copyright [GNU Lesser General Public License](https://www.gnu.org/licenses/lgpl.html)
"""
__all__ = []

from .base import EventsTestCaseBase

# try * import
from sgevents import *

class EngineTestCase(EventsTestCaseBase):
    __slots__ = ()


    def test_base(self):
        self.fail('todo')

# end class EngineTestCase
