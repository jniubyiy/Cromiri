from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit
)
from level_0.level_base import Box
from logger import browser_logger

class ToolbarBox(Box):
    def __init__(self, webview_wrapper, settings, session_wrapper):
        super().__init__("toolbar")
        self.webview = webview_wrapper   # WebViewBox обёртка
        self.settings = settings
        self.session = session_wrapper
        self._widget = None
        self.ext_icons_container = None
        self.ext_icons_layout = None
        self.btn_back = None
        self.btn_forward = None
        self.btn_refresh = None
        self.address_bar = None

    def create_widget(self, parent=None):
        self._widget = QWidget(parent)
        main_layout = QVBoxLayout(self._widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(2)

        self.ext_icons_container = QWidget()
        self.ext_icons_layout = QHBoxLayout(self.ext_icons_container)
        self.ext_icons_layout.setContentsMargins(0, 0, 0, 0)
        self.ext_icons_layout.setSpacing(2)
        main_layout.addWidget(self.ext_icons_container)
        self.ext_icons_container.hide()

        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(2)

        self.btn_back = QPushButton(self.settings.tr("tab.back"))
        self.btn_back.clicked.connect(self.go_back)
        nav_layout.addWidget(self.btn_back)

        self.btn_forward = QPushButton(self.settings.tr("tab.forward"))
        self.btn_forward.clicked.connect(self.go_forward)
        nav_layout.addWidget(self.btn_forward)

        self.btn_refresh = QPushButton(self.settings.tr("tab.refresh"))
        self.btn_refresh.clicked.connect(self.go_refresh)
        nav_layout.addWidget(self.btn_refresh)

        self.address_bar = QLineEdit()
        self.address_bar.setPlaceholderText(self.settings.tr("toolbar.address_placeholder"))
        self.address_bar.returnPressed.connect(self.navigate)
        nav_layout.addWidget(self.address_bar, 1)

        main_layout.addLayout(nav_layout)
        return self._widget

    def go_back(self):
        browser_logger.info("Действие пользователя: нажата кнопка 'Назад'")
        self.session.record_action("Нажата кнопка 'Назад'")
        self.webview.call("back")

    def go_forward(self):
        browser_logger.info("Действие пользователя: нажата кнопка 'Вперёд'")
        self.session.record_action("Нажата кнопка 'Вперёд'")
        self.webview.call("forward")

    def go_refresh(self):
        browser_logger.info("Действие пользователя: нажата кнопка 'Обновить'")
        self.session.record_action("Нажата кнопка 'Обновить'")
        self.webview.call("reload")

    def navigate(self):
        text = self.address_bar.text().strip()
        browser_logger.info(f"Действие пользователя: ввод адреса '{text}' в адресную строку")
        self.session.record_action(f"Введён URL: {text}")
        if text:
            self.webview.call("load_url", text)

    def update_for_view(self, view):
        url = view.url().toString()
        self.address_bar.setText(url)
        self.address_bar.setCursorPosition(0)

    def update_address_bar(self, url: QUrl):
        url_str = url.toString()
        self.address_bar.setText(url_str)
        self.address_bar.setCursorPosition(0)

    def update_extension_icons(self, ext_manager=None, builtin_ext_mgr=None):
        pass

    def retranslate_ui(self):
        self.btn_back.setText(self.settings.tr("tab.back"))
        self.btn_forward.setText(self.settings.tr("tab.forward"))
        self.btn_refresh.setText(self.settings.tr("tab.refresh"))
        self.address_bar.setPlaceholderText(self.settings.tr("toolbar.address_placeholder"))