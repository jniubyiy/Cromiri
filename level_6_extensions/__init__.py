from level_0.level_base import LevelWrapper, LevelCore
from .box_loader.loader import LoaderBox
from .box_manager.manager import ManagerBox

class ExtensionsLevelCore(LevelCore):
    def __init__(self, settings_wrapper):
        super().__init__("ExtensionsLevel")
        self._settings = settings_wrapper
    def setup_boxes(self):
        self.register_box("loader", LoaderBox(self._settings))
    def set_profile(self, profile):
        self.register_box("manager", ManagerBox(profile, self._settings))
    def get_loader(self):
        return self.get_box("loader")
    def get_manager(self):
        return self.get_box("manager")

class ExtensionsLevelWrapper(LevelWrapper):
    def __init__(self, settings_wrapper):
        core = ExtensionsLevelCore(settings_wrapper)
        super().__init__(core)
        core.setup_boxes()
        self.register_external_api(["set_profile", "get_loader", "get_manager"])
    def initialize(self):
        pass