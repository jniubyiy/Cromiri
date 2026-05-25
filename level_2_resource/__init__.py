from level_0.level_base import LevelWrapper, LevelCore, Box
from .box_balancer.balancer import LoadBalancerBox
from .box_task_mgr.task_manager import TaskManagerBox

class ResourceLevelCore(LevelCore):
    def __init__(self, device_wrapper: LevelWrapper):
        super().__init__("ResourceLevel")
        self._device_wrapper = device_wrapper

    def setup_boxes(self):
        balancer_wrapper = self.register_box(LoadBalancerBox(self._device_wrapper))
        balancer_wrapper.expose_methods("can_open_new_tab")

        task_mgr_wrapper = self.register_box(TaskManagerBox(self._device_wrapper))
        task_mgr_wrapper.expose_methods("submit")

    def can_open_tab(self):
        return self.send_to_box("balancer", "can_open_new_tab")

    def submit_task(self, func, *args, **kwargs):
        self.send_to_box("task_mgr", "submit", func, *args, **kwargs)

class ResourceLevelWrapper(LevelWrapper):
    def __init__(self, device_wrapper: LevelWrapper):
        core = ResourceLevelCore(device_wrapper)
        super().__init__(core)
        core.setup_boxes()
        self.register_public_api("can_open_tab", "submit_task")
        self.allow_request_from("*", ["can_open_new_tab", "submit"])

    def initialize(self):
        pass