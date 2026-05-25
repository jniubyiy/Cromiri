from level_0.level_base import LevelWrapper, LevelCore
from .box_cpu.cpu import CPUBox
from .box_gpu.gpu import GPUBox
from .box_memory.memory import MemoryBox

class DeviceLevelCore(LevelCore):
    def __init__(self):
        super().__init__("DeviceLevel")
    def setup_boxes(self):
        self.register_box("cpu", CPUBox())
        self.register_box("gpu", GPUBox())
        self.register_box("memory", MemoryBox())
    def get_cpu_info(self):
        return self.get_box("cpu").get_info()
    def get_gpu_list(self):
        return self.get_box("gpu").get_list()
    def get_total_ram(self):
        return self.get_box("memory").get_total()

class DeviceLevelWrapper(LevelWrapper):
    def __init__(self):
        core = DeviceLevelCore()
        super().__init__(core)
        core.setup_boxes()
        self.register_external_api(["get_cpu_info", "get_gpu_list", "get_total_ram"])
    def initialize(self):
        # при необходимости выполняем обнаружение
        pass