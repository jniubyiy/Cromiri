from logger import browser_logger

class LoadBalancerBox:
    def __init__(self, device_wrapper):
        self.device = device_wrapper
    def can_open_new_tab(self, threshold_cpu=90, threshold_gpu=85):
        cpu_load = self.device._core.get_box("cpu").get_load_percent()
        if cpu_load > threshold_cpu:
            return False, f"Высокая загрузка CPU ({cpu_load}%)"
        if self.device._core.get_box("gpu").is_any_gpu_available():
            gpu_load = self.device._core.get_box("gpu").get_load()
            if gpu_load > threshold_gpu:
                return False, f"Высокая загрузка GPU ({gpu_load}%)"
        return True, "Ресурсы достаточны"