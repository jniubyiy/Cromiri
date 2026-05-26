import os
from level_0.level_base import LevelWrapper, LevelCore, Box
from .box_buffer.buffer import BufferBox
from .box_state.state import StateBox
from .box_history.history import HistoryBox
from .box_bookmarks.bookmarks import BookmarksBox

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

        hist_wrapper = self.register_box(HistoryBox())
        hist_wrapper.expose_methods("set_user_dir", "record_visit", "record_action",
                                    "record_download", "record_settings_change",
                                    "get_all_events", "clear_history")

        bookmarks_wrapper = self.register_box(BookmarksBox())
        bookmarks_wrapper.expose_methods("set_user_dir", "add_bookmark", "remove_bookmark", "get_all_bookmarks")

    def _get_user_path(self, username):
        base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "session")
        return os.path.join(base, username)

    def load_session(self, username):
        user_dir = self._get_user_path(username)
        os.makedirs(user_dir, exist_ok=True)
        self.send_to_box("buffer", "load_all", user_dir)
        self.send_to_box("state", "load", user_dir)
        self.send_to_box("history", "set_user_dir", user_dir)
        self.send_to_box("bookmarks", "set_user_dir", user_dir)

    def save_session(self):
        self.send_to_box("buffer", "save_all")
        self.send_to_box("state", "save")
        # Закладки сохраняются сразу при изменении, но дополнительный вызов не нужен

    def log_action(self, action_type, details=None):
        self.send_to_box("buffer", "log_action", action_type, details)

    def get_tab_states(self):
        return self.send_to_box("state", "get_states")

    def set_tab_states(self, states):
        self.send_to_box("state", "set_states", states)

    # Методы для работы с историей
    def record_visit(self, url, title=""):
        self.send_to_box("history", "record_visit", url, title)

    def record_action(self, action, details=None):
        self.send_to_box("history", "record_action", action, details)

    def record_download(self, file_name):
        self.send_to_box("history", "record_download", file_name)

    def record_settings_change(self, changes):
        self.send_to_box("history", "record_settings_change", changes)

    def get_all_history_events(self, event_type=None):
        return self.send_to_box("history", "get_all_events", event_type)

    # Методы для работы с закладками
    def add_bookmark(self, title, url):
        return self.send_to_box("bookmarks", "add_bookmark", title, url)

    def remove_bookmark(self, index):
        return self.send_to_box("bookmarks", "remove_bookmark", index)

    def get_all_bookmarks(self):
        return self.send_to_box("bookmarks", "get_all_bookmarks")

class SessionLevelWrapper(LevelWrapper):
    def __init__(self, settings_wrapper):
        core = SessionLevelCore(settings_wrapper)
        super().__init__(core)
        core.setup_boxes()
        self.register_public_api(
            "load_session", "save_session", "log_action",
            "get_tab_states", "set_tab_states",
            "record_visit", "record_action", "record_download",
            "record_settings_change", "get_all_history_events",
            "add_bookmark", "remove_bookmark", "get_all_bookmarks"
        )
        self.allow_request_from("*", [
            "load_all", "save_all", "log_action", "load", "save", "get_states", "set_states",
            "set_user_dir", "record_visit", "record_action", "record_download",
            "record_settings_change", "get_all_events", "clear_history",
            "set_user_dir", "add_bookmark", "remove_bookmark", "get_all_bookmarks"
        ])

    def initialize(self):
        active_user = self._core._settings.get("users.active", "Default")
        self._core.load_session(active_user)