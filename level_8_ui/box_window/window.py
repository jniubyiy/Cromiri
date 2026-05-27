from PyQt6.QtCore import QUrl, Qt, QEvent, QStandardPaths
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QStackedWidget
)
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineDownloadRequest
from level_0.level_base import Box
from logger import browser_logger

class WindowBox(Box):
    def __init__(self, boxes_raw: dict, box_wrappers: dict, settings, session_wrapper):
        super().__init__("window")
        self.boxes_raw = boxes_raw
        self.box_wrappers = box_wrappers
        self.settings = settings
        self.session = session_wrapper

    def build(self) -> QMainWindow:
        return BrowserMainWindow(self.boxes_raw, self.box_wrappers, self.settings, self.session)

class BrowserMainWindow(QMainWindow):
    def __init__(self, boxes_raw: dict, box_wrappers: dict, settings, session_wrapper):
        super().__init__()
        self.settings = settings
        self.session = session_wrapper
        self.setWindowTitle(self.settings.tr("app.title"))
        self.resize(1280, 800)

        self.main_tabs = box_wrappers.get("main_tabs")
        self.toolbar = box_wrappers.get("toolbar")
        self.tabs = box_wrappers.get("tabs")
        self.settings_tab = box_wrappers.get("settings_tab")
        self.scripts_tab = box_wrappers.get("scripts_tab")
        self.style_script = box_wrappers.get("style_script")
        self.history_tab = box_wrappers.get("history_tab")
        self.bookmarks_tab = box_wrappers.get("bookmarks_tab")
        self.context_menu = box_wrappers.get("context_menu")
        self.extensions = box_wrappers.get("extensions")

        # Создаём постоянный профиль для текущего пользователя
        self._setup_profile()
        self.profile.downloadRequested.connect(self.handle_download_request)
        if self.extensions:
            self.extensions.set_profile(self.profile)
        self.tabs.call("set_profile", self.profile)

        self.page_stack = QStackedWidget()
        self.tabs.call("set_stack", self.page_stack)
        self.tabs.call("set_toggle_main_callback", self.toggle_main_tabs)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.main_tabs_widget = self.main_tabs.call("create_widget", self)
        tab_bar = self.main_tabs.call("get_tab_bar")
        tab_bar.currentChanged.connect(self.on_main_tab_changed)
        main_layout.addWidget(self.main_tabs_widget)

        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack, 1)

        self.view_tab = QWidget()
        view_layout = QVBoxLayout()
        view_layout.setContentsMargins(0, 0, 0, 0)
        view_layout.setSpacing(0)
        self.page_tabs_widget = self.tabs.call("create_widget", self)
        view_layout.addWidget(self.page_tabs_widget)
        self.toolbar_widget = self.toolbar.call("create_widget", self)
        view_layout.addWidget(self.toolbar_widget)
        view_layout.addWidget(self.page_stack, 1)
        self.view_tab.setLayout(view_layout)

        self.settings_widget = self.settings_tab.call("create_widget", self)
        self.scripts_widget = self.scripts_tab.call("create_widget", self)
        self.history_widget = self.history_tab.call("create_widget", self)
        self.bookmarks_widget = self.bookmarks_tab.call("create_widget", self)

        self.bookmarks_tab.call("set_open_url_callback", self.open_url_from_bookmark)
        if self.context_menu:
            self.context_menu.call("set_new_tab_callback", self.open_url_from_bookmark)

        self.content_stack.addWidget(self.view_tab)         # 0
        self.content_stack.addWidget(self.history_widget)   # 1
        self.content_stack.addWidget(self.bookmarks_widget) # 2
        self.content_stack.addWidget(self.settings_widget)  # 3
        self.content_stack.addWidget(self.scripts_widget)   # 4

        self.tabs.call("set_toolbar", self.toolbar)
        self.settings_tab.call("set_user_changed_callback", self.on_user_changed)
        self.settings_tab.call("set_settings_saved_callback", self.on_settings_saved)

        self.tabs.call("restore_session")
        if self.page_stack.count() == 0:
            self.tabs.call("add_new_page_tab", QUrl("about:blank"))

        self._load_extensions()
        self.installEventFilter(self)
        self.main_tabs_visible = True

    def _setup_profile(self):
        """Создаёт постоянный профиль QWebEngineProfile для текущего пользователя."""
        user = self.settings.get("users.active", "Default")
        base_path = self.settings.get("profile_path", "browser_data")
        user_path = f"{base_path}/{user}" if base_path else f"browser_data/{user}"

        self.profile = QWebEngineProfile(f"user_{user}")
        self.profile.setPersistentStoragePath(user_path)
        self.profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)
        self.apply_download_settings()
        browser_logger.info(f"Постоянный профиль создан для пользователя '{user}', путь: {user_path}")

    def apply_download_settings(self):
        download_path = self.settings.get("downloads.path", "")
        if not download_path:
            download_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DownloadLocation)
        self.profile.setDownloadPath(download_path)

    def handle_download_request(self, download: QWebEngineDownloadRequest):
        ask_before_save = self.settings.get("downloads.ask_before_save", False)
        if not ask_before_save:
            download.accept()
            self.session.record_download(download.downloadFileName())
            browser_logger.info(f"Загрузка начата: {download.downloadFileName()}")

    def open_url_from_bookmark(self, url: str):
        self.tabs.call("add_new_page_tab", QUrl(url))

    def on_user_changed(self, username):
        """Переключение на другого встроенного пользователя."""
        browser_logger.info(f"Переключение на пользователя {username}")
        self.tabs.call("save_session")

        while self.page_stack.count() > 0:
            widget = self.page_stack.widget(0)
            self.page_stack.removeWidget(widget)
            widget.deleteLater()

        self._setup_profile()
        self.tabs.call("set_profile", self.profile)

        self.tabs.call("restore_session")
        if self.page_stack.count() == 0:
            homepage = self.settings.get("startup.homepage", "about:blank")
            self.tabs.call("add_new_page_tab", QUrl(homepage))

        self.history_tab.call("refresh")
        self.bookmarks_tab.call("refresh")
        browser_logger.info(f"Браузер переключился на профиль '{username}'")

    def on_settings_saved(self):
        browser_logger.info("Применение сохранённых настроек...")
        self.retranslate_ui()
        self.settings_tab.call("refresh_all")
        self.tabs.call("apply_settings")
        self.apply_download_settings()

    def retranslate_ui(self):
        self.setWindowTitle(self.settings.tr("app.title"))
        self.main_tabs.call("retranslate_ui")
        self.toolbar.call("retranslate_ui")
        self.tabs.call("retranslate_ui")
        self.settings_tab.call("retranslate_ui")
        self.scripts_tab.call("retranslate_ui")
        self.history_tab.call("retranslate_ui")
        self.bookmarks_tab.call("retranslate_ui")

    def on_main_tab_changed(self, index):
        self.content_stack.setCurrentIndex(index)
        if index == 0:   # Просмотр
            pass
        elif index == 1: # История
            self.history_tab.call("refresh")
        elif index == 2: # Закладки
            self.bookmarks_tab.call("refresh")
        elif index == 3: # Настройки
            self.settings_tab.call("refresh_all")
        elif index == 4: # Скрипты
            self.scripts_tab.call("refresh_scripts_list")

    def toggle_main_tabs(self):
        if self.main_tabs_visible:
            self.main_tabs.call("hide_panel")
            self.main_tabs_visible = False
            browser_logger.info("Панель главных вкладок скрыта")
        else:
            self.main_tabs.call("show_panel")
            self.main_tabs_visible = True
            browser_logger.info("Панель главных вкладок показана")

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_F11:
                if self.isFullScreen():
                    self.showNormal()
                    self.session.record_action("Клавиша F11: выход из полноэкранного режима")
                    browser_logger.info("Выход из полноэкранного режима")
                else:
                    self.showFullScreen()
                    self.session.record_action("Клавиша F11: полноэкранный режим")
                    browser_logger.info("Переход в полноэкранный режим")
                return True
            elif event.key() == Qt.Key.Key_F5:
                self.session.record_action("Клавиша F5: обновить страницу")
                browser_logger.info("Нажата F5 – обновление страницы")
                loader = self.tabs.call("active_loader")
                if loader:
                    loader.reload()
                return True
        return super().eventFilter(obj, event)

    def _load_extensions(self):
        pass

    def closeEvent(self, event):
        browser_logger.info("Закрытие браузера, сохранение сессии")
        self.tabs.call("save_session")
        event.accept()