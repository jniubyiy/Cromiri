from PyQt6.QtCore import QThreadPool, QRunnable
from logger import browser_logger

class TaskManagerBox:
    def __init__(self, device_wrapper):
        self.device = device_wrapper
        self.pool = QThreadPool()
        self.pool.setMaxThreadCount(self.device._core.get_box("cpu").get_available_threads())
    def submit(self, func, *args, **kwargs):
        class Task(QRunnable):
            def run(self):
                try:
                    func(*args, **kwargs)
                except Exception as e:
                    browser_logger.error(f"Ошибка в фоновой задаче: {e}")
        self.pool.start(Task())