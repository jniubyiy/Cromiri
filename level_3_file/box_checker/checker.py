import os
from logger import browser_logger

REQUIRED_DIRS = ["browser_data", "settings", "session", "extensions", "logs", "builtin_extensions"]

class FileCheckerBox:
    def ensure_required_dirs(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        for dirname in REQUIRED_DIRS:
            path = os.path.join(base_dir, dirname)
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
                browser_logger.info(f"Создана папка: {path}")