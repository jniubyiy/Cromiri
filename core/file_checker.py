# core/file_checker.py
import os
from logger import browser_logger

REQUIRED_DIRS = [
    "browser_data",
    "settings",
    "session",
    "extensions",
    "logs",
    "builtin_extensions",
]

def check_required_paths():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for dirname in REQUIRED_DIRS:
        try:
            path = os.path.join(base_dir, dirname)
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
                browser_logger.info(f"Создана папка: {path}")
            else:
                browser_logger.debug(f"Папка существует: {path}")
        except Exception as e:
            browser_logger.exception(f"Не удалось создать/проверить папку {dirname}: {e}")
    browser_logger.info("Проверка всех необходимых папок завершена")