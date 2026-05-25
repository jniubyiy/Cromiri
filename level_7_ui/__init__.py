from level_0.level_base import LevelWrapper, LevelCore, Box
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
        # Создаём объекты боксов
        style_script_box = StyleScriptBox(self._settings)
        tabs_box = TabsBox(self._settings, self._session, style_script_box)
        toolbar_box = ToolbarBox(tabs_box)
        main_tabs_box = MainTabsBox()
        settings_tab_box = SettingsTabBox(self._settings, self._extensions)
        scripts_tab_box = ScriptsTabBox(self._settings, self._session, style_script_box.script_manager)

        # Регистрируем обёртки (получаем BoxWrapper)
        style_script_wrapper = self.register_box(style_script_box)
        tabs_wrapper = self.register_box(tabs_box)
        toolbar_wrapper = self.register_box(toolbar_box)
        main_tabs_wrapper = self.register_box(main_tabs_box)
        settings_tab_wrapper = self.register_box(settings_tab_box)
        scripts_tab_wrapper = self.register_box(scripts_tab_box)

        # Настраиваем публичные методы обёрток
        style_script_wrapper.expose_methods("apply_styles", "inject_scripts", "add_style", "clear_styles",
                                            "get_scripts", "add_script", "remove_script", "toggle_script", "update_script")
        tabs_wrapper.expose_methods("set_stack", "set_toggle_main_callback", "create_widget",
                                    "add_new_page_tab", "active_loader", "restore_session", "save_session",
                                    "on_tab_changed", "on_url_changed", "close_tab")
        toolbar_wrapper.expose_methods("create_widget", "update_extension_icons", "update_for_view", "update_address_bar")
        main_tabs_wrapper.expose_methods("create_widget", "show_panel", "hide_panel", "get_tab_bar")
        settings_tab_wrapper.expose_methods("create_widget", "refresh_all", "refresh_extensions_list", "get_settings")
        scripts_tab_wrapper.expose_methods("create_widget", "refresh_scripts_list")

        # WindowBox получает словари: сырые объекты и обёртки (обёртки для UI)
        window_box = WindowBox(
            {"main_tabs": main_tabs_box, "toolbar": toolbar_box, "tabs": tabs_box,
             "settings_tab": settings_tab_box, "scripts_tab": scripts_tab_box, "style_script": style_script_box},
            self._box_wrappers
        )
        window_wrapper = self.register_box(window_box)
        window_wrapper.expose_methods("build")

    def get_main_window(self):
        return self.send_to_box("window", "build")

class UILevelWrapper(LevelWrapper):
    def __init__(self, settings_wrapper, session_wrapper, extensions_wrapper):
        core = UILevelCore(settings_wrapper, session_wrapper, extensions_wrapper)
        super().__init__(core)
        core.setup_boxes()
        self.register_public_api("get_main_window")
        self.allow_request_from("*", [
            "apply_styles", "inject_scripts", "add_style", "clear_styles",
            "get_scripts", "add_script", "remove_script", "toggle_script", "update_script",
            "set_stack", "set_toggle_main_callback", "create_widget",
            "add_new_page_tab", "active_loader", "restore_session", "save_session",
            "on_tab_changed", "on_url_changed", "close_tab",
            "create_widget", "update_extension_icons", "update_for_view", "update_address_bar",
            "create_widget", "show_panel", "hide_panel", "get_tab_bar",
            "create_widget", "refresh_all", "refresh_extensions_list", "get_settings",
            "build"
        ])
    def initialize(self):
        pass