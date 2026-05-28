import os
import shutil
import importlib
from PyQt6.QtCore import QStandardPaths
from PyQt6.QtWebEngineCore import QWebEngineProfile
from level_0.level_base import Box
from logger import browser_logger


class ManagerBox(Box):
    def __init__(self, profile: QWebEngineProfile, settings_wrapper):
        super().__init__("manager")
        self.profile = profile
        self.settings = settings_wrapper
        self._extensions = {}   # WebEngine расширения (установленные)
        self._supports = hasattr(profile, 'installExtension')
        self._ext_dir = os.path.join(os.path.dirname(__file__), "..", "..", "extensions")
        self._builtin_extensions = {}   # name -> класс расширения
        self._builtin_instances = {}    # name -> экземпляр bridge (для WebChannel)
        self._load_builtin_extensions()

    def _load_builtin_extensions(self):
        builtin_dir = os.path.join(os.path.dirname(__file__), "..", "..", "builtin_extensions")
        builtin_dir = os.path.abspath(builtin_dir)
        if not os.path.isdir(builtin_dir):
            return
        for entry in os.listdir(builtin_dir):
            ext_path = os.path.join(builtin_dir, entry)
            if os.path.isdir(ext_path) and os.path.isfile(os.path.join(ext_path, "__init__.py")):
                try:
                    module = importlib.import_module(f"builtin_extensions.{entry}")
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if isinstance(attr, type) and hasattr(attr, 'name') and hasattr(attr, 'matches') and hasattr(attr, 'get_script'):
                            self._builtin_extensions[attr.name] = attr
                            if hasattr(attr, 'get_bridge_class'):
                                download_path = self.settings.get("downloads.path", "")
                                if not download_path:
                                    download_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DownloadLocation)
                                bridge_class = attr.get_bridge_class()
                                self._builtin_instances[attr.name] = bridge_class(download_path)
                            browser_logger.info(f"Загружено встроенное расширение: {attr.name}")
                except Exception as e:
                    browser_logger.error(f"Ошибка загрузки встроенного расширения {entry}: {e}")

    def get_builtin_extensions(self):
        return list(self._builtin_extensions.values())

    def get_builtin_instance(self, name):
        return self._builtin_instances.get(name)

    def is_builtin_extension_enabled(self, name: str) -> bool:
        return self.settings.get(f"builtin_extensions.{name}", True)

    def toggle_builtin_extension(self, name: str, enabled: bool):
        self.settings.set(f"builtin_extensions.{name}", enabled)
        self.settings.save_settings()

    def install_all(self, webengine_paths: dict):
        if not self._supports:
            return
        for name, path in webengine_paths.items():
            try:
                ext = self.profile.installExtension(path)
                enabled = self.settings.get(f"extensions_state.{name}", True)
                ext.setEnabled(enabled)
                self._extensions[name] = ext
                browser_logger.info(f"Расширение '{name}' установлено")
            except Exception as e:
                browser_logger.error(f"Ошибка установки расширения '{name}': {e}")

    def add_extension(self, source_path: str) -> bool:
        if not self._supports:
            return False
        name = os.path.basename(source_path.rstrip(os.sep))
        dest = os.path.join(self._ext_dir, name)
        if os.path.exists(dest):
            return False
        try:
            shutil.copytree(source_path, dest)
            if not os.path.isfile(os.path.join(dest, 'manifest.json')):
                shutil.rmtree(dest)
                return False
            ext = self.profile.installExtension(dest)
            self._extensions[name] = ext
            return True
        except Exception as e:
            browser_logger.error(f"Ошибка добавления расширения '{name}': {e}")
            return False

    def remove_extension(self, name: str):
        if name in self._extensions:
            try:
                self._extensions[name].setEnabled(False)
                del self._extensions[name]
                shutil.rmtree(os.path.join(self._ext_dir, name), ignore_errors=True)
                self.settings.save_settings()
            except Exception as e:
                browser_logger.error(f"Ошибка удаления расширения '{name}': {e}")

    def toggle_extension(self, name: str, enabled: bool):
        if name in self._extensions:
            self._extensions[name].setEnabled(enabled)
            self.settings.set(f"extensions_state.{name}", enabled)
            self.settings.save_settings()

    def is_enabled(self, name: str) -> bool:
        return self.settings.get(f"extensions_state.{name}", True)

    def get_installed_names(self):
        return list(self._extensions.keys())