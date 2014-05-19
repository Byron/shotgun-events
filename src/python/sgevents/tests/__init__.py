#-*-coding:utf-8-*-
"""
@package sgevents.tests
@brief test suite for sgevents

@author Sebastian Thiel
@copyright [MIT License](http://www.opensource.org/licenses/mit-license.php)
"""
__all__ = []

import os
import tempfile

def _initialize():
    """assure our test suite has a suitable environment"""
    os.environ['TMP'] = tempfile.gettempdir()


_initialize()


