import logging
import os
from enum import Enum
from logging.config import dictConfig
from typing import Union

from .constants import PACKAGE_NAME


class LogLevel(str, Enum):
    """LogLevel in case-insensitive."""

    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"
    NOTSET = "NOTSET"

    @classmethod
    def _missing_(cls, value):
        _v = value.upper()
        try:
            values = list(cls.__members__.values())
            idx = list(cls.__members__.values()).index(_v)
            return values[idx]
        except ValueError:
            return cls.DEBUG


LOG_LEVEL = LogLevel(os.getenv("LOG_LEVEL", "")).value
LOG_FMT = "[%(asctime)s.%(msecs)03d][%(levelname)s][%(module)s][%(funcName)s,%(lineno)s]: %(message)s"
CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"standard": {"format": LOG_FMT, "datefmt": "%Y-%m-%dT%H:%M:%S"}},
    "handlers": {
        "stream": {
            "level": LOG_LEVEL,
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",  # Default is stderr
        },
    },
    "loggers": {
        # Specific logger for seasalt
        PACKAGE_NAME: {
            "handlers": ["stream"],
            "level": LOG_LEVEL,
            "propagate": False,
        }
    },
}

dictConfig(CONFIG)


def get_logger(handlers: Union[list, None] = None):
    """Get logger and support additional custom handers in different classes."""
    logger = logging.getLogger(name=PACKAGE_NAME)
    hdlr_names = [h.__class__.__name__ for h in logger.handlers]
    if handlers:
        hdlr_names = [h.__class__.__name__ for h in logger.handlers]
        for hdlr in handlers:
            if hdlr.__class__.__name__ in hdlr_names:
                continue

            logger.handlers.append(hdlr)

    return logger
