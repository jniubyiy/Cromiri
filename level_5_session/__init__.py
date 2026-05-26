import os
from level_0.level_base import LevelWrapper, LevelCore, Box
from .box_buffer.buffer import BufferBox
from .box_state.state import StateBox

class SessionLevelCore(LevelCore):
    def __init__(self, settings_wrapper):
        super().__init__("SessionLevel")
        self._settings = settings_wrapper
        self._base_dir = None
        self._user_dir = None

    def setup_boxes(self):
        buf_wrapper = self.register_box(BufferBox())
        buf_wrapper.expose_methods("load_all", "save_all", "log_action")

        state_wrapper = self.register_box(StateBox())
        state_wrapper.expose_methods("load", "save", "get_states", "set_states")

    def _get_user_path(self, username):
        base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "session")
        return os.path.join(base, username)

    def load_session(self, username):
        user_dir = self._get_user_path(username)
        os.makedirs(user_dir, exist_ok=True)
        self.send_to_box("buffer", "load_all", user_dir)
        self.send_to_box("state", "load", user_dir)

    def save_session(self):
        self.send_to_box("buffer", "save_all")
        self.send_to_box("state", "save")

    def log_action(self, action_type, details=None):
        self.send_to_box("buffer", "log_action", action_type, details)

    def get_tab_states(self):
        return self.send_to_box("state", "get_states")

    def set_tab_states(self, states):
        self.send_to_box("state", "set_states", states)


class SessionLevelWrapper(LevelWrapper):
    def __init__(self, settings_wrapper):
        core = SessionLevelCore(settings_wrapper)
        super().__init__(core)
        core.setup_boxes()
        self.register_public_api("load_session", "save_session", "log_action",
                                 "get_tab_states", "set_tab_states")
        self.allow_request_from("*", ["load_all", "save_all", "log_action",
                                      "load", "save", "get_states", "set_states"])

    def initialize(self):
        active_user = self._core._settings.get("users.active", "Default")
        self._core.load_session(active_user)