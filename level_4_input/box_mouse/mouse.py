from level_0.level_base import Box
from logger import browser_logger

class MouseBox(Box):
    def __init__(self):
        super().__init__("mouse")
        self._gestures = {}
        self._history = []

    def register_gesture(self, gesture, callback):
        self._gestures[gesture] = callback
        browser_logger.info(f"Зарегистрирован жест мыши: {gesture}")

    def unregister_gesture(self, gesture):
        if gesture in self._gestures:
            del self._gestures[gesture]
            browser_logger.info(f"Удалён жест мыши: {gesture}")

    def get_gesture_history(self):
        return self._history