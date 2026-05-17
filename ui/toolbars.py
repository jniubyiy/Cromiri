# ui/toolbars.py
from PyQt6.QtCore import QUrl, QSize
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QToolButton, QMenu
)
from PyQt6.QtGui import QAction

class NavigationToolbar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.browser = parent

        # Основной вертикальный layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(2)

        # Верхняя строка: значки расширений (если есть)
        self.ext_icons_container = QWidget()
        self.ext_icons_layout = QHBoxLayout(self.ext_icons_container)
        self.ext_icons_layout.setContentsMargins(0, 0, 0, 0)
        self.ext_icons_layout.setSpacing(2)
        # Растяжка справа, чтобы значки были слева
        self.ext_icons_layout.addStretch()
        main_layout.addWidget(self.ext_icons_container)

        # Нижняя строка: кнопки навигации + адресная строка
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
        nav_layout.addWidget(self.address_bar, 1)  # растягивается

        main_layout.addLayout(nav_layout)

        # Изначально скрываем контейнер расширений
        self.ext_icons_container.hide()

    # ---------- Навигация ----------
    def go_back(self):
        loader = self.browser.page_tabs.active_loader()
        if loader:
            loader.back()

    def go_forward(self):
        loader = self.browser.page_tabs.active_loader()
        if loader:
            loader.forward()

    def go_refresh(self):
        loader = self.browser.page_tabs.active_loader()
        if loader:
            loader.reload()

    def navigate(self):
        text = self.address_bar.text().strip()
        if text:
            loader = self.browser.page_tabs.active_loader()
            if loader:
                loader.load_url(text)

    def update_for_view(self, view):
        self.address_bar.setText(view.url().toString())
        self.address_bar.setCursorPosition(0)

    def update_address_bar(self, url: QUrl):
        self.address_bar.setText(url.toString())
        self.address_bar.setCursorPosition(0)

    # ---------- Расширения ----------
    def update_extension_icons(self):
        # Очищаем старые значки
        while self.ext_icons_layout.count():
            item = self.ext_icons_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        # Проверяем, поддерживаются ли расширения
        if not self.browser.ext_manager._supports_extensions:
            self.ext_icons_container.hide()
            return

        # Добавляем значки включённых расширений
        any_visible = False
        for name in self.browser.ext_manager.get_installed_names():
            if self.browser.ext_manager.is_enabled(name):
                any_visible = True
                btn = QToolButton()
                btn.setIcon(self.browser.ext_manager.get_icon(name))
                btn.setIconSize(QSize(20, 20))
                btn.setToolTip(name)
                menu = QMenu()
                action_disable = QAction("Отключить", menu)
                action_disable.triggered.connect(
                    lambda checked, n=name: self.browser.toggle_extension(n, False)
                )
                menu.addAction(action_disable)
                btn.setMenu(menu)
                btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
                self.ext_icons_layout.addWidget(btn)

        if any_visible:
            # Добавляем растяжку, чтобы значки были слева, а справа пустота
            self.ext_icons_layout.addStretch()
            self.ext_icons_container.show()
        else:
            self.ext_icons_container.hide()