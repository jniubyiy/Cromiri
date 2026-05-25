import os, json
from logger import browser_logger

class LoaderBox:
    def __init__(self, settings_wrapper):
        self.settings = settings_wrapper
        self._ext_dir = os.path.join(os.path.dirname(__file__), "..", "..", "extensions")
        self._builtin_dir = os.path.join(os.path.dirname(__file__), "..", "..", "builtin_extensions")
    def scan(self):
        webengine = {}
        if os.path.isdir(self._ext_dir):
            for name in os.listdir(self._ext_dir):
                path = os.path.join(self._ext_dir, name)
                if os.path.isdir(path) and os.path.isfile(os.path.join(path, 'manifest.json')):
                    size_mb = self._get_dir_size_mb(path)
                    max_size = self.settings.get("extension_limits.max_size_mb", 100)
                    if size_mb > max_size:
                        browser_logger.warning(f"Расширение '{name}' пропущено (размер {size_mb:.1f} МБ > {max_size} МБ)")
                        continue
                    if self._validate_manifest(os.path.join(path, 'manifest.json')):
                        webengine[name] = path
        builtin = []
        if os.path.isdir(self._builtin_dir):
            for name in os.listdir(self._builtin_dir):
                full = os.path.join(self._builtin_dir, name)
                if os.path.isdir(full) and os.path.isfile(os.path.join(full, '__init__.py')):
                    builtin.append(name)
        return webengine, builtin
    def _validate_manifest(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return isinstance(data, dict) and "name" in data and "version" in data
        except Exception as e:
            browser_logger.error(f"Ошибка чтения манифеста {path}: {e}")
            return False
    def _get_dir_size_mb(self, path):
        total = 0
        for dirpath, _, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.isfile(fp):
                    total += os.path.getsize(fp)
        return total / (1024 * 1024)