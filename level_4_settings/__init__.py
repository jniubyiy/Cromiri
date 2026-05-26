import os
from level_0.level_base import LevelWrapper, LevelCore, Box
from .box_io.io import SettingsIOBox
from .box_validation.validation import SettingsValidationBox
from .box_config.config import SettingsConfigBox
from .box_locale.locale import LocaleBox

class SettingsLevelCore(LevelCore):
    def __init__(self):
        super().__init__("SettingsLevel")
        self._data = {}
        self._filepath = None

    def setup_boxes(self):
        io_wrapper = self.register_box(SettingsIOBox())
        io_wrapper.expose_methods("load", "save")

        val_wrapper = self.register_box(SettingsValidationBox())
        val_wrapper.expose_methods("validate")

        cfg_wrapper = self.register_box(SettingsConfigBox())
        cfg_wrapper.expose_methods("set_data", "get", "set")

        locale_wrapper = self.register_box(LocaleBox())
        locale_wrapper.expose_methods("tr", "available_languages", "load_language", "get_current_lang")

    def load_settings(self, filepath):
        data = self.send_to_box("io", "load", filepath)
        self._data = data
        self._filepath = filepath
        self.send_to_box("config", "set_data", data)
        self.send_to_box("validation", "validate", data)
        lang = self.send_to_box("config", "get", "locale", "ru")
        self.send_to_box("locale", "load_language", lang)

    def save_settings(self):
        self.send_to_box("io", "save", self._filepath, self._data)

    def save(self):
        """Псевдоним для save_settings (для совместимости)."""
        self.save_settings()

    def get(self, key, default=None):
        return self.send_to_box("config", "get", key, default)

    def set(self, key, value):
        self.send_to_box("config", "set", key, value)

    def tr(self, key, default=None):
        return self.send_to_box("locale", "tr", key, default)

    def available_languages(self):
        return self.send_to_box("locale", "available_languages")

    def load_language(self, lang):
        self.send_to_box("locale", "load_language", lang)

    def get_current_lang(self):
        return self.send_to_box("locale", "get_current_lang")


class SettingsLevelWrapper(LevelWrapper):
    def __init__(self):
        core = SettingsLevelCore()
        super().__init__(core)
        core.setup_boxes()
        # Добавляем все публичные методы, включая save
        self.register_public_api("load_settings", "save_settings", "get", "set",
                                 "tr", "available_languages", "load_language", "get_current_lang",
                                 "save")   # ← добавлено
        self.allow_request_from("*", ["load", "save", "validate", "set_data", "get", "set",
                                      "tr", "available_languages", "load_language", "get_current_lang"])

    def initialize(self):
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(base, "settings", "settings.json")
        self._core.load_settings(path)