# extensions_loader.py
import os
import json
from typing import Dict, List
from logger import browser_logger

MAX_EXTENSION_SIZE_MB = 100

class ExtensionsLoader:
    def __init__(self, settings):
        self.settings = settings
        self.webengine_extensions: Dict[str, str] = {}
        self.builtin_extensions: Dict[str, dict] = {}
        self._ext_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extensions")
        self._builtin_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "builtin_extensions")

    def analyze_extensions(self):
        self._scan_webengine_extensions()
        self._scan_builtin_extensions()
        browser_logger.info(
            f"Анализ расширений завершён: WebEngine={len(self.webengine_extensions)}, "
            f"встроенные={len(self.builtin_extensions)}"
        )

    def _scan_webengine_extensions(self):
        if not os.path.isdir(self._ext_dir):
            os.makedirs(self._ext_dir, exist_ok=True)
            return
        for name in os.listdir(self._ext_dir):
            try:
                path = os.path.join(self._ext_dir, name)
                if not os.path.isdir(path):
                    continue
                # Проверка размера папки
                size_mb = self._get_dir_size_mb(path)
                if size_mb > MAX_EXTENSION_SIZE_MB:
                    browser_logger.warning(f"Расширение '{name}' пропущено: размер {size_mb:.1f} МБ превышает лимит")
                    continue
                manifest = os.path.join(path, 'manifest.json')
                if not os.path.isfile(manifest):
                    continue
                # Валидация манифеста
                if self._validate_manifest(manifest):
                    self.webengine_extensions[name] = path
                    browser_logger.debug(f"Найдено WebEngine-расширение: {name}")
            except Exception as e:
                browser_logger.exception(f"Ошибка сканирования расширения '{name}': {e}")

    def _scan_builtin_extensions(self):
        if not os.path.isdir(self._builtin_dir):
            os.makedirs(self._builtin_dir, exist_ok=True)
            return
        for entry in os.listdir(self._builtin_dir):
            try:
                full_path = os.path.join(self._builtin_dir, entry)
                if os.path.isdir(full_path) and os.path.isfile(os.path.join(full_path, '__init__.py')):
                    self.builtin_extensions[entry] = {'path': full_path}
                    browser_logger.debug(f"Найдено встроенное расширение: {entry}")
            except Exception as e:
                browser_logger.exception(f"Ошибка сканирования встроенного расширения '{entry}': {e}")

    def _validate_manifest(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if not isinstance(data, dict):
                return False
            if "name" not in data or "version" not in data:
                browser_logger.warning(f"Манифест {path} не содержит обязательных полей name/version")
                return False
            return True
        except Exception as e:
            browser_logger.exception(f"Ошибка чтения манифеста {path}: {e}")
            return False

    def _get_dir_size_mb(self, path):
        total = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.isfile(fp):
                    total += os.path.getsize(fp)
        return total / (1024 * 1024)

    def get_webengine_extension_paths(self) -> Dict[str, str]:
        return self.webengine_extensions

    def get_builtin_extension_names(self) -> List[str]:
        return list(self.builtin_extensions.keys())