import re
from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from level_0.level_base import Box
from logger import browser_logger

class ScriptBox(Box):
    def __init__(self, settings):
        super().__init__("script")
        self.settings = settings
        self.scripts = []
        self._load()

    def _load(self):
        raw = self.settings.get("site_scripts", [])
        self.scripts = raw
        browser_logger.info(f"Загружено {len(self.scripts)} пользовательских скриптов")

    def _save(self):
        self.settings.set("site_scripts", self.scripts)
        self.settings.save()

    def add(self, name: str, description: str, pattern: str, code: str):
        script = {
            "name": name, "description": description,
            "pattern": pattern, "code": code, "enabled": True
        }
        self.scripts.append(script)
        self._save()
        browser_logger.info(f"Добавлен скрипт '{name}'")

    def remove(self, index: int):
        if 0 <= index < len(self.scripts):
            name = self.scripts[index]["name"]
            del self.scripts[index]
            self._save()
            browser_logger.info(f"Удалён скрипт '{name}'")

    def toggle(self, index: int, enabled: bool):
        if 0 <= index < len(self.scripts):
            self.scripts[index]["enabled"] = enabled
            self._save()

    def update(self, index: int, name: str, description: str, pattern: str, code: str):
        if 0 <= index < len(self.scripts):
            s = self.scripts[index]
            s["name"] = name
            s["description"] = description
            s["pattern"] = pattern
            s["code"] = code
            self._save()

    def get_all(self):
        return self.scripts

    def inject(self, view: QWebEngineView, url: QUrl):
        url_str = url.toString()
        if url.scheme() in ("about", "chrome", "file"):
            return
        for script in self.scripts:
            if not script.get("enabled", True):
                continue
            if self._match(script["pattern"], url_str):
                try:
                    debug_code = f"console.log('Скрипт \"{script['name']}\" выполняется');\n{script['code']}"
                    view.page().runJavaScript(debug_code)
                    browser_logger.info(f"Скрипт '{script['name']}' внедрён на {url_str}")
                except Exception as e:
                    browser_logger.error(f"Ошибка скрипта '{script['name']}': {e}")

    def _match(self, pattern: str, url: str) -> bool:
        if len(pattern) > 1 and pattern.startswith('/') and pattern.endswith('/'):
            try:
                return re.search(pattern[1:-1], url) is not None
            except re.error:
                return False
        escaped = re.escape(pattern).replace(r'\*', '.*')
        return re.fullmatch(escaped, url) is not None