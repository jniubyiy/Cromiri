from typing import Dict, List
from .level_base import LevelWrapper
from logger import browser_logger

class LevelZero:
    def __init__(self):
        self._loaded_levels: Dict[str, LevelWrapper] = {}
        self._init_sequence = [
            {"name": "device",    "module": "level_1_device",    "class": "DeviceLevelWrapper",    "deps": []},
            {"name": "resource",  "module": "level_2_resource",  "class": "ResourceLevelWrapper",  "deps": ["device"]},
            {"name": "file",      "module": "level_3_file",      "class": "FileLevelWrapper",      "deps": []},
            {"name": "settings",  "module": "level_4_settings",  "class": "SettingsLevelWrapper",  "deps": []},
            {"name": "session",   "module": "level_5_session",   "class": "SessionLevelWrapper",   "deps": []},
            {"name": "extensions","module": "level_6_extensions","class": "ExtensionsLevelWrapper","deps": ["settings"]},
            {"name": "ui",        "module": "level_7_ui",        "class": "UILevelWrapper",        "deps": ["settings","session","extensions"]},
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
                browser_logger.info(f"Уровень '{name}' ({module_path}) загружен и инициализирован")
            except Exception as e:
                browser_logger.exception(f"КРИТИЧЕСКАЯ ОШИБКА загрузки уровня {name} ({module_path}): {e}")
                raise SystemExit(1) from e
        browser_logger.info("Все уровни успешно активированы, передаю управление UI")