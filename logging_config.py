import logging
import sys

LOGGING_CONFIG = {
    "version": 1,
    "handlers": {
        "default": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "myFormatter",
            "filename": "crawl_log.log",
            "encoding": "utf-8",
            "maxBytes": 2097152,
            "backupCount": 3
        }
    },
    "loggers": {
        "": {
            "handlers": ["default"],
            "level": "INFO",
        }
    },
    "formatters": {
        "myFormatter": {
            "format": "%(asctime)s,%(msecs)03d %(levelname)s: %(message)s - %(threadName)s",
            "datefmt": "%d-%m-%y %H:%M:%S"
        }
    }
}
