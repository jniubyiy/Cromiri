from level_0.level_base import LevelWrapper, LevelCore, Box
from .box_reloader.reloader import ReloaderBox

class ManagerLevelCore(LevelCore):
    def __init__(self):
        super().__init__("ManagerLevel")
        self._level_zero = None

    def set_level_zero(self, level_zero):
        """Получает ссылку на LevelZero для управления всеми уровнями."""
        self._level_zero = level_zero

    def setup_boxes(self):
        reloader_wrapper = self.register_box(ReloaderBox(self))
        reloader_wrapper.expose_methods("reload_box", "reload_level")

    def reload_box(self, target_level: str, box_name: str):
        """Перезагружает конкретный бокс на любом из вышестоящих уровней."""
        if not self._level_zero:
            raise RuntimeError("LevelZero не установлен")
        self._level_zero.reload_box(target_level, box_name)

    def reload_level(self, target_level: str):
        """Перезагружает весь уровень (его ядро и обёртку), сохраняя связи."""
        if not self._level_zero:
            raise RuntimeError("LevelZero не установлен")
        self._level_zero.reload_level(target_level)


class ManagerLevelWrapper(LevelWrapper):
    def __init__(self):
        core = ManagerLevelCore()
        super().__init__(core)
        core.setup_boxes()
        self.register_public_api("reload_box", "reload_level")
        self.allow_request_from("*", ["reload_box", "reload_level"])

    def initialize(self):
        pass

    def set_level_zero(self, level_zero):
        """Прокидывает ссылку на LevelZero в ядро."""
        self._core.set_level_zero(level_zero)