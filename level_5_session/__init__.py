import os
from level_0.level_base import LevelWrapper, LevelCore, Box
from .box_buffer.buffer import BufferBox
from .box_state.state import StateBox

class SessionLevelCore(LevelCore):
    def __init__(self):
        super().__init__("SessionLevel")
        self._base_dir = None

    def setup_boxes(self):
        buf_wrapper = self.register_box(BufferBox())
        buf_wrapper.expose_methods("load_all", "save_all", "log_action")

        state_wrapper = self.register_box(StateBox())
        state_wrapper.expose_methods("load", "save", "get_states", "set_states")

    def load_session(self, base_dir):
        self._base_dir = base_dir
        self.send_to_box("buffer", "load_all", base_dir)
        self.send_to_box("state", "load", base_dir)

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
    def __init__(self):
        core = SessionLevelCore()
        super().__init__(core)
        core.setup_boxes()
        self.register_public_api("load_session", "save_session", "log_action", "get_tab_states", "set_tab_states")
        self.allow_request_from("*", ["load_all", "save_all", "log_action", "load", "save", "get_states", "set_states"])

    def initialize(self):
        base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "session")
        self._core.load_session(base)