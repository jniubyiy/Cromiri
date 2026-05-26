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
        # 1. StyleScriptBox
        style_script_box = StyleScriptBox(self._settings)
        style_script_wrapper = self.register_box(style_script_box)
        style_script_wrapper.expose_methods("apply_styles", "inject_scripts",
                                            "add_style", "clear_styles",
                                            "get_scripts", "add_script",
                                            "remove_script", "toggle_script",
                                            "update_script")

        # 2. TabsBox (передаём обёртку style_script и extensions_wrapper)
        tabs_box = TabsBox(self._settings, self._session, style_script_wrapper, self._extensions)
        tabs_wrapper = self.register_box(tabs_box)
        tabs_wrapper.expose_methods("set_stack", "set_toggle_main_callback",
                                    "create_widget", "add_new_page_tab",
                                    "active_loader", "restore_session",
                                    "save_session", "on_tab_changed",
                                    "on_url_changed", "close_tab",
                                    "set_toolbar", "retranslate_ui",
                                    "apply_settings")

        # 3. ToolbarBox (передаём обёртку tabs)
        toolbar_box = ToolbarBox(tabs_wrapper, self._settings)
        toolbar_wrapper = self.register_box(toolbar_box)
        toolbar_wrapper.expose_methods("create_widget", "update_extension_icons",
                                       "update_for_view", "update_address_bar",
                                       "retranslate_ui")

        # 4. MainTabsBox
        main_tabs_box = MainTabsBox(self._settings)
        main_tabs_wrapper = self.register_box(main_tabs_box)
        main_tabs_wrapper.expose_methods("create_widget", "show_panel",
                                         "hide_panel", "get_tab_bar",
                                         "retranslate_ui")

        # 5. SettingsTabBox
        settings_tab_box = SettingsTabBox(self._settings, self._extensions)
        settings_tab_wrapper = self.register_box(settings_tab_box)
        settings_tab_wrapper.expose_methods("create_widget", "refresh_all",
                                            "refresh_extensions_list", "get_settings",
                                            "set_user_changed_callback", "retranslate_ui",
                                            "set_settings_saved_callback")

        # 6. ScriptsTabBox
        scripts_tab_box = ScriptsTabBox(self._settings, self._session, style_script_box.script_manager)
        scripts_tab_wrapper = self.register_box(scripts_tab_box)
        scripts_tab_wrapper.expose_methods("create_widget", "refresh_scripts_list",
                                           "retranslate_ui")

        # 7. WindowBox (добавляем обёртку расширений в box_wrappers)
        window_box = WindowBox(
            {"main_tabs": main_tabs_box, "toolbar": toolbar_box,
             "tabs": tabs_box, "settings_tab": settings_tab_box,
             "scripts_tab": scripts_tab_box, "style_script": style_script_box},
            {**self._box_wrappers, "extensions": self._extensions},
            self._settings
        )
        window_wrapper = self.register_box(window_box)
        window_wrapper.expose_methods("build", "retranslate_ui", "reload_settings")

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
            "get_scripts", "add_script", "remove_script", "toggle_script",
            "update_script", "set_stack", "set_toggle_main_callback",
            "create_widget", "add_new_page_tab", "active_loader",
            "restore_session", "save_session", "on_tab_changed",
            "on_url_changed", "close_tab", "update_extension_icons",
            "update_for_view", "update_address_bar", "show_panel",
            "hide_panel", "get_tab_bar", "refresh_all",
            "refresh_extensions_list", "get_settings",
            "refresh_scripts_list", "build", "set_toolbar",
            "set_user_changed_callback", "retranslate_ui",
            "apply_settings", "set_settings_saved_callback", "reload_settings"
        ])

    def initialize(self):
        pass