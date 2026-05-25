import psutil
from logger import browser_logger

class MemoryBox:
    def get_total(self):
        try:
            return psutil.virtual_memory().total
        except Exception as e:
            browser_logger.exception(f"MemoryBox error: {e}")
            return 0
    def get_usage_percent(self):
        return psutil.virtual_memory().percent