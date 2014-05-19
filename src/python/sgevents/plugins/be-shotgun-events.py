#-*-coding:utf-8-*-
"""
@package sgevents.plugins.be-shotgun-events

@author Sebastian Thiel
@copyright [GNU Lesser General Public License](https://www.gnu.org/licenses/lgpl.html)
"""
__all__ = []

import bapp
from be import BeSubCommand

from sgevents import ShotgunEventEngineCommand


class ShotgunEventsDaemonBeSubCommand(ShotgunEventEngineCommand, BeSubCommand, bapp.plugin_type()):
    """A daemon for integration with the be UTC"""
    __slots__ = ()

# end class ShotgunEventsDaemonBeSubCommand

