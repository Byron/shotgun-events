#-*-coding:utf-8-*-
"""
@package sgevents.cmd
@brief implementation of a commandline interface for the EventEngine

@author Sebastian Thiel
@copyright [MIT License](http://www.opensource.org/licenses/mit-license.php)
"""
__all__ = []

from bcmd import DaemonCommandMixin

from butility import Version
from bcmd import Command

from .engine import EventEngine


class ShotgunEventEngineCommand(DaemonCommandMixin, Command):
    """Makes the events engine available from the commandline"""
    __slots__ = ()

    name = 'shotgun-events'
    version = Version('0.1.0')
    description = "polls shotgun events and have plugins react to them"

    ThreadType = EventEngine

# end class ShotgunEventEngineCommand

if __name__ == '__main__':
    ShotgunEventEngineCommand.main()
