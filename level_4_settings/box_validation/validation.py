from logger import browser_logger

class SettingsValidationBox:
    def validate(self, data):
        if not isinstance(data, dict):
            browser_logger.warning("Настройки повреждены, сброс")
            data.clear()
        if "profile_path" not in data:
            data["profile_path"] = "browser_data"