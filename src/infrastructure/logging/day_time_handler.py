import logging
import os
from datetime import datetime


class DateTimeFileHandler(logging.Handler):
    "Handler for log in year/month/day/hour/minute.txt file"

    def __init__(self, base_dir: str | None = None):
        super().__init__()
        self.base_dir = base_dir or os.getcwd()

    def emit(self, record: logging.LogRecord):
        try:
            log_file_path = self.get_and_create_if_not_exists_log_file_path()

            with open(log_file_path, "a") as log_file:
                log_file.write(self.format(record) + "\n")

        except Exception:
            self.handleError(record)

    def get_and_create_if_not_exists_log_file_path(self):
        now = datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        day = now.strftime("%d")
        hour = now.strftime("%H")
        minute = now.strftime("%M")

        log_dir = os.path.join(self.base_dir, year, month, day, hour)
        os.makedirs(log_dir, exist_ok=True)

        log_file_path = os.path.join(log_dir, f"{minute}.txt")
        return log_file_path
