# session.py
import json
import os
from datetime import datetime
from PyQt6.QtCore import QObject

class SessionManager(QObject):
    def __init__(self, parent=None, storage_path=None):
        super().__init__(parent)
        if storage_path is None:
            session_dir = os.path.join(os.path.dirname(__file__), "session")
            os.makedirs(session_dir, exist_ok=True)
            storage_path = os.path.join(session_dir, "session.json")
        self.storage_path = storage_path
        self.history = {
            "actions": [],
            "navigation": [],
            "settings_changes": [],
            "page_events": []
        }
        self.load()

    def log_action(self, action_type, detail=""):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": action_type,
            "detail": detail
        }
        self.history["actions"].append(entry)

    def log_navigation(self, url, title=""):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "url": url,
            "title": title
        }
        self.history["navigation"].append(entry)

    def log_setting_change(self, setting_name, old_value, new_value):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "setting": setting_name,
            "old_value": old_value,
            "new_value": new_value
        }
        self.history["settings_changes"].append(entry)

    def log_page_event(self, event_type, detail=""):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "detail": detail
        }
        self.history["page_events"].append(entry)

    def save(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка сохранения сессии: {e}")

    def load(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except Exception:
                pass

    def clear(self):
        self.history = {key: [] for key in self.history}