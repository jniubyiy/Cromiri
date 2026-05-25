from PyQt6.QtCore import QUrl, Qt, QEvent
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QStackedWidget
)
from PyQt6.QtWebEngineCore import QWebEngineProfile
from logger import browser_logger

class WindowBox:
    def __init__(self, boxes: dict):
        self.boxes = boxes
    def build(self) -> QMainWindow:
        return BrowserMainWindow(self.boxes)

class BrowserMainWindow(QMainWindow):
    def __init__(self, boxes: dict):
        super().__init__()
        self.setWindowTitle("Cromiri")
        self.resize(1280, 800)

        self.boxes = boxes
        self.main_tabs_box = boxes["main_tabs"]
        self.toolbar_box = boxes["toolbar"]
        self.tabs_box = boxes["tabs"]
        self.settings_tab_box = boxes["settings_tab"]
        self.scripts_tab_box = boxes["scripts_tab"]
        self.style_script_box = boxes["style_script"]
        self.settings = self.settings_tab_box.settings

        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.setPersistentStoragePath(self.settings.get("profile_path", "browser_data"))
        self.profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)

        # Внешний стек для страниц
        self.page_stack = QStackedWidget()
        self.tabs_box.set_stack(self.page_stack)
        self.tabs_box.set_toggle_main_callback(self.toggle_main_tabs)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.main_tabs_widget = self.main_tabs_box.create_widget(self)
        main_layout.addWidget(self.main_tabs_widget)
        self.main_tabs_box.tab_bar.currentChanged.connect(self.on_main_tab_changed)

        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack, 1)

        # Вкладка "Просмотр"
        self.view_tab = QWidget()
        view_layout = QVBoxLayout()
        view_layout.setContentsMargins(0, 0, 0, 0)
        view_layout.setSpacing(0)

        self.page_tabs_widget = self.tabs_box.create_widget(self)
        view_layout.addWidget(self.page_tabs_widget)

        self.toolbar_widget = self.toolbar_box.create_widget(self)
        view_layout.addWidget(self.toolbar_widget)

        view_layout.addWidget(self.page_stack, 1)
        self.view_tab.setLayout(view_layout)

        self.settings_widget = self.settings_tab_box.create_widget(self)
        self.scripts_widget = self.scripts_tab_box.create_widget(self)

        self.content_stack.addWidget(self.view_tab)        # 0
        self.content_stack.addWidget(self.settings_widget)  # 1
        self.content_stack.addWidget(self.scripts_widget)   # 2

        self.tabs_box.restore_session()
        if self.page_stack.count() == 0:
            self.tabs_box.add_new_page_tab(QUrl("about:blank"))

        self._load_extensions()
        self.installEventFilter(self)
        self.main_tabs_visible = True

    def on_main_tab_changed(self, index):
        self.content_stack.setCurrentIndex(index)
        if index == 1:
            self.settings_tab_box.refresh_all()
        elif index == 2:
            self.scripts_tab_box.refresh_scripts_list()

    def toggle_main_tabs(self):
        if self.main_tabs_visible:
            self.main_tabs_box.hide_panel()
            self.main_tabs_visible = False
        else:
            self.main_tabs_box.show_panel()
            self.main_tabs_visible = True

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_F11:
                self.showNormal() if self.isFullScreen() else self.showFullScreen()
                return True
            elif event.key() == Qt.Key.Key_F5:
                loader = self.tabs_box.active_loader()
                if loader:
                    loader.reload()
                return True
        return super().eventFilter(obj, event)

    def _load_extensions(self):
        try:
            ext_wrapper = self.boxes.get("extensions")
            if ext_wrapper:
                ext_wrapper.set_profile(self.profile)
                loader = ext_wrapper.get_loader()
                webengine_paths, _ = loader.scan()
                manager = ext_wrapper.get_manager()
                if manager:
                    manager.install_all(webengine_paths)
                    self.toolbar_box.update_extension_icons(ext_manager=manager)
        except Exception as e:
            browser_logger.exception(f"Ошибка загрузки расширений: {e}")

    def closeEvent(self, event):
        self.tabs_box.save_session()
        event.accept()