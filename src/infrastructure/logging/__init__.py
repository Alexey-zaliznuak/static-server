import os
import logging

from .config import LoggingConfig as Config
from .day_time_handler import DateTimeFileHandler


def init_logging_settings():
    full_logs_dir = Config.BASE_LOG_DIRECTORY + "/full/"

    os.makedirs(full_logs_dir, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(full_logs_dir + "app.log"),
            logging.StreamHandler(),
            DateTimeFileHandler(Config.BASE_LOG_DIRECTORY),
        ]
    )

__all__ = [
    "init_logging_settings"
]
