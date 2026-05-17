# session.py
import json
import os
from datetime import datetime
from PyQt6.QtCore import QObject
from logger import browser_logger

MAX_SESSION_SIZE = 5 * 1024 * 1024  # 5 MB

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
        self.history["actions"].append({
            "timestamp": datetime.now().isoformat(),
            "type": action_type,
            "detail": detail
        })

    def log_navigation(self, url, title=""):
        self.history["navigation"].append({
            "timestamp": datetime.now().isoformat(),
            "url": url,
            "title": title
        })

    def log_setting_change(self, setting_name, old_value, new_value):
        self.history["settings_changes"].append({
            "timestamp": datetime.now().isoformat(),
            "setting": setting_name,
            "old_value": old_value,
            "new_value": new_value
        })

    def log_page_event(self, event_type, detail=""):
        self.history["page_events"].append({
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "detail": detail
        })

    def save(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        # Обрезаем старые записи, если размер превышает лимит
        self._trim_history()
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            browser_logger.exception(f"Ошибка сохранения сессии: {e}")

    def load(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                for key in self.history.keys():
                    if key in loaded and isinstance(loaded[key], list):
                        self.history[key] = loaded[key]
            except (json.JSONDecodeError, IOError) as e:
                browser_logger.exception(f"Ошибка загрузки сессии: {e}")

    def clear(self):
        self.history = {key: [] for key in self.history}

    def _trim_history(self):
        # Грубая оценка размера: сериализуем в JSON и проверяем длину
        try:
            while True:
                data = json.dumps(self.history, ensure_ascii=False)
                if len(data) <= MAX_SESSION_SIZE:
                    break
                # Удаляем самую старую запись из actions или navigation
                removed = False
                for cat in ("actions", "navigation"):
                    if self.history[cat]:
                        self.history[cat].pop(0)
                        removed = True
                        break
                if not removed:
                    # Если нечего удалять, очищаем всё
                    self.clear()
                    break
        except Exception as e:
            browser_logger.exception(f"Ошибка при обрезке сессии: {e}")