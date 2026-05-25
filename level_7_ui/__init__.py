from level_0.level_base import LevelWrapper, LevelCore
from .box_main_tabs.main_tabs import MainTabsBox
from .box_toolbar.toolbar import ToolbarBox
from .box_tabs.tabs import TabsBox
from .box_settings_tab.settings_tab import SettingsTabBox
from .box_scripts_tab.scripts_tab import ScriptsTabBox
from .box_style_script.style_script import StyleScriptBox
from .box_window.window import WindowBox

class UILevelCore(LevelCore):
    def __init__(self, settings_wrapper, session_wrapper, extensions_wrapper):
        super().__init__("UILevel")
        self._settings = settings_wrapper
        self._session = session_wrapper
        self._extensions = extensions_wrapper
    def setup_boxes(self):
        style_script = StyleScriptBox(self._settings)
        self.register_box("style_script", style_script)

        tabs = TabsBox(self._settings, self._session, style_script)
        self.register_box("tabs", tabs)

        toolbar = ToolbarBox(tabs)
        self.register_box("toolbar", toolbar)

        main_tabs = MainTabsBox()
        self.register_box("main_tabs", main_tabs)

        settings_tab = SettingsTabBox(self._settings, self._extensions)
        self.register_box("settings_tab", settings_tab)

        scripts_tab = ScriptsTabBox(self._settings, self._session, style_script.script_manager)
        self.register_box("scripts_tab", scripts_tab)

        window = WindowBox(self._boxes)
        self.register_box("window", window)

    def get_main_window(self):
        return self.get_box("window").build()

class UILevelWrapper(LevelWrapper):
    def __init__(self, settings_wrapper, session_wrapper, extensions_wrapper):
        core = UILevelCore(settings_wrapper, session_wrapper, extensions_wrapper)
        super().__init__(core)
        core.setup_boxes()
        self.register_external_api(["get_main_window"])
    def initialize(self):
        pass