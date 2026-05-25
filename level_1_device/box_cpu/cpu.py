import psutil
import platform
from logger import browser_logger

class CPUBox:
    def get_info(self):
        try:
            freq = psutil.cpu_freq()
            return {
                'name': platform.processor() or 'Unknown CPU',
                'physical_cores': psutil.cpu_count(logical=False),
                'logical_cores': psutil.cpu_count(logical=True),
                'max_freq_mhz': freq.max if freq else None,
                'architecture': platform.machine()
            }
        except Exception as e:
            browser_logger.exception(f"CPUBox error: {e}")
            return {}
    def get_load_percent(self):
        return psutil.cpu_percent(interval=0.5)
    def get_available_threads(self):
        logical = psutil.cpu_count(logical=True) or 4
        return max(1, logical - 1)