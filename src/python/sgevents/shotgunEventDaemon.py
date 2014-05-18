#!/usr/bin/python
#
# Init file for Shotgun event daemon
#
# chkconfig: 345 99 00
# description: Shotgun event daemon
#
### BEGIN INIT INFO
# Provides: shotgunEvent
# Required-Start: $network
# Should-Start: $remote_fs
# Required-Stop: $network
# Should-Stop: $remote_fs
# Default-Start: 2 3 4 5
# Short-Description: Shotgun event daemon
# Description: Shotgun event daemon
### END INIT INFO

"""
For an overview of shotgunEvents, please see raw documentation in the docs
folder or an html compiled version at:

http://shotgunsoftware.github.com/shotgunEvents
"""

__version__ = '0.9'
__version_info__ = (0, 9)

import ConfigParser
import datetime
import imp
import logging
import logging.handlers
import os
import pprint
import socket
import sys
import time
import types
import traceback
import weakref





class Config(ConfigParser.ConfigParser):
    def __init__(self, path):
        ConfigParser.ConfigParser.__init__(self)
        self.read(path)

    def getShotgunURL(self):
        return self.get('shotgun', 'server')

    def getEngineScriptName(self):
        return self.get('shotgun', 'name')

    def getEngineScriptKey(self):
        return self.get('shotgun', 'key')

    def getEventIdFile(self):
        return self.get('daemon', 'eventIdFile')

    def getEnginePIDFile(self):
        return self.get('daemon', 'pidFile')

    def getPluginPaths(self):
        return [s.strip() for s in self.get('plugins', 'paths').split(',')]

    def getSMTPServer(self):
        return self.get('emails', 'server')

    def getFromAddr(self):
        return self.get('emails', 'from')

    def getToAddrs(self):
        return [s.strip() for s in self.get('emails', 'to').split(',')]

    def getEmailSubject(self):
        return self.get('emails', 'subject')

    def getEmailUsername(self):
        if self.has_option('emails', 'username'):
            return self.get('emails', 'username')
        return None

    def getEmailPassword(self):
        if self.has_option('emails', 'password'):
            return self.get('emails', 'password')
        return None

    def getLogMode(self):
        return self.getint('daemon', 'logMode')

    def getLogLevel(self):
        return self.getint('daemon', 'logging')

    def getLogFile(self, filename=None):
        if filename is None:
            if self.has_option('daemon', 'logFile'):
                filename = self.get('daemon', 'logFile')
            else:
                raise ConfigError('The config file has no logFile option.')

        if self.has_option('daemon', 'logPath'):
            path = self.get('daemon', 'logPath')

            if not os.path.exists(path):
                os.makedirs(path)
            elif not os.path.isdir(path):
                raise ConfigError('The logPath value in the config should point to a directory.')

            path = os.path.join(path, filename)

        else:
            path = filename

        return path







