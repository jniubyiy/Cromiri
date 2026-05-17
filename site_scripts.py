# site_scripts.py
import re
from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from logger import browser_logger

class SiteScript:
    def __init__(self, name: str, description: str, pattern: str, code: str, enabled: bool = True):
        self.name = name
        self.description = description
        self.pattern = pattern
        self.code = code
        self.enabled = enabled

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "pattern": self.pattern,
            "code": self.code,
            "enabled": self.enabled
        }

    @staticmethod
    def from_dict(d):
        return SiteScript(d["name"], d.get("description", ""), d["pattern"], d["code"], d.get("enabled", True))


class SiteScriptManager:
    def __init__(self, settings: 'SettingsManager'):
        self.settings = settings
        self.scripts: list[SiteScript] = []
        self._load()

    def _load(self):
        raw = self.settings.get("site_scripts", [])
        self.scripts = [SiteScript.from_dict(item) for item in raw]

    def _save(self):
        self.settings.set("site_scripts", [s.to_dict() for s in self.scripts])
        self.settings.save()

    def add_script(self, name: str, description: str, pattern: str, code: str):
        script = SiteScript(name, description, pattern, code, True)
        self.scripts.append(script)
        self._save()
        browser_logger.info(f"Добавлен скрипт '{name}' с шаблоном '{pattern}'")

    def remove_script(self, index: int):
        if 0 <= index < len(self.scripts):
            name = self.scripts[index].name
            del self.scripts[index]
            self._save()
            browser_logger.info(f"Удалён скрипт '{name}'")

    def toggle_script(self, index: int, enabled: bool):
        if 0 <= index < len(self.scripts):
            self.scripts[index].enabled = enabled
            self._save()
            browser_logger.info(f"Скрипт '{self.scripts[index].name}' {'включён' if enabled else 'отключён'}")

    def update_script(self, index: int, name: str, description: str, pattern: str, code: str):
        if 0 <= index < len(self.scripts):
            s = self.scripts[index]
            s.name = name
            s.description = description
            s.pattern = pattern
            s.code = code
            self._save()
            browser_logger.info(f"Скрипт '{name}' обновлён")

    def get_scripts(self):
        return self.scripts

    def inject_scripts(self, view: QWebEngineView, url: QUrl):
        url_str = url.toString()
        for script in self.scripts:
            if not script.enabled:
                continue
            if self._match_pattern(script.pattern, url_str):
                try:
                    view.page().runJavaScript(script.code)
                    browser_logger.debug(f"Скрипт '{script.name}' внедрён на {url_str}")
                except Exception as e:
                    browser_logger.error(f"Ошибка выполнения скрипта '{script.name}': {e}")

    def _match_pattern(self, pattern: str, url: str) -> bool:
        if pattern.startswith('/') and pattern.endswith('/'):
            try:
                regex = pattern[1:-1]
                return re.search(regex, url) is not None
            except re.error:
                browser_logger.error(f"Некорректное регулярное выражение в шаблоне '{pattern}'")
                return False
        else:
            escaped = re.escape(pattern).replace(r'\*', '.*')
            return re.fullmatch(escaped, url) is not None