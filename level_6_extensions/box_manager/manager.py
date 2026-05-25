import os, shutil
from PyQt6.QtWebEngineCore import QWebEngineProfile
from logger import browser_logger

class ManagerBox:
    def __init__(self, profile: QWebEngineProfile, settings_wrapper):
        self.profile = profile
        self.settings = settings_wrapper
        self._extensions = {}
        self._supports = hasattr(profile, 'installExtension')
        self._ext_dir = os.path.join(os.path.dirname(__file__), "..", "..", "extensions")
        if not self._supports:
            browser_logger.warning("PyQt6 WebEngine не поддерживает установку расширений")
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