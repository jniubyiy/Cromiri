from level_0.level_base import Box
from logger import browser_logger

class HotkeyBox(Box):
    def __init__(self):
        super().__init__("hotkeys")
        self._registered = {}
        self._history = []

    def register(self, key_combination, callback):
        self._registered[key_combination] = callback
        browser_logger.info(f"Зарегистрирована горячая клавиша: {key_combination}")

    def unregister(self, key_combination):
        if key_combination in self._registered:
            del self._registered[key_combination]
            browser_logger.info(f"Удалена горячая клавиша: {key_combination}")

    def get_history(self):
        return self._history