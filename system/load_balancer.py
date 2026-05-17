# system/load_balancer.py
from .device_detector import DeviceDetector
from .cpu_manager import CPUManager
from .gpu_manager import GPUManager
from logger import browser_logger

class LoadBalancer:
    """
    Центральный балансировщик нагрузки: собирает данные с CPU/GPU
    и даёт рекомендации по созданию новых вкладок или распределению ресурсов.
    """
    def __init__(self):
        self.device = DeviceDetector()
        self.cpu = CPUManager(self.device)
        self.gpu = GPUManager(self.device)

    def can_open_new_tab(self, threshold_cpu=90, threshold_gpu=85):
        """
        Проверяет, достаточно ли ресурсов для комфортного открытия новой вкладки.
        Возвращает (bool, str) где str – пояснение.
        """
        cpu_load = self.cpu.get_current_load_percent()
        if cpu_load > threshold_cpu:
            return False, f"Высокая загрузка CPU ({cpu_load}%)"
        if self.gpu.is_any_gpu_available():
            gpu_load = self.gpu.get_gpu_load()
            if gpu_load > threshold_gpu:
                return False, f"Высокая загрузка GPU ({gpu_load}%)"
        return True, "Ресурсы достаточны"

    def get_system_status(self):
        return {
            "cpu_load": self.cpu.get_current_load_percent(),
            "available_threads": self.cpu.get_available_threads(),
            "gpu_load": self.gpu.get_gpu_load() if self.gpu.is_any_gpu_available() else 0,
            "ram_total_gb": self.device.total_ram // (1024**3),
            "gpu_available": self.gpu.is_any_gpu_available()
        }