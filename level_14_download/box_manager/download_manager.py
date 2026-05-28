from level_0.level_base import Box
from logger import browser_logger

class DownloadManagerBox(Box):
    def __init__(self):
        super().__init__("download_manager")
        self._queue = []
        self._next_id = 1

    def add(self, url, file_path):
        entry = {
            "id": self._next_id,
            "url": url,
            "file_path": file_path,
            "status": "pending"
        }
        self._queue.append(entry)
        self._next_id += 1
        browser_logger.info(f"Добавлена загрузка #{entry['id']}: {url}")
        return entry["id"]

    def pause(self, download_id):
        for entry in self._queue:
            if entry["id"] == download_id and entry["status"] == "active":
                entry["status"] = "paused"
                browser_logger.info(f"Загрузка #{download_id} приостановлена")

    def resume(self, download_id):
        for entry in self._queue:
            if entry["id"] == download_id and entry["status"] == "paused":
                entry["status"] = "pending"
                browser_logger.info(f"Загрузка #{download_id} возобновлена")

    def cancel(self, download_id):
        for entry in self._queue:
            if entry["id"] == download_id:
                entry["status"] = "cancelled"
                browser_logger.info(f"Загрузка #{download_id} отменена")
                break

    def get_queue(self):
        return self._queue