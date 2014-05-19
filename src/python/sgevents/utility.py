#-*-coding:utf-8-*-
"""
@package sgevents.utility
@brief Various utilities that don't have considerable dependnecies

@author Sebastian Thiel
@copyright [MIT License](http://www.opensource.org/licenses/mit-license.php)
"""
__all__ = ['CustomSMTPHandler', 'set_file_path_on_logger', 'set_emails_on_logger', 'EventEngineError']

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

def set_emails_on_logger(logger, settings, emails):
    """Configures a logger to either receive emails or not. In any case, existing handlers will be removed
    @param logger 
    @param settings obtained from EventEngine.settings_value().logging.email
    @param emails either True, False, or a list of e-mail to addresses to send emails to.
    If False, existing smtp handlers will be removed. If True, e-email to addresses will be reset to the 
    ones configured for the engine.
    Otherwise it is expected to be a list or tuple of e-mail to-addresses."""
    # Configure the logger for email output
    remove_handlers_from_logger(logger, logging.handlers.SMTPHandler)

    if emails is False:
        return

    username = settings.username or None
    password = settings.password or None

    if emails is True:
        to_addrs = settings.to
    elif isinstance(emails, (list, tuple)):
        to_addrs = emails
    else:
        msg = 'Argument emails should be True to use the default addresses, False to not send any emails or a list of recipient addresses. Got %s.'
        raise ValueError(msg % type(emails))
    # end handle emails arg

    CustomSMTPHandler.add_to_logger(logger, settings['host'], settings['from'], to_addrs, settings.subject,
                                    username, password)

def remove_handlers_from_logger(logger, handlerTypes=None):
    """
    Remove all handlers or handlers of a specified type from a logger.

    @param logger The logger who's handlers should be processed.
    
    @param handlerTypes A type of handler or list/tuple of types of handlers
        that should be removed from the logger. If I{None}, all handlers are
        removed.
    
        I{list}/I{tuple} of logging.Handler subclasses.
    """
    for handler in logger.handlers:
        if handlerTypes is None or isinstance(handler, handlerTypes):
            logger.removeHandler(handler)
    # end for each handler

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
    def add_to_logger(cls, logger, smtpServer, fromAddr, toAddrs, emailSubject, username=None, password=None):
        """
        Configure a logger with a handler that sends emails to specified
        addresses.

        The format of the email is defined by L{LogFactory.EMAIL_FORMAT_STRING}.

        @note: Any SMTPHandler already connected to the logger will be removed.

        @param logger The logger to configure
        
        @param toAddrs The addresses to send the email to.
        
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
