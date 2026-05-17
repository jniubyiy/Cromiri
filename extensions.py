# extensions.py
import os
import shutil
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QStyle
from logger import browser_logger

class ExtensionManager:
    def __init__(self, profile, settings, extensions_dir: str):
        self.profile = profile
        self.settings = settings
        self.extensions_dir = extensions_dir
        os.makedirs(self.extensions_dir, exist_ok=True)
        self._extensions = {}
        self._supports_extensions = hasattr(profile, 'installExtension')
        if not self._supports_extensions:
            browser_logger.warning("Ваша версия PyQt6 WebEngine не поддерживает установку расширений. Расширения будут отключены.")

    def install_all(self):
        if not self._supports_extensions:
            return
        for name, path in self._scan_dirs():
            if name in self._extensions:
                continue
            try:
                ext = self.profile.installExtension(path)
                enabled = self.settings.get(f"extensions_state.{name}", True)
                ext.setEnabled(enabled)
                self._extensions[name] = ext
                browser_logger.info(f"Расширение '{name}' успешно установлено (включено={enabled})")
            except Exception as e:
                browser_logger.error(f"Ошибка установки расширения '{name}': {e}")
        self._save_state()

    def add_extension(self, source_path: str) -> bool:
        if not self._supports_extensions:
            browser_logger.warning("Попытка добавить расширение, но они не поддерживаются")
            return False
        name = os.path.basename(source_path.rstrip(os.sep))
        dest = os.path.join(self.extensions_dir, name)
        if os.path.exists(dest):
            browser_logger.warning(f"Расширение '{name}' уже существует")
            return False
        try:
            shutil.copytree(source_path, dest)
            if not os.path.isfile(os.path.join(dest, 'manifest.json')):
                shutil.rmtree(dest)
                browser_logger.warning(f"Папка '{source_path}' не содержит manifest.json")
                return False
            ext = self.profile.installExtension(dest)
            enabled = self.settings.get(f"extensions_state.{name}", True)
            ext.setEnabled(enabled)
            self._extensions[name] = ext
            self._save_state()
            browser_logger.info(f"Расширение '{name}' добавлено и включено")
            return True
        except Exception as e:
            browser_logger.error(f"Ошибка добавления расширения '{name}': {e}")
            return False

    def remove_extension(self, name: str):
        if not self._supports_extensions or name not in self._extensions:
            return
        try:
            self._extensions[name].setEnabled(False)
            del self._extensions[name]
            path = os.path.join(self.extensions_dir, name)
            if os.path.exists(path):
                shutil.rmtree(path)
            # Удаляем ключ из extensions_state
            ext_state = self.settings.data.get("extensions_state", {})
            if name in ext_state:
                del ext_state[name]
            self.settings.save()
            browser_logger.info(f"Расширение '{name}' удалено")
        except Exception as e:
            browser_logger.error(f"Ошибка удаления расширения '{name}': {e}")

    def toggle_extension(self, name: str, enabled: bool):
        if not self._supports_extensions:
            return
        if name in self._extensions:
            self._extensions[name].setEnabled(enabled)
            self.settings.set(f"extensions_state.{name}", enabled)
            self.settings.save()
            browser_logger.info(f"Расширение '{name}' {'включено' if enabled else 'отключено'}")

    def is_enabled(self, name: str) -> bool:
        return self.settings.get(f"extensions_state.{name}", True)

    def get_installed_names(self):
        return list(self._extensions.keys())

    def get_icon(self, name: str) -> QIcon:
        base = os.path.join(self.extensions_dir, name)
        for fname in ('icon16.png', 'icon48.png', 'icon128.png'):
            path = os.path.join(base, fname)
            if os.path.isfile(path):
                return QIcon(path)
        try:
            for f in os.listdir(base):
                if f.endswith('.png'):
                    return QIcon(os.path.join(base, f))
        except Exception:
            pass
        return QApplication.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)

    def _scan_dirs(self):
        dirs = []
        if not os.path.isdir(self.extensions_dir):
            return dirs
        for name in os.listdir(self.extensions_dir):
            path = os.path.join(self.extensions_dir, name)
            if os.path.isdir(path) and os.path.isfile(os.path.join(path, 'manifest.json')):
                dirs.append((name, path))
        return dirs

    def _save_state(self):
        if self._supports_extensions:
            for name in self._extensions:
                self.settings.set(f"extensions_state.{name}", self.is_enabled(name))
            self.settings.save()