import json
import os
from level_0.level_base import Box
from logger import browser_logger

class BookmarksBox(Box):
    def __init__(self):
        super().__init__("bookmarks")
        self._bookmarks = []          # список словарей {title, url}
        self._filepath = None

    def set_user_dir(self, user_dir: str):
        """Устанавливает директорию пользователя и загружает закладки."""
        os.makedirs(user_dir, exist_ok=True)
        self._filepath = os.path.join(user_dir, "bookmarks.json")
        self._load()
        browser_logger.info(f"Закладки загружены из {self._filepath}, количество: {len(self._bookmarks)}")

    def _load(self):
        if self._filepath and os.path.exists(self._filepath):
            try:
                with open(self._filepath, 'r', encoding='utf-8') as f:
                    self._bookmarks = json.load(f)
            except Exception as e:
                browser_logger.error(f"Ошибка загрузки закладок: {e}")
                self._bookmarks = []
        else:
            self._bookmarks = []

    def _save(self):
        if self._filepath:
            try:
                with open(self._filepath, 'w', encoding='utf-8') as f:
                    json.dump(self._bookmarks, f, indent=2, ensure_ascii=False)
            except Exception as e:
                browser_logger.error(f"Ошибка сохранения закладок: {e}")

    def add_bookmark(self, title: str, url: str):
        """Добавляет новую закладку. Возвращает True при успехе."""
        # Простейшая проверка на дубликат (необязательно)
        for bm in self._bookmarks:
            if bm["url"] == url:
                browser_logger.info(f"Закладка с URL {url} уже существует")
                return False
        self._bookmarks.append({"title": title, "url": url})
        self._save()
        browser_logger.info(f"Добавлена закладка: {title} ({url})")
        return True

    def remove_bookmark(self, index: int):
        """Удаляет закладку по индексу. Возвращает True, если индекс корректен."""
        if 0 <= index < len(self._bookmarks):
            removed = self._bookmarks.pop(index)
            self._save()
            browser_logger.info(f"Удалена закладка: {removed['title']}")
            return True
        return False

    def get_all_bookmarks(self):
        """Возвращает список всех закладок."""
        return self._bookmarks