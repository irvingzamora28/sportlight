import logging
import logging.config
from logging import Logger, StreamHandler


class CustomLogger(Logger):
    def console(self, message, *args, **kwargs):
        # Create a console handler
        console_handler = StreamHandler()
        console_handler.setFormatter(
            logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
        )
        console_handler.setLevel(logging.INFO)

        # Add the console handler, log the message, and remove the handler
        self.addHandler(console_handler)
        self.info(message, *args, **kwargs)
        self.removeHandler(console_handler)


# Set the custom logger class
logging.setLoggerClass(CustomLogger)

# Configure logging
logging.config.dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
            }
        },
        "handlers": {
            "file": {
                "class": "logging.FileHandler",
                "filename": "app.log",
                "formatter": "default",
                "level": "DEBUG",
            }
        },
        "loggers": {
            # Specific logger configuration for selenium
            "selenium": {
                "level": "WARNING",
                "handlers": ["file"],
                "propagate": False,
            }
        },
        "root": {"level": "DEBUG", "handlers": ["file"]},
    }
)

# Create a logger instance
logger = logging.getLogger(__name__)
logger.info("Application started")
