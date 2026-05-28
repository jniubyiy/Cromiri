from level_0.level_base import Box

class ProfileBox(Box):
    def __init__(self, settings):
        super().__init__("profile")
        self.settings = settings

    def switch_user(self, name):
        self.settings.set("users.active", name)
        self.settings.save_settings()

    def get_active_user(self):
        return self.settings.get("users.active", "Default")

    def create_user(self, name):
        users = self.settings.get("users.list", ["Default"])
        if name not in users:
            users.append(name)
            self.settings.set("users.list", users)
            self.settings.save_settings()

    def delete_user(self, name):
        if name == "Default":
            return False
        users = self.settings.get("users.list", ["Default"])
        if name in users:
            users.remove(name)
            self.settings.set("users.list", users)
            self.settings.save_settings()
            if self.get_active_user() == name:
                self.switch_user("Default")
            return True
        return False

    def get_users(self):
        return self.settings.get("users.list", ["Default"])