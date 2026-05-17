# ui/main_tabs.py
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QTabBar

class MainTabManager(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.browser = parent

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self.toggle_btn = QPushButton("◻")
        self.toggle_btn.setFixedSize(28, 28)
        self.toggle_btn.setToolTip("Свернуть/Развернуть главные вкладки")
        self.toggle_btn.clicked.connect(self.toggle_tabs)
        layout.addWidget(self.toggle_btn)

        self.tab_bar_container = QWidget()
        self.tab_bar_container.setMinimumWidth(0)
        container_layout = QVBoxLayout(self.tab_bar_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        self.tab_bar = QTabBar()
        self.tab_bar.addTab("📋 Просмотр")
        self.tab_bar.addTab("⚙️ Настройки")
        self.tab_bar.addTab("📜 Скрипты")
        container_layout.addWidget(self.tab_bar)

        layout.addWidget(self.tab_bar_container, 1)
        layout.addStretch()

        self.tabs_visible = True
        self.update_tab_bar_width()
        self.tab_bar_container.setMaximumWidth(self.tab_bar_width)

    def update_tab_bar_width(self):
        width = self.tab_bar.sizeHint().width() + 4
        if width < 200:
            width = 300
        self.tab_bar_width = width

    def toggle_tabs(self):
        self.tabs_visible = not self.tabs_visible
        target_width = self.tab_bar_width if self.tabs_visible else 0
        self.anim = QPropertyAnimation(self.tab_bar_container, b"maximumWidth")
        self.anim.setDuration(300)
        self.anim.setStartValue(self.tab_bar_container.maximumWidth())
        self.anim.setEndValue(target_width)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.anim.start()