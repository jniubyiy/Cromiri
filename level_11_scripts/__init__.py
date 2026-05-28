from level_0.level_base import LevelWrapper, LevelCore
from .box_script.script_box import ScriptBox

DEPS = ["UserLevel"]
WRAPPER_CLASS = "ScriptLevelWrapper"

class ScriptLevelCore(LevelCore):
    def __init__(self, user_wrapper):
        super().__init__("ScriptLevel")
        self._user = user_wrapper

    def setup_boxes(self):
        script_box = ScriptBox(self._user)
        script_wrapper = self.register_box(script_box)
        script_wrapper.expose_methods("inject", "add", "remove", "toggle", "update", "get_all")

    def inject_script(self, view, url):
        self.send_to_box("script", "inject", view, url)

    def add_script(self, name, desc, pattern, code):
        self.send_to_box("script", "add", name, desc, pattern, code)

    def remove_script(self, index):
        self.send_to_box("script", "remove", index)

    def toggle_script(self, index, enabled):
        self.send_to_box("script", "toggle", index, enabled)

    def update_script(self, index, name, desc, pattern, code):
        self.send_to_box("script", "update", index, name, desc, pattern, code)

    def get_scripts(self):
        return self.send_to_box("script", "get_all")


class ScriptLevelWrapper(LevelWrapper):
    def __init__(self, user_wrapper):
        core = ScriptLevelCore(user_wrapper)
        super().__init__(core)
        core.setup_boxes()
        self.register_public_api("inject_script", "add_script", "remove_script",
                                 "toggle_script", "update_script", "get_scripts")
        self.allow_request_from("*", ["inject", "add", "remove", "toggle", "update", "get_all"])

    def initialize(self):
        pass