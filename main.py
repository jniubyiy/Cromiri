# main.py
import sys
import os
from PyQt6.QtWidgets import QApplication

# Уровень 2: логирование уже работает при импорте
from logger import browser_logger

# Уровень 3: устройства
from system.device_detector import DeviceDetector

# Уровень 4: файлы и папки
from core.file_checker import check_required_paths

# Уровень 5: настройки
from settings import SettingsManager

# Уровень 6: сессия
from session import SessionManager

# Уровень 7: анализ расширений
from extensions_loader import ExtensionsLoader

# Уровень 8: интерфейс
from ui.main_window import BrowserUI


def safe_init_level(level_name, init_func, *args, **kwargs):
    """
    Выполняет инициализацию уровня. В случае ошибки:
    - выводит подробный traceback через browser_logger.exception,
    - пишет сообщение в stderr,
    - возвращает None.
    """
    browser_logger.info(f"Инициализация уровня: {level_name}")
    try:
        result = init_func(*args, **kwargs)
        browser_logger.info(f"Уровень {level_name} успешно загружен")
        return result
    except Exception as e:
        browser_logger.exception(f"Критический сбой на уровне {level_name}: {e}")
        print(f"\n[!] Ошибка при загрузке уровня {level_name}: {e}\n"
              f"    Подробности в лог-файле.\n", file=sys.stderr)
        return None


if __name__ == "__main__":
    browser_logger.info("===== Запуск браузера Cromiri =====")

    # Уровень 3: устройства
    device_detector = safe_init_level("3. Устройства", DeviceDetector)

    # Уровень 4: файлы и папки
    safe_init_level("4. Проверка файлов", check_required_paths)

    # Уровень 5: настройки
    settings = safe_init_level("5. Настройки", SettingsManager)
    if settings is None:
        browser_logger.warning("Создаю аварийные настройки по умолчанию")
        settings = SettingsManager()

    # Уровень 6: сессия
    session = safe_init_level("6. Сессия", SessionManager)
    if session is None:
        browser_logger.warning("Сессия недоступна, создаю пустую")
        session = SessionManager()

    # Уровень 7: анализ расширений
    ext_loader = safe_init_level("7. Анализ расширений", ExtensionsLoader, settings)
    if ext_loader is None:
        browser_logger.warning("Анализатор расширений недоступен, расширения не будут загружены")
        # Заглушка, чтобы окно не падало
        class DummyLoader:
            def get_webengine_extension_paths(self):
                return {}
            def get_builtin_extension_names(self):
                return []
        ext_loader = DummyLoader()

    # Создание Qt-приложения
    app = QApplication(sys.argv)

    # Уровень 8: главное окно
    window = None
    try:
        browser_logger.info("Инициализация уровня 8: главное окно")
        window = BrowserUI(settings, session, ext_loader)
        browser_logger.info("Главное окно создано")
    except Exception as e:
        browser_logger.exception(f"Фатальная ошибка при создании окна: {e}")
        print(f"Фатальная ошибка: не удалось открыть окно браузера.\n{e}", file=sys.stderr)
        sys.exit(1)

    # Запуск
    if window:
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit(1)