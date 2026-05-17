# system/gpu_manager.py
import threading
from logger import browser_logger

class GPUManager:
    """
    Мониторит загрузку GPU и управляет выбором графического процессора для задач.
    В браузере Chromium/QtWebEngine GPU используется для рендеринга автоматически,
    но мы можем рекомендовать не запускать дополнительные нагруженные операции при высокой загрузке.
    """
    def __init__(self, device_detector=None):
        self.device = device_detector
        self._lock = threading.Lock()
        self.gpu_count = len(self.device.get_gpu_list()) if self.device else 0

    def get_gpu_load(self, gpu_index=0):
        """Возвращает загрузку указанного GPU в процентах."""
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus and gpu_index < len(gpus):
                return gpus[gpu_index].load * 100
        except Exception as e:
            browser_logger.error(f"Ошибка получения загрузки GPU: {e}")
        return 0

    def is_any_gpu_available(self):
        return self.gpu_count > 0

    def is_heavy_load(self, threshold=80):
        return any(self.get_gpu_load(i) > threshold for i in range(self.gpu_count))