from level_0.level_base import Box
from logger import browser_logger

class LoggerBox(Box):
    def __init__(self):
        super().__init__("logger")
        self._log_level = "INFO"

    def log(self, level, message):
        if level == "DEBUG":
            browser_logger.debug(message)
        elif level == "INFO":
            browser_logger.info(message)
        elif level == "WARNING":
            browser_logger.warning(message)
        elif level == "ERROR":
            browser_logger.error(message)
        else:
            browser_logger.info(message)

    def set_level(self, level):
        self._log_level = level

    def get_level(self):
        return self._log_level