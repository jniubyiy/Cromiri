from level_0.level_base import Box

class ReloaderBox(Box):
    """Бокс, предоставляющий функции перезагрузки других боксов и уровней."""
    def __init__(self, core):
        super().__init__("reloader")
        self._core = core    # ManagerLevelCore

    def reload_box(self, target_level: str, box_name: str):
        """Перезагружает указанный бокс на целевом уровне."""
        self._core.reload_box(target_level, box_name)

    def reload_level(self, target_level: str):
        """Перезагружает весь целевой уровень."""
        self._core.reload_level(target_level)