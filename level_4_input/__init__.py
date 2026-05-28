from level_0.level_base import LevelWrapper, LevelCore, Box
from .box_hotkeys.hotkeys import HotkeyBox
from .box_mouse.mouse import MouseBox

class InputLevelCore(LevelCore):
    def __init__(self):
        super().__init__("InputLevel")

    def setup_boxes(self):
        hotkey_wrapper = self.register_box(HotkeyBox())
        hotkey_wrapper.expose_methods("register", "unregister", "get_history")

        mouse_wrapper = self.register_box(MouseBox())
        mouse_wrapper.expose_methods("register_gesture", "unregister_gesture", "get_gesture_history")

    def register_hotkey(self, key_combination, callback):
        self.send_to_box("hotkeys", "register", key_combination, callback)

    def unregister_hotkey(self, key_combination):
        self.send_to_box("hotkeys", "unregister", key_combination)

    def get_hotkey_history(self):
        return self.send_to_box("hotkeys", "get_history")

    def register_mouse_gesture(self, gesture, callback):
        self.send_to_box("mouse", "register_gesture", gesture, callback)

    def unregister_mouse_gesture(self, gesture):
        self.send_to_box("mouse", "unregister_gesture", gesture)

    def get_mouse_gesture_history(self):
        return self.send_to_box("mouse", "get_gesture_history")


class InputLevelWrapper(LevelWrapper):
    def __init__(self):
        core = InputLevelCore()
        super().__init__(core)
        core.setup_boxes()
        self.register_public_api(
            "register_hotkey", "unregister_hotkey", "get_hotkey_history",
            "register_mouse_gesture", "unregister_mouse_gesture", "get_mouse_gesture_history"
        )
        self.allow_request_from("*", [
            "register", "unregister", "get_history",
            "register_gesture", "unregister_gesture", "get_gesture_history"
        ])

    def initialize(self):
        pass