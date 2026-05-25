from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QToolButton
)
from logger import browser_logger

class ToolbarBox:
    def __init__(self, tabs_box):
        self.tabs_box = tabs_box
        self._widget = None
        self.ext_icons_container = None
        self.ext_icons_layout = None

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

        self.btn_back = QPushButton("←")
        self.btn_back.clicked.connect(self.go_back)
        nav_layout.addWidget(self.btn_back)

        self.btn_forward = QPushButton("→")
        self.btn_forward.clicked.connect(self.go_forward)
        nav_layout.addWidget(self.btn_forward)

        self.btn_refresh = QPushButton("⟳")
        self.btn_refresh.clicked.connect(self.go_refresh)
        nav_layout.addWidget(self.btn_refresh)

        self.address_bar = QLineEdit()
        self.address_bar.returnPressed.connect(self.navigate)
        nav_layout.addWidget(self.address_bar, 1)

        main_layout.addLayout(nav_layout)
        return self._widget

    def go_back(self):
        loader = self.tabs_box.active_loader()
        if loader:
            loader.back()

    def go_forward(self):
        loader = self.tabs_box.active_loader()
        if loader:
            loader.forward()

    def go_refresh(self):
        loader = self.tabs_box.active_loader()
        if loader:
            loader.reload()

    def navigate(self):
        text = self.address_bar.text().strip()
        if text:
            loader = self.tabs_box.active_loader()
            if loader:
                loader.load_url(text)

    def update_for_view(self, view):
        self.address_bar.setText(view.url().toString())
        self.address_bar.setCursorPosition(0)

    def update_address_bar(self, url: QUrl):
        self.address_bar.setText(url.toString())
        self.address_bar.setCursorPosition(0)

    def update_extension_icons(self, ext_manager=None, builtin_ext_mgr=None):
        while self.ext_icons_layout.count():
            item = self.ext_icons_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        webengine_exts = []
        if ext_manager and hasattr(ext_manager, 'get_installed_names'):
            for name in ext_manager.get_installed_names():
                if ext_manager.is_enabled(name):
                    webengine_exts.append(name)
        builtin_exts = []
        if builtin_ext_mgr:
            builtin_exts = builtin_ext_mgr.get_activated_extensions()
        if not webengine_exts and not builtin_exts:
            self.ext_icons_container.hide()
            return
        for name in webengine_exts:
            btn = QToolButton()
            btn.setText(name[:2].upper())
            btn.setToolTip(name)
            btn.setFixedSize(24, 24)
            self.ext_icons_layout.addWidget(btn)
        for name in builtin_exts:
            btn = QToolButton()
            btn.setText(name[:2].upper())
            btn.setToolTip(f"[B] {name}")
            btn.setFixedSize(24, 24)
            self.ext_icons_layout.addWidget(btn)
        self.ext_icons_layout.addStretch()
        self.ext_icons_container.show()