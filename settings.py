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
            },
            "tab_limits": {
                "max_tabs": 50,
                "reload_limit": 5,
                "reload_interval_sec": 30
            },
            "resource_limits": {
                "max_memory_percent": 85,
                "max_cpu_percent": 90,
                "monitor_interval_ms": 5000
            },
            "extension_limits": {
                "max_size_mb": 100,
                "max_errors_per_interval": 5,
                "error_interval_sec": 10
            },
            "interface": {
                "animation_timeout_ms": 1000
            },
            "session": {
                "max_size_mb": 5,
                "max_restore_fails": 3
            }
        }
        self.load()
        self._validate()

    def load(self):
        path = self.filepath
        if os.path.exists(path):
            if not self._load_json(path):
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
            # Рекурсивное обновление словаря с сохранением значений по умолчанию
            self._deep_update(self.data, loaded)
            return True
        except (json.JSONDecodeError, IOError) as e:
            browser_logger.exception(f"Ошибка загрузки настроек из {path}: {e}")
            return False

    def _deep_update(self, base, updates):
        for key, value in updates.items():
            if isinstance(value, dict) and isinstance(base.get(key), dict):
                self._deep_update(base[key], value)
            else:
                base[key] = value

    def save(self):
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
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
        # Профиль
        if not isinstance(self.data.get("profile_path"), str) or not self.data["profile_path"]:
            browser_logger.warning("Некорректный путь профиля, сброшен на значение по умолчанию")
            self.data["profile_path"] = os.path.join(os.path.dirname(__file__), "browser_data")
        # Булевы настройки браузера
        bc = self.data.get("browser_config", {})
        for key in ("javascript_enabled", "images_enabled"):
            if not isinstance(bc.get(key), bool):
                bc[key] = True
        # Числовые лимиты: принудительно в разумных пределах
        self._validate_limits("tab_limits.max_tabs", 1, 200)
        self._validate_limits("tab_limits.reload_limit", 1, 50)
        self._validate_limits("tab_limits.reload_interval_sec", 5, 300)
        self._validate_limits("resource_limits.max_memory_percent", 30, 100)
        self._validate_limits("resource_limits.max_cpu_percent", 30, 100)
        self._validate_limits("resource_limits.monitor_interval_ms", 1000, 60000)
        self._validate_limits("extension_limits.max_size_mb", 10, 1000)
        self._validate_limits("extension_limits.max_errors_per_interval", 1, 100)
        self._validate_limits("extension_limits.error_interval_sec", 1, 300)
        self._validate_limits("interface.animation_timeout_ms", 100, 5000)
        self._validate_limits("session.max_size_mb", 1, 100)
        self._validate_limits("session.max_restore_fails", 0, 10)

    def _validate_limits(self, key, min_val, max_val):
        val = self.get(key)
        if not isinstance(val, (int, float)) or val < min_val or val > max_val:
            default = self._get_default(key)
            browser_logger.warning(f"Недопустимое значение {key}: {val}, установлено {default}")
            self.set(key, default)

    def _get_default(self, key):
        # Получаем значение по умолчанию из исходного self.data
        keys = key.split('.')
        d = SettingsManager().__dict__['data']  # хак для получения дефолтов
        for k in keys:
            d = d[k]
        return d