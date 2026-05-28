from level_0.level_base import Box
from logger import browser_logger

class SettingsValidationBox(Box):
    def __init__(self):
        super().__init__("validation")
    def validate(self, data):
        if not isinstance(data, dict):
            browser_logger.warning("Настройки повреждены, сброс")
            data.clear()
        if "profile_path" not in data:
            data["profile_path"] = "browser_data"