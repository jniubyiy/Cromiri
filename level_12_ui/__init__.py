# level_12_ui/__init__.py

from level_0.level_base import LevelWrapper, LevelCore
from .box_main_tabs.main_tabs import MainTabsBox
from .box_toolbar.toolbar import ToolbarBox
from .box_tabs.tabs import TabsBox
from .box_settings_tab.settings_tab import SettingsTabBox
from .box_scripts_tab.scripts_tab import ScriptsTabBox
from .box_style.style_box import StyleBox
from .box_window.window import WindowBox
from .box_history_tab.history_tab import HistoryTabBox
from .box_bookmarks_tab.bookmarks_tab import BookmarksTabBox
from .box_context_menu.context_menu import ContextMenuBox
from .box_navigation.navigation import NavigationBox
from .box_webview.webview import WebViewBox

DEPS = ["UserLevel", "SessionLevel", "ExtensionsLevel", "ScriptLevel"]
WRAPPER_CLASS = "UILevelWrapper"   # ← обязательно!

class UILevelCore(LevelCore):
    def __init__(self, user_wrapper, session_wrapper, extensions_wrapper, script_wrapper):
        super().__init__("UILevel")
        self._user = user_wrapper
        self._session = session_wrapper
        self._extensions = extensions_wrapper
        self._script = script_wrapper

    def setup_boxes(self):
        # 1. StyleBox
        style_box = StyleBox(self._user)
        style_wrapper = self.register_box(style_box)
        style_wrapper.expose_methods("apply", "add", "clear_all")

        # 2. ContextMenuBox
        context_menu_box = ContextMenuBox(self._user)
        context_menu_wrapper = self.register_box(context_menu_box)
        context_menu_wrapper.expose_methods("setup_view", "set_new_tab_callback")

        # 3. NavigationBox
        navigation_box = NavigationBox()
        navigation_wrapper = self.register_box(navigation_box)
        navigation_wrapper.expose_methods("setup_loader", "load_url", "back", "forward", "reload")

        # 4. TabsBox
        tabs_box = TabsBox(
            self._user, self._session, style_wrapper, self._script,
            self._extensions, navigation_wrapper, context_menu_wrapper
        )
        tabs_wrapper = self.register_box(tabs_box)
        tabs_wrapper.expose_methods(
            "set_stack", "set_toggle_main_callback", "create_widget", "add_new_page_tab",
            "active_loader", "restore_session", "save_session", "on_tab_changed",
            "on_url_changed", "close_tab", "set_toolbar", "retranslate_ui", "apply_settings",
            "set_profile"
        )

        # 5. WebViewBox
        webview_box = WebViewBox(tabs_wrapper, navigation_wrapper)
        webview_wrapper = self.register_box(webview_box)
        webview_wrapper.expose_methods("get_active_view", "get_current_url", "load_url", "back", "forward", "reload")

        # 6. ToolbarBox
        toolbar_box = ToolbarBox(webview_wrapper, self._user, self._session)
        toolbar_wrapper = self.register_box(toolbar_box)
        toolbar_wrapper.expose_methods(
            "create_widget", "update_extension_icons", "update_for_view",
            "update_address_bar", "retranslate_ui"
        )

        # 7. MainTabsBox
        main_tabs_box = MainTabsBox(self._user)
        main_tabs_wrapper = self.register_box(main_tabs_box)
        main_tabs_wrapper.expose_methods(
            "create_widget", "show_panel", "hide_panel", "get_tab_bar", "retranslate_ui"
        )

        # 8. SettingsTabBox
        settings_tab_box = SettingsTabBox(self._user, self._extensions, self._session)
        settings_tab_wrapper = self.register_box(settings_tab_box)
        settings_tab_wrapper.expose_methods(
            "create_widget", "refresh_all", "refresh_extensions_list", "get_settings",
            "set_user_changed_callback", "retranslate_ui", "set_settings_saved_callback"
        )

        # 9. ScriptsTabBox
        scripts_tab_box = ScriptsTabBox(self._user, self._session, self._script)
        scripts_tab_wrapper = self.register_box(scripts_tab_box)
        scripts_tab_wrapper.expose_methods("create_widget", "refresh_scripts_list", "retranslate_ui")

        # 10. HistoryTabBox
        history_tab_box = HistoryTabBox(self._session, self._user)
        history_tab_wrapper = self.register_box(history_tab_box)
        history_tab_wrapper.expose_methods("create_widget", "refresh", "retranslate_ui")

        # 11. BookmarksTabBox
        bookmarks_tab_box = BookmarksTabBox(self._session, self._user)
        bookmarks_tab_wrapper = self.register_box(bookmarks_tab_box)
        bookmarks_tab_wrapper.expose_methods("create_widget", "refresh", "set_open_url_callback", "retranslate_ui")

        # 12. WindowBox
        window_box = WindowBox(
            {
                "main_tabs": main_tabs_box,
                "toolbar": toolbar_box,
                "tabs": tabs_box,
                "settings_tab": settings_tab_box,
                "scripts_tab": scripts_tab_box,
                "style": style_box,
                "history_tab": history_tab_box,
                "bookmarks_tab": bookmarks_tab_box,
                "context_menu": context_menu_box,
                "navigation": navigation_box,
                "webview": webview_box
            },
            {**self._box_wrappers, "extensions": self._extensions},
            self._user,
            self._session
        )
        window_wrapper = self.register_box(window_box)
        window_wrapper.expose_methods("build", "retranslate_ui", "reload_settings")

    def get_main_window(self):
        return self.send_to_box("window", "build")


class UILevelWrapper(LevelWrapper):
    def __init__(self, user_wrapper, session_wrapper, extensions_wrapper, script_wrapper):
        core = UILevelCore(user_wrapper, session_wrapper, extensions_wrapper, script_wrapper)
        super().__init__(core)
        core.setup_boxes()
        self.register_public_api("get_main_window")
        self.allow_request_from("*", [
            "apply", "add", "clear_all",
            "setup_view", "set_new_tab_callback",
            "setup_loader", "load_url", "back", "forward", "reload",
            "set_stack", "set_toggle_main_callback", "create_widget", "add_new_page_tab",
            "active_loader", "restore_session", "save_session", "on_tab_changed",
            "on_url_changed", "close_tab",
            "get_active_view", "get_current_url",
            "update_extension_icons", "update_for_view", "update_address_bar",
            "show_panel", "hide_panel", "get_tab_bar", "refresh_all", "refresh_extensions_list",
            "get_settings", "refresh_scripts_list", "build", "set_toolbar", "set_user_changed_callback",
            "retranslate_ui", "apply_settings", "set_settings_saved_callback", "reload_settings",
            "refresh", "record_visit", "record_action", "record_download", "record_settings_change",
            "set_open_url_callback", "set_profile"
        ])

    def initialize(self):
        pass