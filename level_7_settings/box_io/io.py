import json, os
from level_0.level_base import Box
from logger import browser_logger

class SettingsIOBox(Box):
    def __init__(self):
        super().__init__("io")
    def load(self, filepath):
        if not os.path.exists(filepath):
            return {}
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            browser_logger.exception(f"Ошибка загрузки настроек: {e}")
            return {}
    def save(self, filepath, data):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        try:
            with open(filepath + ".bak", 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            browser_logger.exception(f"Ошибка сохранения настроек: {e}")