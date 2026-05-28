import sys
import os
import re
import json
import importlib
from PyQt6.QtWidgets import QApplication
from level_0 import LevelZero
from logger import browser_logger

def scan_levels(base_dir):
    levels = []
    pattern = re.compile(r'^level_(\d+)_(.+)$')
    for entry in os.listdir(base_dir):
        match = pattern.match(entry)
        if not match:
            continue
        num = int(match.group(1))
        if num == 0:
            continue
        name_suffix = match.group(2)
        module_name = entry
        wrapper_class = None
        deps = []
        try:
            mod = importlib.import_module(module_name)
            if hasattr(mod, 'WRAPPER_CLASS'):
                wrapper_class = mod.WRAPPER_CLASS
            if hasattr(mod, 'DEPS'):
                deps = mod.DEPS
        except Exception:
            pass
        if not wrapper_class:
            wrapper_class = ''.join(part.capitalize() for part in name_suffix.split('_')) + 'LevelWrapper'
        level_name = wrapper_class.replace('LevelWrapper', 'Level')
        levels.append({
            'num': num,
            'name': level_name,
            'module': module_name,
            'class': wrapper_class,
            'deps': deps
        })
    levels.sort(key=lambda x: x['num'])
    return levels

def scan_boxes(level_path):
    boxes = []
    if not os.path.isdir(level_path):
        return boxes
    for entry in os.listdir(level_path):
        if entry.startswith('box_') and os.path.isdir(os.path.join(level_path, entry)):
            boxes.append(entry)
    return boxes

def generate_registry(base_dir, output_path):
    levels = scan_levels(base_dir)
    registry = []
    for lvl in levels:
        level_dir = os.path.join(base_dir, lvl['module'])
        boxes = scan_boxes(level_dir)
        registry.append({
            'name': lvl['name'],
            'module': lvl['module'],
            'class': lvl['class'],
            'deps': lvl['deps'],
            'boxes': boxes
        })
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Автоматически сгенерированный реестр уровней и боксов\n")
        f.write("# Не редактируйте вручную\n\n")
        f.write("LEVELS = ")
        f.write(json.dumps(registry, indent=4, ensure_ascii=False))
        f.write("\n")
    browser_logger.info(f"Реестр уровней сгенерирован: {output_path}")

if __name__ == "__main__":
    browser_logger.info("Запуск браузера Cromiri")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    registry_path = os.path.join(base_dir, "level_0", "level_registry.py")

    if not os.path.exists(registry_path) or "--generate-registry" in sys.argv:
        generate_registry(base_dir, registry_path)

    level_zero = LevelZero()
    level_zero.bootstrap()

    app = QApplication(sys.argv)

    # Получаем UILevel по имени, а не по индексу
    ui_wrapper = None
    for level in level_zero.levels:
        if level._core.level_name == "UILevel":
            ui_wrapper = level
            break

    if not ui_wrapper:
        browser_logger.error("Не удалось найти UILevel среди загруженных уровней")
        sys.exit(1)

    main_window = ui_wrapper.get_main_window()
    main_window.show()
    browser_logger.info("Главное окно отображено, браузер готов")
    sys.exit(app.exec())