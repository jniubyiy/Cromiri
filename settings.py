# settings.py
import json
import os

class SettingsManager:
    def __init__(self, filepath=None):
        if filepath is None:
            settings_dir = os.path.join(os.path.dirname(__file__), "settings")
            os.makedirs(settings_dir, exist_ok=True)
            filepath = os.path.join(settings_dir, "settings.json")
        self.filepath = filepath
        self.data = {
            "profile_path": os.path.join(os.path.dirname(__file__), "browser_data"),
            "extensions_state": {},
            "custom_styles": [],
            "site_scripts": [],
            "browser_config": {
                "user_agent": None,
                "javascript_enabled": True,
                "images_enabled": True
            }
        }
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self.data.update(loaded)
            except Exception:
                pass

    def save(self):
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def get(self, key, default=None):
        keys = key.split('.')
        value = self.data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    def set(self, key, value):
        keys = key.split('.')
        d = self.data
        for k in keys[:-1]:
            d = d.setdefault(k, {})
        d[keys[-1]] = value