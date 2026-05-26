import json
import os
from level_0.level_base import Box
from logger import browser_logger

class LocaleBox(Box):
    def __init__(self):
        super().__init__("locale")
        self.translations = {}
        self.current_lang = "ru"
        self._locales_dir = os.path.join(os.path.dirname(__file__), "..", "..", "locales")

    def load_language(self, lang):
        self.current_lang = lang
        self.translations = {}
        filepath = os.path.join(self._locales_dir, f"{lang}.json")
        if os.path.isfile(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.translations = json.load(f)
            except Exception as e:
                browser_logger.error(f"Ошибка загрузки локализации {lang}: {e}")
                # fallback к русскому
                self.load_language("ru")
        else:
            browser_logger.warning(f"Файл локализации {lang}.json не найден, использую русский по умолчанию.")
            if lang != "ru":
                self.load_language("ru")

    def tr(self, key, default=None):
        return self.translations.get(key, default if default is not None else key)

    def available_languages(self):
        langs = []
        if os.path.isdir(self._locales_dir):
            for file in os.listdir(self._locales_dir):
                if file.endswith(".json"):
                    langs.append(file[:-5])
        return sorted(langs)

    def get_current_lang(self):
        return self.current_lang