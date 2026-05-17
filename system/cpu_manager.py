# system/cpu_manager.py
import psutil
import threading
from logger import browser_logger

class CPUManager:
    """
    Мониторит загрузку CPU и предлагает оптимальное количество потоков для задач.
    """
    def __init__(self, device_detector=None):
        self.device = device_detector
        self._lock = threading.Lock()
        self.max_workers = self._calculate_max_workers()

    def _calculate_max_workers(self):
        logical = psutil.cpu_count(logical=True) or 4
        # Оставляем одно ядро для системы
        return max(1, logical - 1)

    def get_current_load_percent(self):
        """Возвращает среднюю загрузку CPU в процентах."""
        try:
            return psutil.cpu_percent(interval=0.5)
        except Exception as e:
            browser_logger.error(f"Ошибка получения загрузки CPU: {e}")
            return 50  # значение по умолчанию

    def get_available_threads(self):
        """Рекомендует число потоков на основе текущей загрузки."""
        load = self.get_current_load_percent()
        # Чем выше загрузка, тем меньше дополнительных потоков выделяем
        if load > 90:
            return 1
        elif load > 70:
            return max(1, self.max_workers // 4)
        elif load > 50:
            return max(2, self.max_workers // 2)
        else:
            return self.max_workers

    def is_overloaded(self, threshold=85):
        return self.get_current_load_percent() > threshold