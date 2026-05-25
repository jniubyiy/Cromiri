from level_0.level_base import LevelWrapper, LevelCore, Box
from .box_loader.loader import LoaderBox
from .box_manager.manager import ManagerBox

class ExtensionsLevelCore(LevelCore):
    def __init__(self, settings_wrapper):
        super().__init__("ExtensionsLevel")
        self._settings = settings_wrapper

    def setup_boxes(self):
        loader_wrapper = self.register_box(LoaderBox(self._settings))
        loader_wrapper.expose_methods("scan")
        # manager регистрируется позже

    def set_profile(self, profile):
        mgr_wrapper = self.register_box(ManagerBox(profile, self._settings))
        mgr_wrapper.expose_methods("install_all", "add_extension", "remove_extension", "toggle_extension", "is_enabled", "get_installed_names")

    def get_loader(self):
        return self._box_wrappers.get("loader")

    def get_manager(self):
        return self._box_wrappers.get("manager")

    # Методы, доступные через обёртку
    def scan_extensions(self):
        return self.send_to_box("loader", "scan")

    def install_all_extensions(self, paths):
        self.send_to_box("manager", "install_all", paths)

    def add_extension(self, path):
        return self.send_to_box("manager", "add_extension", path)

    def remove_extension(self, name):
        self.send_to_box("manager", "remove_extension", name)

    def toggle_extension(self, name, enabled):
        self.send_to_box("manager", "toggle_extension", name, enabled)

class ExtensionsLevelWrapper(LevelWrapper):
    def __init__(self, settings_wrapper):
        core = ExtensionsLevelCore(settings_wrapper)
        super().__init__(core)
        core.setup_boxes()
        self.register_public_api("set_profile", "scan_extensions", "install_all_extensions", "add_extension", "remove_extension", "toggle_extension", "get_loader", "get_manager")
        self.allow_request_from("*", ["scan", "install_all", "add_extension", "remove_extension", "toggle_extension", "is_enabled", "get_installed_names"])

    def initialize(self):
        pass