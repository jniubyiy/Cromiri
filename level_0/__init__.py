from typing import Dict, List
from .level_base import LevelWrapper
from logger import browser_logger

class LevelZero:
    def __init__(self):
        self._loaded_levels: Dict[str, LevelWrapper] = {}
        self._init_sequence = [
            {"name": "DeviceLevel",     "module": "level_1_device",     "class": "DeviceLevelWrapper",      "deps": []},
            {"name": "ResourceLevel",   "module": "level_2_resource",   "class": "ResourceLevelWrapper",    "deps": ["DeviceLevel"]},
            {"name": "FileLevel",       "module": "level_3_file",       "class": "FileLevelWrapper",        "deps": []},
            {"name": "SettingsLevel",   "module": "level_4_settings",   "class": "SettingsLevelWrapper",    "deps": []},
            {"name": "SessionLevel",    "module": "level_5_session",    "class": "SessionLevelWrapper",     "deps": []},
            {"name": "ExtensionsLevel", "module": "level_6_extensions", "class": "ExtensionsLevelWrapper",  "deps": ["SettingsLevel"]},
            {"name": "UILevel",         "module": "level_7_ui",         "class": "UILevelWrapper",          "deps": ["SettingsLevel", "SessionLevel", "ExtensionsLevel"]},
        ]
        self.levels: List[LevelWrapper] = []

    def bootstrap(self):
        browser_logger.info("=== Нулевой уровень: запуск последовательной загрузки ===")
        for entry in self._init_sequence:
            name = entry["name"]
            module_path = entry["module"]
            class_name = entry["class"]
            dep_names = entry["deps"]
            try:
                import importlib
                module = importlib.import_module(module_path)
                wrapper_cls = getattr(module, class_name)
                dep_instances = [self._loaded_levels[dep] for dep in dep_names]
                if dep_instances:
                    wrapper = wrapper_cls(*dep_instances)
                else:
                    wrapper = wrapper_cls()
                wrapper.initialize()
                self._loaded_levels[name] = wrapper
                self.levels.append(wrapper)
                browser_logger.info(f"Уровень '{name}' загружен и инициализирован")
            except Exception as e:
                browser_logger.exception(f"КРИТИЧЕСКАЯ ОШИБКА загрузки уровня {name}: {e}")
                raise SystemExit(1) from e
        # Связываем соседей (по порядку загрузки)
        for i, level in enumerate(self.levels):
            lower = self.levels[i-1] if i > 0 else None
            upper = self.levels[i+1] if i < len(self.levels)-1 else None
            level.set_neighbors(lower=lower, upper=upper)
        browser_logger.info("Все уровни активированы и связаны")