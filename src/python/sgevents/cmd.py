#-*-coding:utf-8-*-
"""
@package sgevents.cmd
@brief implementation of a commandline interface for the EventEngine

@author Sebastian Thiel
@copyright [MIT License](http://www.opensource.org/licenses/mit-license.php)
"""
__all__ = []

from bcmd import DaemonCommandMixin

import bapp
from butility import Version
from be import BeSubCommand


class ShotgunEventsBeSubCommand(BeSubCommand, bapp.plugin_type()):
    """A shotgun events plugin"""
    __slots__ = ()

    name = 'shotgun-events'
    version = Version('0.1.0')
    description = "polls shotgun events and have plugins react to them"

    def setup_argparser(self, parser):
        """Setup your flags using argparse"""
        super(ShotgunEventsBeSubCommand, self).setup_argparser(parser)
        # parser.add_argument('-v', '--verbose',
        #                     action='store_true', 
        #                     default=False, 
        #                     dest='verbosity',
        #                     help='enable verbose mode')
        return self

    def execute(self, args, remaining_args):
        raise NotImplementedError('tbd')
        return self.SUCCESS

