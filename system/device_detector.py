# system/device_detector.py
import psutil
import platform
import subprocess
import sys
from logger import browser_logger

class DeviceDetector:
    """
    Определяет аппаратные и программные ресурсы системы:
    - CPU: модель, ядра (физические/логические), частота
    - GPU: список видеокарт с поддержкой драйверов (через GPUtil или systeminfo)
    - ОЗУ: общий объём
    """
    def __init__(self):
        self.cpu_info = {}
        self.gpu_list = []
        self.total_ram = 0
        self.detect()

    def detect(self):
        self._detect_cpu()
        self._detect_gpu()
        self._detect_memory()
        browser_logger.info(f"Обнаружены устройства: CPU={self.cpu_info.get('name')}, "
                            f"GPU={len(self.gpu_list)} шт., RAM={self.total_ram // (1024**3)} GB")

    def _detect_cpu(self):
        try:
            freq = psutil.cpu_freq()
            self.cpu_info = {
                'name': platform.processor(),
                'physical_cores': psutil.cpu_count(logical=False),
                'logical_cores': psutil.cpu_count(logical=True),
                'max_freq_mhz': freq.max if freq else None,
                'architecture': platform.machine()
            }
        except Exception as e:
            browser_logger.error(f"Ошибка обнаружения CPU: {e}")

    def _detect_gpu(self):
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            for gpu in gpus:
                self.gpu_list.append({
                    'name': gpu.name,
                    'driver': gpu.driver,
                    'memory_total_mb': gpu.memoryTotal,
                    'load': gpu.load * 100
                })
        except Exception as e:
            browser_logger.warning(f"GPUtil не установлен или GPU не обнаружены: {e}")
            # Запасной метод через wmi или subprocess (опционально)
            self.gpu_list.append({'name': 'Unknown GPU', 'driver': 'N/A', 'memory_total_mb': 0, 'load': 0})

    def _detect_memory(self):
        try:
            mem = psutil.virtual_memory()
            self.total_ram = mem.total
        except Exception as e:
            browser_logger.error(f"Ошибка определения ОЗУ: {e}")

    def get_cpu_count(self):
        return self.cpu_info.get('logical_cores', 4)

    def get_gpu_list(self):
        return self.gpu_list