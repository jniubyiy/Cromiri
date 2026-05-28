from PyQt6.QtWebEngineCore import QWebEngineScript
from level_0.level_base import Box
from logger import browser_logger

class StyleBox(Box):
    def __init__(self, settings):
        super().__init__("style")
        self.settings = settings
        self.script_name = "user_styles"

    def apply(self, view):
        """Применяет все активные пользовательские стили к указанному view."""
        styles = self.settings.get("custom_styles", [])
        css = "\n".join(styles)
        scripts_collection = view.page().scripts()
        existing = self._find_script(scripts_collection, self.script_name)
        if existing:
            scripts_collection.remove(existing)
        if css:
            js = f"""
            (function() {{
                var style = document.createElement('style');
                style.id = 'user_styles_injected';
                style.textContent = `{css}`;
                document.head.appendChild(style);
            }})();
            """
            script = QWebEngineScript()
            script.setName(self.script_name)
            script.setSourceCode(js)
            script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentReady)
            script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
            script.setRunsOnSubFrames(True)
            scripts_collection.insert(script)
            browser_logger.debug("Пользовательские стили применены")

    def add(self, css_text: str):
        styles = self.settings.get("custom_styles", [])
        styles.append(css_text)
        self.settings.set("custom_styles", styles)
        self.settings.save()
        browser_logger.info("Добавлен новый пользовательский стиль")

    def clear_all(self):
        self.settings.set("custom_styles", [])
        self.settings.save()
        browser_logger.info("Все пользовательские стили удалены")

    def _find_script(self, collection, name):
        for script in collection.toList():
            if script.name() == name:
                return script
        return None