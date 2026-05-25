from level_0.level_base import LevelWrapper, LevelCore
from .box_checker.checker import FileCheckerBox

class FileLevelCore(LevelCore):
    def __init__(self):
        super().__init__("FileLevel")
    def setup_boxes(self):
        self.register_box("checker", FileCheckerBox())
    def check_paths(self):
        self.get_box("checker").ensure_required_dirs()

class FileLevelWrapper(LevelWrapper):
    def __init__(self):
        core = FileLevelCore()
        super().__init__(core)
        core.setup_boxes()
        self.register_external_api(["check_paths"])
    def initialize(self):
        self._core.check_paths()