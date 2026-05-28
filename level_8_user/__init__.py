from level_0.level_base import LevelWrapper, LevelCore
from .box_profile.profile import ProfileBox

DEPS = ["SettingsLevel"]
WRAPPER_CLASS = "UserLevelWrapper"

class UserLevelCore(LevelCore):
    def __init__(self, settings_wrapper):
        super().__init__("UserLevel")
        self._settings = settings_wrapper

    def setup_boxes(self):
        profile_wrapper = self.register_box(ProfileBox(self._settings))
        profile_wrapper.expose_methods("switch_user", "get_active_user", "create_user", "delete_user", "get_users")

    # Прокси-методы к SettingsLevel
    def tr(self, key, default=None):
        return self._settings.tr(key, default)

    def get(self, key, default=None):
        return self._settings.get(key, default)

    def set(self, key, value):
        self._settings.set(key, value)

    def save_settings(self):
        self._settings.save_settings()

    def load_language(self, lang):
        self._settings.load_language(lang)

    def available_languages(self):
        return self._settings.available_languages()

    def get_current_lang(self):
        return self._settings.get_current_lang()

    def get_settings(self):
        return self._settings

    def switch_user(self, name):
        self.send_to_box("profile", "switch_user", name)

    def get_active_user(self):
        return self.send_to_box("profile", "get_active_user")

    def create_user(self, name):
        self.send_to_box("profile", "create_user", name)

    def delete_user(self, name):
        self.send_to_box("profile", "delete_user", name)

    def get_users(self):
        return self.send_to_box("profile", "get_users")

class UserLevelWrapper(LevelWrapper):
    def __init__(self, settings_wrapper):
        core = UserLevelCore(settings_wrapper)
        super().__init__(core)
        core.setup_boxes()
        self.register_public_api(
            "switch_user", "get_active_user", "create_user", "delete_user", "get_users",
            "tr", "get", "set", "save_settings", "load_language", "available_languages",
            "get_current_lang", "get_settings"
        )
        self.allow_request_from("*", [
            "switch_user", "get_active_user", "create_user", "delete_user", "get_users",
            "tr", "get", "set", "save_settings", "load_language", "available_languages",
            "get_current_lang", "get_settings"
        ])

    def initialize(self):
        pass