from level_0.level_base import LevelWrapper, LevelCore, Box
from .box_main_tabs.main_tabs import MainTabsBox
from .box_toolbar.toolbar import ToolbarBox
from .box_tabs.tabs import TabsBox
from .box_settings_tab.settings_tab import SettingsTabBox
from .box_scripts_tab.scripts_tab import ScriptsTabBox
from .box_style_script.style_script import StyleScriptBox
from .box_window.window import WindowBox
from .box_history_tab.history_tab import HistoryTabBox
from .box_bookmarks_tab.bookmarks_tab import BookmarksTabBox
from .box_context_menu.context_menu import ContextMenuBox

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
        style_script_wrapper.expose_methods(
            "apply_styles", "inject_scripts", "add_style", "clear_styles",
            "get_scripts", "add_script", "remove_script", "toggle_script", "update_script"
        )

        # 2. ContextMenuBox
        context_menu_box = ContextMenuBox(self._settings)
        context_menu_wrapper = self.register_box(context_menu_box)
        context_menu_wrapper.expose_methods("setup_view", "set_new_tab_callback")

        # 3. TabsBox
        tabs_box = TabsBox(
            self._settings, self._session, style_script_wrapper,
            self._extensions, context_menu_wrapper
        )
        tabs_wrapper = self.register_box(tabs_box)
        tabs_wrapper.expose_methods(
            "set_stack", "set_toggle_main_callback", "create_widget", "add_new_page_tab",
            "active_loader", "restore_session", "save_session", "on_tab_changed",
            "on_url_changed", "close_tab", "set_toolbar", "retranslate_ui", "apply_settings",
            "set_profile"
        )

        # 4. ToolbarBox
        toolbar_box = ToolbarBox(tabs_wrapper, self._settings, self._session)
        toolbar_wrapper = self.register_box(toolbar_box)
        toolbar_wrapper.expose_methods(
            "create_widget", "update_extension_icons", "update_for_view",
            "update_address_bar", "retranslate_ui"
        )

        # 5. MainTabsBox (5 вкладок)
        main_tabs_box = MainTabsBox(self._settings)
        main_tabs_wrapper = self.register_box(main_tabs_box)
        main_tabs_wrapper.expose_methods(
            "create_widget", "show_panel", "hide_panel", "get_tab_bar", "retranslate_ui"
        )

        # 6. SettingsTabBox
        settings_tab_box = SettingsTabBox(self._settings, self._extensions, self._session)
        settings_tab_wrapper = self.register_box(settings_tab_box)
        settings_tab_wrapper.expose_methods(
            "create_widget", "refresh_all", "refresh_extensions_list", "get_settings",
            "set_user_changed_callback", "retranslate_ui", "set_settings_saved_callback"
        )

        # 7. ScriptsTabBox
        scripts_tab_box = ScriptsTabBox(self._settings, self._session, style_script_box.script_manager)
        scripts_tab_wrapper = self.register_box(scripts_tab_box)
        scripts_tab_wrapper.expose_methods("create_widget", "refresh_scripts_list", "retranslate_ui")

        # 8. HistoryTabBox
        history_tab_box = HistoryTabBox(self._session, self._settings)
        history_tab_wrapper = self.register_box(history_tab_box)
        history_tab_wrapper.expose_methods("create_widget", "refresh", "retranslate_ui")

        # 9. BookmarksTabBox
        bookmarks_tab_box = BookmarksTabBox(self._session, self._settings)
        bookmarks_tab_wrapper = self.register_box(bookmarks_tab_box)
        bookmarks_tab_wrapper.expose_methods("create_widget", "refresh", "set_open_url_callback", "retranslate_ui")

        # 10. WindowBox
        window_box = WindowBox(
            {
                "main_tabs": main_tabs_box,
                "toolbar": toolbar_box,
                "tabs": tabs_box,
                "settings_tab": settings_tab_box,
                "scripts_tab": scripts_tab_box,
                "style_script": style_script_box,
                "history_tab": history_tab_box,
                "bookmarks_tab": bookmarks_tab_box,
                "context_menu": context_menu_box
            },
            {**self._box_wrappers, "extensions": self._extensions},
            self._settings,
            self._session
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
            "apply_styles", "inject_scripts", "add_style", "clear_styles", "get_scripts", "add_script",
            "remove_script", "toggle_script", "update_script",
            "set_stack", "set_toggle_main_callback", "create_widget", "add_new_page_tab",
            "active_loader", "restore_session", "save_session", "on_tab_changed", "on_url_changed",
            "close_tab", "update_extension_icons", "update_for_view", "update_address_bar",
            "show_panel", "hide_panel", "get_tab_bar", "refresh_all", "refresh_extensions_list",
            "get_settings", "refresh_scripts_list", "build", "set_toolbar", "set_user_changed_callback",
            "retranslate_ui", "apply_settings", "set_settings_saved_callback", "reload_settings",
            "refresh", "record_visit", "record_action", "record_download", "record_settings_change",
            "set_open_url_callback", "setup_view", "set_new_tab_callback", "set_profile"
        ])

    def initialize(self):
        pass