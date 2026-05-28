from level_0.level_base import LevelWrapper, LevelCore, Box
from .box_cpu.cpu import CPUBox
from .box_gpu.gpu import GPUBox
from .box_memory.memory import MemoryBox

class DeviceLevelCore(LevelCore):
    def __init__(self):
        super().__init__("DeviceLevel")

    def setup_boxes(self):
        cpu_wrapper = self.register_box(CPUBox())
        cpu_wrapper.expose_methods("get_info", "get_load_percent", "get_available_threads")

        gpu_wrapper = self.register_box(GPUBox())
        gpu_wrapper.expose_methods("get_list", "get_load", "is_any_gpu_available")

        mem_wrapper = self.register_box(MemoryBox())
        mem_wrapper.expose_methods("get_total", "get_usage_percent")

    def get_cpu_info(self):
        return self.send_to_box("cpu", "get_info")
    def get_cpu_load_percent(self):
        return self.send_to_box("cpu", "get_load_percent")
    def get_available_threads(self):
        return self.send_to_box("cpu", "get_available_threads")
    def get_gpu_list(self):
        return self.send_to_box("gpu", "get_list")
    def get_gpu_load(self):
        return self.send_to_box("gpu", "get_load")
    def is_gpu_available(self):
        return self.send_to_box("gpu", "is_any_gpu_available")
    def get_total_ram(self):
        return self.send_to_box("memory", "get_total")

class DeviceLevelWrapper(LevelWrapper):
    def __init__(self):
        core = DeviceLevelCore()
        super().__init__(core)
        core.setup_boxes()
        self.register_public_api(
            "get_cpu_info", "get_cpu_load_percent", "get_available_threads",
            "get_gpu_list", "get_gpu_load", "is_gpu_available", "get_total_ram"
        )
        self.allow_request_from("*", [
            "get_info", "get_load_percent", "get_available_threads",
            "get_list", "get_load", "is_any_gpu_available",
            "get_total", "get_usage_percent"
        ])
    def initialize(self):
        pass