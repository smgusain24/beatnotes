import logging
from logging.config import dictConfig
import os

# Ensure the logs directory exists
os.makedirs("logs", exist_ok=True)

dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s %(filename)s %(funcName)s() > %(message)s",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "default",
            },
            "beatnotes_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "logs/beatnotes.log",
                "maxBytes": 1000000,
                "backupCount": 10,
                "formatter": "default",
                "encoding": "utf-8"
            }
        },
        "loggers": {
            "beatnotes": {
                "level": "INFO",
                "handlers": ["console", "beatnotes_file"],
            },
        },
    }
)

logger = logging.getLogger("beatnotes")
