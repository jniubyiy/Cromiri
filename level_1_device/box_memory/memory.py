import psutil
from level_0.level_base import Box
from logger import browser_logger

class MemoryBox(Box):
    def __init__(self):
        super().__init__("memory")
    def get_total(self):
        try:
            return psutil.virtual_memory().total
        except Exception as e:
            browser_logger.exception(f"MemoryBox error: {e}")
            return 0
    def get_usage_percent(self):
        return psutil.virtual_memory().percent