# style_manager.py
from PyQt6.QtWebEngineCore import QWebEngineScript
from logger import browser_logger

class StyleManager:
    def __init__(self, settings: 'SettingsManager'):
        self.settings = settings
        self.script_name = "user_styles"

    def apply_styles(self, view):
        """
        Внедряет пользовательские CSS-стили через JavaScript.
        """
        styles = self.settings.get("custom_styles", [])
        css = "\n".join(styles)

        scripts_collection = view.page().scripts()
        existing_script = self._find_script_by_name(scripts_collection, self.script_name)
        if existing_script:
            scripts_collection.remove(existing_script)

        if css:
            js_code = f"""
                (function() {{
                    var style = document.createElement('style');
                    style.id = 'user_styles_injected';
                    style.textContent = `{css}`;
                    document.head.appendChild(style);
                }})();
            """
            script = QWebEngineScript()
            script.setName(self.script_name)
            script.setSourceCode(js_code)
            script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentReady)
            script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
            script.setRunsOnSubFrames(True)
            scripts_collection.insert(script)
            browser_logger.debug("Пользовательские стили применены")

    def add_style(self, css_text: str):
        styles = self.settings.get("custom_styles", [])
        styles.append(css_text)
        self.settings.set("custom_styles", styles)
        self.settings.save()
        browser_logger.info("Добавлен новый пользовательский стиль")

    def clear_styles(self):
        self.settings.set("custom_styles", [])
        self.settings.save()
        browser_logger.info("Все пользовательские стили удалены")

    def _find_script_by_name(self, collection, name):
        for script in collection.toList():
            if script.name() == name:
                return script
        return None