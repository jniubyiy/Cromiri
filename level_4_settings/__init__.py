import os
from level_0.level_base import LevelWrapper, LevelCore
from .box_io.io import SettingsIOBox
from .box_validation.validation import SettingsValidationBox
from .box_config.config import SettingsConfigBox

class SettingsLevelCore(LevelCore):
    def __init__(self):
        super().__init__("SettingsLevel")
        self._data = {}
        self._filepath = None
    def setup_boxes(self):
        self.register_box("io", SettingsIOBox())
        self.register_box("validation", SettingsValidationBox())
        self.register_box("config", SettingsConfigBox())
    def load_settings(self, filepath):
        io = self.get_box("io")
        self._data = io.load(filepath)
        self._filepath = filepath
        self.get_box("config").set_data(self._data)
        self.get_box("validation").validate(self._data)
    def save_settings(self):
        self.get_box("io").save(self._filepath, self._data)
    def get(self, key, default=None):
        return self.get_box("config").get(key, default)
    def set(self, key, value):
        self.get_box("config").set(key, value)

class SettingsLevelWrapper(LevelWrapper):
    def __init__(self):
        core = SettingsLevelCore()
        super().__init__(core)
        core.setup_boxes()
        self.register_external_api(["load_settings", "save_settings", "get", "set"])
    def initialize(self):
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(base, "settings", "settings.json")
        self._core.load_settings(path)