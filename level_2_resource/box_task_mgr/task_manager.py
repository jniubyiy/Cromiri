from PyQt6.QtCore import QThreadPool, QRunnable
from level_0.level_base import Box
from logger import browser_logger

class TaskManagerBox(Box):
    def __init__(self, device_wrapper):
        super().__init__("task_mgr")
        self.device = device_wrapper
        self.pool = QThreadPool()
        self.pool.setMaxThreadCount(self.device.get_available_threads())

    def submit(self, func, *args, **kwargs):
        class Task(QRunnable):
            def run(self):
                try:
                    func(*args, **kwargs)
                except Exception as e:
                    browser_logger.error(f"Ошибка в фоновой задаче: {e}")
        # Приоритет = номер уровня (меньше номер → выше приоритет)
        priority = self.level_number
        self.pool.start(Task(), priority=priority)