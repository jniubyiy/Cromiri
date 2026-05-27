from typing import Dict, List
from .level_base import LevelWrapper
from logger import browser_logger
import importlib
import os
import json

class LevelZero:
    def __init__(self):
        self._loaded_levels: Dict[str, LevelWrapper] = {}
        # Попытка загрузить реестр из сгенерированного файла
        try:
            from . import level_registry
            self._init_sequence = level_registry.LEVELS
            browser_logger.info("Загружен внешний реестр уровней")
        except ImportError:
            # Резервный список, если реестр не сгенерирован
            self._init_sequence = [
                {"name": "DeviceLevel",     "module": "level_1_device",       "class": "DeviceLevelWrapper",     "deps": []},
                {"name": "ResourceLevel",   "module": "level_2_resource",     "class": "ResourceLevelWrapper",   "deps": ["DeviceLevel"]},
                {"name": "ManagerLevel",    "module": "level_3_manager",      "class": "ManagerLevelWrapper",    "deps": []},
                {"name": "FileLevel",       "module": "level_4_file",         "class": "FileLevelWrapper",       "deps": []},
                {"name": "SettingsLevel",   "module": "level_5_settings",     "class": "SettingsLevelWrapper",   "deps": []},
                {"name": "SessionLevel",    "module": "level_6_session",      "class": "SessionLevelWrapper",    "deps": ["SettingsLevel"]},
                {"name": "ExtensionsLevel", "module": "level_7_extensions",   "class": "ExtensionsLevelWrapper", "deps": ["SettingsLevel"]},
                {"name": "UILevel",         "module": "level_8_ui",           "class": "UILevelWrapper",         "deps": ["SettingsLevel", "SessionLevel", "ExtensionsLevel"]},
            ]
            browser_logger.info("Используется встроенный список уровней (реестр не найден)")
        self.levels: List[LevelWrapper] = []

    def bootstrap(self):
        browser_logger.info("=== Нулевой уровень: запуск последовательной загрузки ===")
        for entry in self._init_sequence:
            name = entry["name"]
            module_path = entry["module"]
            class_name = entry["class"]
            dep_names = entry.get("deps", [])
            try:
                module = importlib.import_module(module_path)
                wrapper_cls = getattr(module, class_name)
                dep_instances = [self._loaded_levels[dep] for dep in dep_names] if dep_names else []
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

        for i, level in enumerate(self.levels):
            lower = self.levels[i-1] if i > 0 else None
            upper = self.levels[i+1] if i < len(self.levels)-1 else None
            level.set_neighbors(lower=lower, upper=upper)

        # Передаём ссылку на LevelZero в ManagerLevel
        manager = self._loaded_levels.get("ManagerLevel")
        if manager:
            manager.set_level_zero(self)

        browser_logger.info("Все уровни активированы и связаны")

    def reload_box(self, target_level: str, box_name: str):
        """Перезагружает указанный бокс в целевом уровне."""
        level = self._loaded_levels.get(target_level)
        if not level:
            raise ValueError(f"Уровень '{target_level}' не найден")
        core = level._core
        if hasattr(core, 'reload_box'):
            core.reload_box(box_name)
        else:
            raise NotImplementedError(f"Уровень '{target_level}' не поддерживает перезагрузку боксов")

    def reload_level(self, target_level: str):
        """Перезагружает целевой уровень, заменяя его ядро и обёртку."""
        if target_level not in self._loaded_levels:
            raise ValueError(f"Уровень '{target_level}' не найден")
        old_wrapper = self._loaded_levels[target_level]
        idx = self.levels.index(old_wrapper)
        lower = old_wrapper._lower
        upper = old_wrapper._upper

        wrapper_cls = type(old_wrapper)
        new_wrapper = wrapper_cls()
        new_wrapper.initialize()

        if lower:
            lower._upper = new_wrapper
        if upper:
            upper._lower = new_wrapper
        new_wrapper.set_neighbors(lower, upper)

        self._loaded_levels[target_level] = new_wrapper
        self.levels[idx] = new_wrapper

        del old_wrapper
        browser_logger.info(f"Уровень '{target_level}' перезагружен")