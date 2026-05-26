import sys
from PyQt6.QtWidgets import QApplication
from level_0 import LevelZero
from logger import browser_logger

if __name__ == "__main__":
    browser_logger.info("Запуск браузера Cromiri")
    # 1. Загружаем все уровни (включая импорт QtWebEngineWidgets)
    level_zero = LevelZero()
    level_zero.bootstrap()

    # 2. Создаём QApplication после импорта WebEngine
    app = QApplication(sys.argv)

    # 3. Получаем главное окно от UI-уровня через прямой вызов публичного метода
    ui_wrapper = level_zero.levels[-1]  # UILevelWrapper
    main_window = ui_wrapper.get_main_window()  # публичный метод
    main_window.show()
    browser_logger.info("Главное окно отображено, браузер готов")
    sys.exit(app.exec())