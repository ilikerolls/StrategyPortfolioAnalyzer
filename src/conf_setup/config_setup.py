import logging
import sys
from logging.handlers import RotatingFileHandler

from src.conf_setup import APP_NAME, LOG_LEVEL, LOG_FILE, LOG_FILE_ERR, LOG_BACKUPS

logger = logging.getLogger(APP_NAME)


def load_logger():
    """ Load logger to be used in other classes """
    log_handlers = [logging.StreamHandler(sys.stdout)]
    # Main Logfile handler
    main_handler = RotatingFileHandler(LOG_FILE, maxBytes=5242880, backupCount=LOG_BACKUPS,
                                       encoding="UTF-8")
    main_handler.setLevel(level=LOG_LEVEL.upper())

    # Error logfile handler
    error_handler = RotatingFileHandler(LOG_FILE_ERR, maxBytes=5242880, backupCount=LOG_BACKUPS,
                                        encoding="UTF-8")
    error_handler.setLevel(level=logging.WARNING)
    log_handlers.extend([main_handler, error_handler])

    formatter = logging.Formatter(
        fmt='%(asctime)s | %(filename)s:%(funcName)s:%(lineno)s | %(levelname)s |  %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    for h in log_handlers:
        h.setFormatter(formatter)
        logger.addHandler(h)
    # Set Log Level
    logger.setLevel(LOG_LEVEL.upper())

    logger.debug("***** Logger Loaded *****")

    return logger


# Load our logging settings
load_logger()
