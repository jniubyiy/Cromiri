import os
from level_0.level_base import LevelWrapper, LevelCore, Box
from .box_checker.checker import FileCheckerBox

class FileLevelCore(LevelCore):
    def __init__(self):
        super().__init__("FileLevel")

    def setup_boxes(self):
        checker_wrapper = self.register_box(FileCheckerBox())
        checker_wrapper.expose_methods("ensure_required_dirs")

    def check_paths(self):
        self.send_to_box("checker", "ensure_required_dirs")

class FileLevelWrapper(LevelWrapper):
    def __init__(self):
        core = FileLevelCore()
        super().__init__(core)
        core.setup_boxes()
        self.register_public_api("check_paths")
        self.allow_request_from("*", ["ensure_required_dirs"])

    def initialize(self):
        self._core.check_paths()