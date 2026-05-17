# logger.py
import logging
import os
import sys
from datetime import datetime

class BrowserLogger:
    """
    Централизованный логгер браузера.
    Записывает информационные сообщения, предупреждения и ошибки
    в файл browser.log и дублирует в консоль.
    """
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

        # Определяем директорию для логов
        if log_dir is None:
            log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
        os.makedirs(log_dir, exist_ok=True)

        self.log_file = os.path.join(log_dir, "browser.log")

        # Создаём логгер
        self.logger = logging.getLogger("browser")
        self.logger.setLevel(level)

        # Форматтер
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Файловый обработчик
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Консольный обработчик (только warnings и ошибки)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

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
        """Логирует исключение с трейсбеком."""
        self.logger.exception(msg, *args, **kwargs)

# Глобальный экземпляр для импорта
browser_logger = BrowserLogger()