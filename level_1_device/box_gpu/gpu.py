from logger import browser_logger

class GPUBox:
    def get_list(self):
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            return [{'name': g.name, 'driver': g.driver, 'memory_total_mb': g.memoryTotal, 'load': g.load * 100} for g in gpus]
        except ImportError:
            browser_logger.info("GPUtil не установлен")
            return []
        except Exception as e:
            browser_logger.exception(f"GPUBox error: {e}")
            return []
    def get_load(self, index=0):
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus and index < len(gpus):
                return gpus[index].load * 100
        except:
            pass
        return 0
    def is_any_gpu_available(self):
        return len(self.get_list()) > 0