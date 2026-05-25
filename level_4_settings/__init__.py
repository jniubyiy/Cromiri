import os
from level_0.level_base import LevelWrapper, LevelCore, Box
from .box_io.io import SettingsIOBox
from .box_validation.validation import SettingsValidationBox
from .box_config.config import SettingsConfigBox

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

    def load_settings(self, filepath):
        data = self.send_to_box("io", "load", filepath)
        self._data = data
        self._filepath = filepath
        self.send_to_box("config", "set_data", data)
        self.send_to_box("validation", "validate", data)

    def save_settings(self):
        self.send_to_box("io", "save", self._filepath, self._data)

    def get(self, key, default=None):
        return self.send_to_box("config", "get", key, default)

    def set(self, key, value):
        self.send_to_box("config", "set", key, value)

class SettingsLevelWrapper(LevelWrapper):
    def __init__(self):
        core = SettingsLevelCore()
        super().__init__(core)
        core.setup_boxes()
        self.register_public_api("load_settings", "save_settings", "get", "set")
        self.allow_request_from("*", ["load", "save", "validate", "set_data", "get", "set"])

    def initialize(self):
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(base, "settings", "settings.json")
        self._core.load_settings(path)