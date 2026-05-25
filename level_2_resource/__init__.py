from level_0.level_base import LevelWrapper, LevelCore
from .box_balancer.balancer import LoadBalancerBox
from .box_task_mgr.task_manager import TaskManagerBox

class ResourceLevelCore(LevelCore):
    def __init__(self, device_wrapper):
        super().__init__("ResourceLevel")
        self._device = device_wrapper
    def setup_boxes(self):
        self.register_box("balancer", LoadBalancerBox(self._device))
        self.register_box("task_mgr", TaskManagerBox(self._device))
    def can_open_tab(self):
        return self.get_box("balancer").can_open_new_tab()
    def submit_task(self, func, *args, **kwargs):
        self.get_box("task_mgr").submit(func, *args, **kwargs)

class ResourceLevelWrapper(LevelWrapper):
    def __init__(self, device_wrapper):
        core = ResourceLevelCore(device_wrapper)
        super().__init__(core)
        core.setup_boxes()
        self.register_external_api(["can_open_tab", "submit_task"])
    def initialize(self):
        pass