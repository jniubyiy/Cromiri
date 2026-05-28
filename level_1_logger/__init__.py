from level_0.level_base import LevelWrapper, LevelCore, Box
from .box_logger.logger_box import LoggerBox

class LoggerLevelCore(LevelCore):
    def __init__(self):
        super().__init__("LoggerLevel")

    def setup_boxes(self):
        logger_wrapper = self.register_box(LoggerBox())
        logger_wrapper.expose_methods("log", "set_level", "get_level")

    def log(self, level, message):
        self.send_to_box("logger", "log", level, message)

    def set_log_level(self, level):
        self.send_to_box("logger", "set_level", level)

    def get_log_level(self):
        return self.send_to_box("logger", "get_level")

class LoggerLevelWrapper(LevelWrapper):
    def __init__(self):
        core = LoggerLevelCore()
        super().__init__(core)
        core.setup_boxes()
        self.register_public_api("log", "set_log_level", "get_log_level")
        self.allow_request_from("*", ["log", "set_level", "get_level"])

    def initialize(self):
        pass