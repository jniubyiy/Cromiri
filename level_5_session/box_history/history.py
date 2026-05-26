import json
import os
from datetime import datetime
from level_0.level_base import Box
from logger import browser_logger

class HistoryBox(Box):
    def __init__(self):
        super().__init__("history")
        self._events = []          # список всех событий
        self._filepath = None      # путь к файлу истории текущего пользователя

    def set_user_dir(self, user_dir: str):
        """Устанавливает директорию пользователя и загружает существующую историю."""
        os.makedirs(user_dir, exist_ok=True)
        self._filepath = os.path.join(user_dir, "history.json")
        self._load()
        browser_logger.info(f"История загружена из {self._filepath}, событий: {len(self._events)}")

    def _load(self):
        if self._filepath and os.path.exists(self._filepath):
            try:
                with open(self._filepath, 'r', encoding='utf-8') as f:
                    self._events = json.load(f)
            except Exception as e:
                browser_logger.error(f"Ошибка загрузки истории: {e}")
                self._events = []
        else:
            self._events = []

    def _save(self):
        if self._filepath:
            try:
                with open(self._filepath, 'w', encoding='utf-8') as f:
                    json.dump(self._events, f, indent=2, ensure_ascii=False)
            except Exception as e:
                browser_logger.error(f"Ошибка сохранения истории: {e}")

    def record_visit(self, url: str, title: str = ""):
        event = {
            "type": "visit",
            "url": url,
            "title": title,
            "timestamp": datetime.now().isoformat()
        }
        self._events.append(event)
        self._save()
        browser_logger.debug(f"Записано посещение: {url}")

    def record_action(self, action: str, details: dict = None):
        event = {
            "type": "action",
            "action": action,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self._events.append(event)
        self._save()
        browser_logger.debug(f"Записано действие: {action}")

    def record_download(self, file_name: str):
        event = {
            "type": "download",
            "file_name": file_name,
            "timestamp": datetime.now().isoformat()
        }
        self._events.append(event)
        self._save()
        browser_logger.debug(f"Записана загрузка: {file_name}")

    def record_settings_change(self, changes: dict):
        """changes: dict вида {ключ: {"old": старое, "new": новое}}"""
        event = {
            "type": "settings_change",
            "changes": changes,
            "timestamp": datetime.now().isoformat()
        }
        self._events.append(event)
        self._save()
        browser_logger.debug(f"Записаны изменения настроек: {list(changes.keys())}")

    def get_all_events(self, event_type: str = None):
        """Возвращает все события, опционально фильтруя по типу."""
        if event_type:
            return [e for e in self._events if e.get("type") == event_type]
        return self._events

    def clear_history(self):
        self._events.clear()
        self._save()