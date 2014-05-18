#-*-coding:utf-8-*-
"""
@package sgevents.utility
@brief Various utilities that don't have considerable dependnecies

@author Sebastian Thiel
@copyright [MIT License](http://www.opensource.org/licenses/mit-license.php)
"""
__all__ = ['CustomSMTPHandler', 'set_file_path_on_logger', 'EventEngineError']

import logging

from butility import (Path,
                      Error)
from bkvstore import (FrequencyStringAsSeconds,
                      KeyValueStoreSchema,
                      StringList)



# ==============================================================================
## @name Schemas
# ------------------------------------------------------------------------------
## @{

engine_schema = KeyValueStoreSchema('shotgun-events-engine', {'connection' : {
                                                                    'retries' : 5,
                                                                    'retry-every': FrequencyStringAsSeconds('60s')},
                                                              'poll-every' : FrequencyStringAsSeconds('60s'),
                                                              'socket-timeout' : FrequencyStringAsSeconds('60s'),
                                                              'event-journal-file' : Path,
                                                              'logging' : {
                                                                        'one-file-per-plugin' : True,
                                                                        'plugin-log-tree' : Path,
                                                                        'path' : Path,
                                                                        'email' : {
                                                                            'host' : str,
                                                                            'from' : str,
                                                                            'subject' : str,
                                                                            'to' : StringList,
                                                                            'username' : str,
                                                                            'password' : str
                                                                        } # end emails
                                                                    }# end logging
                                                             })

## -- End Schemas -- @}



# ==============================================================================
## @name Functions
# ------------------------------------------------------------------------------
## @{

def set_file_path_on_logger(logger, path):
    # Remove any previous handler.
    remove_handlers_from_logger(logger, logging.handlers.TimedRotatingFileHandler)

    # Add the file handler
    handler = logging.handlers.TimedRotatingFileHandler(path, 'midnight', backupCount=10)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)


## -- End Functions -- @}




# ==============================================================================
## @name Types
# ------------------------------------------------------------------------------
## @{


class EventEngineError(Error):
    """Standard event engine error"""
    __slots__ = ()

# end class EventEngineError


class CustomSMTPHandler(logging.handlers.SMTPHandler):
    """
    A custom SMTPHandler subclass that will adapt it's subject depending on the
    error severity.
    """

    EMAIL_FORMAT_STRING = """Time: %(asctime)s
Logger: %(name)s
Path: %(pathname)s
Function: %(funcName)s
Line: %(lineno)d

%(message)s"""


    LEVEL_SUBJECTS = {
        logging.ERROR: 'ERROR - Shotgun event daemon.',
        logging.CRITICAL: 'CRITICAL - Shotgun event daemon.',
    }

    def subject(self, record):
        subject = logging.handlers.SMTPHandler.subject(self, record)
        if record.levelno in self.LEVEL_SUBJECTS:
            return subject + ' ' + self.LEVEL_SUBJECTS[record.levelno]
        return subject


    # -------------------------
    ## @name Subclass Interface
    # For potential overrides in subclasses
    # @{


    @classmethod
    def remove_handlers_from_logger(cls, logger, handlerTypes=None):
        """
        Remove all handlers or handlers of a specified type from a logger.

        @param logger: The logger who's handlers should be processed.
        @type logger: A logging.Logger object
        @param handlerTypes: A type of handler or list/tuple of types of handlers
            that should be removed from the logger. If I{None}, all handlers are
            removed.
        @type handlerTypes: L{None}, a logging.Handler subclass or
            I{list}/I{tuple} of logging.Handler subclasses.
        """
        for handler in logger.handlers:
            if handlerTypes is None or isinstance(handler, handlerTypes):
                logger.removeHandler(handler)


    @classmethod
    def add_to_logger(cls, logger, smtpServer, fromAddr, toAddrs, emailSubject, username=None, password=None):
        """
        Configure a logger with a handler that sends emails to specified
        addresses.

        The format of the email is defined by L{LogFactory.EMAIL_FORMAT_STRING}.

        @note: Any SMTPHandler already connected to the logger will be removed.

        @param logger: The logger to configure
        @type logger: A logging.Logger instance
        @param toAddrs: The addresses to send the email to.
        @type toAddrs: A list of email addresses that will be passed on to the
            SMTPHandler.
        """
        if not (smtpServer and fromAddr and toAddrs and emailSubject):
            return

        if username and password:
            mailHandler = cls(smtpServer, fromAddr, toAddrs, emailSubject, (username, password))
        else:
            mailHandler = cls(smtpServer, fromAddr, toAddrs, emailSubject)
        # end use credentials

        mailHandler.setLevel(logging.ERROR)
        mailFormatter = logging.Formatter(cls.EMAIL_FORMAT_STRING)
        mailHandler.setFormatter(mailFormatter)

        logger.addHandler(mailHandler)

    
    ## -- End Subclass Interface -- @}


## -- End Types -- @}
