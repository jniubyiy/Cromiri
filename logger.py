import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from datetime import datetime

class BrowserLogger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, log_dir=None, level=logging.DEBUG):
        if self._initialized:
            return
        self._initialized = True

        if log_dir is None:
            log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
        os.makedirs(log_dir, exist_ok=True)

        self.log_file = os.path.join(log_dir, "browser.log")
        self.logger = logging.getLogger("browser")
        self.logger.setLevel(level)

        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Файловый обработчик: 5 МБ, до 3 бэкапов
        file_handler = RotatingFileHandler(
            self.log_file, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8'
        )
        file_handler.setLevel(level)  # DEBUG — будут записаны все вызовы боксов
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Консольный обработчик полностью убран

        self.logger.info("=" * 50)
        self.logger.info("Запуск браузера")
        self.logger.info(f"Лог-файл: {self.log_file}")

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        self.logger.exception(msg, *args, **kwargs)

browser_logger = BrowserLogger()