# settings.py
import json
import os
from logger import browser_logger

class SettingsManager:
    def __init__(self, filepath=None):
        if filepath is None:
            settings_dir = os.path.join(os.path.dirname(__file__), "settings")
            os.makedirs(settings_dir, exist_ok=True)
            filepath = os.path.join(settings_dir, "settings.json")
        self.filepath = filepath
        self.bak_path = filepath + ".bak"
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
        self._validate()

    def load(self):
        # Пробуем основной файл
        path = self.filepath
        if os.path.exists(path):
            if not self._load_json(path):
                # если основной повреждён, пробуем бэкап
                if os.path.exists(self.bak_path):
                    browser_logger.warning("Повреждён основной файл настроек, пробую резервную копию")
                    if not self._load_json(self.bak_path):
                        browser_logger.error("Не удалось загрузить настройки даже из резервной копии")
                else:
                    browser_logger.error("Основной файл настроек повреждён, резервная копия отсутствует")

    def _load_json(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
            self.data.update(loaded)
            return True
        except (json.JSONDecodeError, IOError) as e:
            browser_logger.exception(f"Ошибка загрузки настроек из {path}: {e}")
            return False

    def save(self):
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        # Сначала сохраняем в бэкап, потом в основной
        try:
            with open(self.bak_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            browser_logger.exception(f"Ошибка сохранения настроек: {e}")

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

    def _validate(self):
        # Пример валидации: profile_path должен быть непустой строкой
        if not isinstance(self.data.get("profile_path"), str) or not self.data["profile_path"]:
            browser_logger.warning("Некорректный путь профиля, сброшен на значение по умолчанию")
            self.data["profile_path"] = os.path.join(os.path.dirname(__file__), "browser_data")
        # Проверка булевых настроек
        bc = self.data.get("browser_config", {})
        for key in ("javascript_enabled", "images_enabled"):
            if not isinstance(bc.get(key), bool):
                bc[key] = True