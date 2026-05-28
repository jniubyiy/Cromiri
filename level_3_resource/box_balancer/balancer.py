from level_0.level_base import Box
from logger import browser_logger

class LoadBalancerBox(Box):
    def __init__(self, device_wrapper):
        super().__init__("balancer")
        self.device = device_wrapper

    def can_open_new_tab(self, threshold_cpu=90, threshold_gpu=85):
        # Обращаемся к device_wrapper через его публичные методы (не напрямую к боксам!)
        cpu_load = self.device.get_cpu_load_percent()
        if cpu_load > threshold_cpu:
            return False, f"Высокая загрузка CPU ({cpu_load}%)"
        if self.device.is_gpu_available():
            gpu_load = self.device.get_gpu_load()
            if gpu_load > threshold_gpu:
                return False, f"Высокая загрузка GPU ({gpu_load}%)"
        return True, "Ресурсы достаточны"