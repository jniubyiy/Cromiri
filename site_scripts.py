import re
from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineScript
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
        return SiteScript(
            d["name"],
            d.get("description", ""),
            d["pattern"],
            d["code"],
            d.get("enabled", True)
        )

class SiteScriptManager:
    def __init__(self, settings: 'SettingsManager'):
        self.settings = settings
        self.scripts: list[SiteScript] = []
        self._load()

    def _load(self):
        raw = self.settings.get("site_scripts", [])
        self.scripts = [SiteScript.from_dict(item) for item in raw]
        browser_logger.info(f"Загружено {len(self.scripts)} пользовательских скриптов")

    def _save(self):
        self.settings.set("site_scripts", [s.to_dict() for s in self.scripts])
        self.settings.save()
        browser_logger.info("Список скриптов сохранён")

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
        browser_logger.debug(f"Попытка инжекции скриптов на {url_str}")
        if url.scheme() in ("about", "chrome", "file"):
            browser_logger.debug(f"Пропуск инжекции для схемы {url.scheme()}")
            return

        for script in self.scripts:
            if not script.enabled:
                continue
            matched = self._match_pattern(script.pattern, url_str)
            browser_logger.debug(f"Проверка шаблона '{script.pattern}' для '{url_str}': {matched}")
            if matched:
                try:
                    # Добавляем отладочный вывод, чтобы убедиться, что код исполняется
                    debug_code = f"console.log('Cromiri: скрипт \"{script.name}\" выполняется');\n" + script.code
                    view.page().runJavaScript(debug_code, lambda result: self._on_script_result(script.name, result))
                    browser_logger.info(f"Скрипт '{script.name}' внедрён на {url_str}")
                except Exception as e:
                    browser_logger.error(f"Ошибка выполнения скрипта '{script.name}': {e}")

    def _on_script_result(self, name, result):
        # Ничего не делаем, просто для отладки
        pass

    def _match_pattern(self, pattern: str, url: str) -> bool:
        # Если шаблон заключён в /.../, это регулярное выражение
        if len(pattern) > 1 and pattern.startswith('/') and pattern.endswith('/'):
            try:
                regex = pattern[1:-1]
                res = re.search(regex, url) is not None
                browser_logger.debug(f"Regex '{regex}' для '{url}': {res}")
                return res
            except re.error as e:
                browser_logger.error(f"Некорректное регулярное выражение в шаблоне '{pattern}': {e}")
                return False
        else:
            # Превращаем glob-шаблон в регулярное выражение
            escaped = re.escape(pattern).replace(r'\*', '.*')
            res = re.fullmatch(escaped, url) is not None
            browser_logger.debug(f"Glob '{escaped}' для '{url}': {res}")
            return res