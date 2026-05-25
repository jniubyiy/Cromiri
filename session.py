# session.py
import json
import os
from datetime import datetime
from PyQt6.QtCore import QObject
from logger import browser_logger

AUTO_SAVE_THRESHOLD = 50

class SessionManager(QObject):
    def __init__(self, parent=None, storage_dir=None):
        super().__init__(parent)
        if storage_dir is None:
            base_dir = os.path.join(os.path.dirname(__file__), "session")
        else:
            base_dir = storage_dir
        self.base_dir = base_dir

        self.dirs = {
            "actions": os.path.join(base_dir, "actions"),
            "navigation": os.path.join(base_dir, "navigation"),
            "settings_changes": os.path.join(base_dir, "settings_changes"),
            "page_events": os.path.join(base_dir, "page_events"),
            "tab_states": os.path.join(base_dir, "tab_states"),
        }
        for d in self.dirs.values():
            os.makedirs(d, exist_ok=True)

        self.files = {
            "actions": os.path.join(self.dirs["actions"], "actions.json"),
            "navigation": os.path.join(self.dirs["navigation"], "navigation.json"),
            "settings_changes": os.path.join(self.dirs["settings_changes"], "settings_changes.json"),
            "page_events": os.path.join(self.dirs["page_events"], "page_events.json"),
            "tab_states": os.path.join(self.dirs["tab_states"], "tab_states.json"),
        }

        self.buffers = {
            "actions": [],
            "navigation": [],
            "settings_changes": [],
            "page_events": [],
        }
        self._tab_states = []   # не буферизуется в памяти, сохраняется только при явном вызове

        self.max_size_mb = 5
        self.max_restore_fails = 3

        self.load_all()
        self._load_tab_states()

    def load_all(self):
        for key, path in self.files.items():
            if key == "tab_states":
                continue  # загружается отдельно
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    if isinstance(data, list):
                        self.buffers[key] = data
                        browser_logger.debug(f"Загружено {len(data)} записей {key}")
                except Exception as e:
                    browser_logger.exception(f"Ошибка загрузки {key}: {e}")

    def _load_tab_states(self):
        path = self.files["tab_states"]
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, list):
                    self._tab_states = data
                    browser_logger.debug(f"Загружено состояний вкладок: {len(data)}")
            except Exception as e:
                browser_logger.exception(f"Ошибка загрузки tab_states: {e}")

    def save_all(self):
        for key, path in self.files.items():
            if key == "tab_states":
                continue
            try:
                self._trim_buffer(key)
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(self.buffers[key], f, indent=2, ensure_ascii=False)
            except Exception as e:
                browser_logger.exception(f"Ошибка сохранения {key}: {e}")
        # tab_states сохраняется отдельно
        self._save_tab_states()

    def _save_tab_states(self):
        path = self.files["tab_states"]
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self._tab_states, f, indent=2, ensure_ascii=False)
        except Exception as e:
            browser_logger.exception(f"Ошибка сохранения tab_states: {e}")

    def _trim_buffer(self, key):
        max_file_size = (self.max_size_mb * 1024 * 1024) // 4
        data = self.buffers[key]
        while True:
            size = len(json.dumps(data, ensure_ascii=False))
            if size <= max_file_size or not data:
                break
            data.pop(0)
        self.buffers[key] = data

    def _auto_save(self, key):
        if len(self.buffers[key]) >= AUTO_SAVE_THRESHOLD:
            self.save_all()

    def log_action(self, action_type, detail=""):
        entry = {"timestamp": datetime.now().isoformat(), "type": action_type, "detail": detail}
        self.buffers["actions"].append(entry)
        self._auto_save("actions")

    def log_navigation(self, url, title=""):
        entry = {"timestamp": datetime.now().isoformat(), "url": url, "title": title}
        self.buffers["navigation"].append(entry)
        self._auto_save("navigation")

    def log_setting_change(self, setting_name, old_value, new_value):
        entry = {"timestamp": datetime.now().isoformat(), "setting": setting_name, "old_value": old_value, "new_value": new_value}
        self.buffers["settings_changes"].append(entry)
        self._auto_save("settings_changes")

    def log_page_event(self, event_type, detail=""):
        entry = {"timestamp": datetime.now().isoformat(), "type": event_type, "detail": detail}
        self.buffers["page_events"].append(entry)
        self._auto_save("page_events")

    def save_tab_states(self, states):
        """Сохраняет список состояний вкладок (обычно вызывается при закрытии)."""
        self._tab_states = states
        self._save_tab_states()

    def get_tab_states(self):
        """Возвращает сохранённые состояния вкладок (для восстановления)."""
        return self._tab_states

    @property
    def history(self):
        return self.buffers

    def clear(self):
        for key in self.buffers:
            self.buffers[key] = []
        self._tab_states = []
        self.save_all()

    def save(self):
        self.save_all()

    def load(self):
        self.load_all()
        self._load_tab_states()