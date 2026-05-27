import sys
import os
import re
import json
from PyQt6.QtWidgets import QApplication
from level_0 import LevelZero
from logger import browser_logger

def scan_levels(base_dir):
    """
    Сканирует папки уровней (level_N_...) в base_dir и возвращает список словарей
    с информацией об уровне: имя, модуль, класс обёртки, номер, зависимости (пока пустые).
    """
    levels = []
    pattern = re.compile(r'^level_(\d+)_(.+)$')
    for entry in os.listdir(base_dir):
        match = pattern.match(entry)
        if not match:
            continue
        num = int(match.group(1))
        name_suffix = match.group(2)
        class_name = ''.join(part.capitalize() for part in name_suffix.split('_')) + 'LevelWrapper'
        module_name = entry
        level_name = class_name.replace('LevelWrapper', 'Level')
        levels.append({
            'num': num,
            'name': level_name,
            'module': module_name,
            'class': class_name,
            'deps': []  # зависимости можно будет задать в description.txt
        })
    levels.sort(key=lambda x: x['num'])
    return levels

def scan_boxes(level_path):
    """Сканирует подпапки box_* внутри папки уровня и возвращает список имён боксов."""
    boxes = []
    if not os.path.isdir(level_path):
        return boxes
    for entry in os.listdir(level_path):
        if entry.startswith('box_') and os.path.isdir(os.path.join(level_path, entry)):
            boxes.append(entry)
    return boxes

def generate_registry(base_dir, output_path):
    """Создаёт файл level_registry.py, содержащий списки уровней и их боксов."""
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

    # Генерируем реестр, если его нет или если запущен с флагом --generate-registry
    if not os.path.exists(registry_path) or "--generate-registry" in sys.argv:
        generate_registry(base_dir, registry_path)

    # 1. Загружаем все уровни (включая импорт QtWebEngineWidgets)
    level_zero = LevelZero()
    level_zero.bootstrap()

    # 2. Создаём QApplication после импорта WebEngine
    app = QApplication(sys.argv)

    # 3. Получаем главное окно от UI-уровня через прямой вызов публичного метода
    ui_wrapper = level_zero.levels[-1]  # UILevelWrapper
    main_window = ui_wrapper.get_main_window()
    main_window.show()
    browser_logger.info("Главное окно отображено, браузер готов")
    sys.exit(app.exec())