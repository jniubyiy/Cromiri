from style_manager import StyleManager
from site_scripts import SiteScriptManager
from level_0.level_base import Box
from logger import browser_logger

class StyleScriptBox(Box):
    def __init__(self, settings):
        super().__init__("style_script")
        self.settings = settings
        self.style_manager = StyleManager(settings)
        self.script_manager = SiteScriptManager(settings)

    def apply_styles(self, view):
        self.style_manager.apply_styles(view)

    def inject_scripts(self, view, url):
        self.script_manager.inject_scripts(view, url)

    def add_style(self, css_text):
        self.style_manager.add_style(css_text)

    def clear_styles(self):
        self.style_manager.clear_styles()

    def get_scripts(self):
        return self.script_manager.get_scripts()

    def add_script(self, name, desc, pattern, code):
        self.script_manager.add_script(name, desc, pattern, code)

    def remove_script(self, index):
        self.script_manager.remove_script(index)

    def toggle_script(self, index, enabled):
        self.script_manager.toggle_script(index, enabled)

    def update_script(self, index, name, desc, pattern, code):
        self.script_manager.update_script(index, name, desc, pattern, code)