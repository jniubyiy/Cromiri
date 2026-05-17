# ui/main_tabs.py
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QTimer
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QTabBar

class MainTabsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.tab_bar = QTabBar()
        self.tab_bar.addTab(" Просмотр")
        self.tab_bar.addTab("⚙️ Настройки")
        self.tab_bar.addTab(" Скрипты")
        layout.addWidget(self.tab_bar)
        layout.addStretch()

        self.full_width = self.tab_bar.sizeHint().width() + 8
        self.full_height = self.tab_bar.sizeHint().height() + 4

        self.setMaximumWidth(0)
        self.setMaximumHeight(0)

        self.width_anim = QPropertyAnimation(self, b"maximumWidth")
        self.width_anim.setDuration(300)
        self.width_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self.height_anim = QPropertyAnimation(self, b"maximumHeight")
        self.height_anim.setDuration(300)
        self.height_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

        # Тайм-аут анимации
        self._anim_timer = QTimer(self)
        self._anim_timer.setSingleShot(True)
        self._anim_timer.timeout.connect(self._on_anim_timeout)

    def show_panel(self):
        self._start_anim(self.full_width, self.full_height)

    def hide_panel(self):
        self._start_anim(0, 0)

    def _start_anim(self, target_width, target_height):
        self.width_anim.stop()
        self.height_anim.stop()
        self.width_anim.setStartValue(self.width())
        self.width_anim.setEndValue(target_width)
        self.height_anim.setStartValue(self.height())
        self.height_anim.setEndValue(target_height)
        self.width_anim.start()
        self.height_anim.start()
        # Тайм-аут: если через 1 с анимация не завершилась, принудительно ставим конечное состояние
        self._anim_timer.start(1000)
        self._target_width = target_width
        self._target_height = target_height

    def _on_anim_timeout(self):
        self.width_anim.stop()
        self.height_anim.stop()
        self.setMaximumWidth(self._target_width)
        self.setMaximumHeight(self._target_height)