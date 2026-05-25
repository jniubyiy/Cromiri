from PyQt6.QtCore import QUrl, Qt, QEvent
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QStackedWidget
)
from PyQt6.QtWebEngineCore import QWebEngineProfile
from level_0.level_base import Box, BoxWrapper
from logger import browser_logger

class WindowBox(Box):
    def __init__(self, boxes_raw: dict, box_wrappers: dict):
        super().__init__("window")
        self.boxes_raw = boxes_raw
        self.box_wrappers = box_wrappers

    def build(self) -> QMainWindow:
        return BrowserMainWindow(self.boxes_raw, self.box_wrappers)


class BrowserMainWindow(QMainWindow):
    def __init__(self, boxes_raw: dict, box_wrappers: dict):
        super().__init__()
        self.setWindowTitle("Cromiri")
        self.resize(1280, 800)

        # Извлекаем обёртки (BoxWrapper)
        self.main_tabs = box_wrappers.get("main_tabs")
        self.toolbar = box_wrappers.get("toolbar")
        self.tabs = box_wrappers.get("tabs")
        self.settings_tab = box_wrappers.get("settings_tab")
        self.scripts_tab = box_wrappers.get("scripts_tab")
        self.style_script = box_wrappers.get("style_script")

        # Получаем настройки через публичный метод
        self.settings = self.settings_tab.call("get_settings")

        self.profile = QWebEngineProfile.defaultProfile()
        if self.settings:
            self.profile.setPersistentStoragePath(self.settings.get("profile_path", "browser_data"))
        self.profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)

        # Стек страниц
        self.page_stack = QStackedWidget()
        self.tabs.call("set_stack", self.page_stack)
        self.tabs.call("set_toggle_main_callback", self.toggle_main_tabs)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Главные вкладки
        self.main_tabs_widget = self.main_tabs.call("create_widget", self)
        # Подключаем сигнал через get_tab_bar
        tab_bar = self.main_tabs.call("get_tab_bar")
        tab_bar.currentChanged.connect(self.on_main_tab_changed)
        main_layout.addWidget(self.main_tabs_widget)

        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack, 1)

        # Вкладка "Просмотр"
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

        self.content_stack.addWidget(self.view_tab)        # 0
        self.content_stack.addWidget(self.settings_widget)  # 1
        self.content_stack.addWidget(self.scripts_widget)   # 2

        # Восстановление сессии
        self.tabs.call("restore_session")

        if self.page_stack.count() == 0:
            self.tabs.call("add_new_page_tab", QUrl("about:blank"))

        self._load_extensions()
        self.installEventFilter(self)
        self.main_tabs_visible = True

    def on_main_tab_changed(self, index):
        self.content_stack.setCurrentIndex(index)
        if index == 1:
            self.settings_tab.call("refresh_all")
        elif index == 2:
            self.scripts_tab.call("refresh_scripts_list")

    def toggle_main_tabs(self):
        if self.main_tabs_visible:
            self.main_tabs.call("hide_panel")
            self.main_tabs_visible = False
        else:
            self.main_tabs.call("show_panel")
            self.main_tabs_visible = True

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_F11:
                self.showNormal() if self.isFullScreen() else self.showFullScreen()
                return True
            elif event.key() == Qt.Key.Key_F5:
                loader = self.tabs.call("active_loader")
                if loader:
                    loader.reload()
                return True
        return super().eventFilter(obj, event)

    def _load_extensions(self):
        # Пока заглушка
        pass

    def closeEvent(self, event):
        self.tabs.call("save_session")
        event.accept()