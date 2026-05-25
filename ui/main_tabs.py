# ui/main_tabs.py
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QParallelAnimationGroup
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QTabBar

class MainTabsPanel(QWidget):
    """Боковая панель главных вкладок – выезжает слева и одновременно раскрывается по высоте;
       при скрытии уходит влево и вверх."""
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

        # Вычисляем целевые размеры
        self.full_width = self.tab_bar.sizeHint().width() + 8
        self.full_height = self.tab_bar.sizeHint().height() + 4

        # Начальное состояние: полностью видима (будет управляться извне)
        self.setMaximumWidth(self.full_width)
        self.setMaximumHeight(self.full_height)

        # Анимации ширины и высоты
        self.width_anim = QPropertyAnimation(self, b"maximumWidth")
        self.width_anim.setDuration(300)
        self.width_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self.height_anim = QPropertyAnimation(self, b"maximumHeight")
        self.height_anim.setDuration(300)
        self.height_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self.anim_group = QParallelAnimationGroup()
        self.anim_group.addAnimation(self.width_anim)
        self.anim_group.addAnimation(self.height_anim)

    def show_panel(self):
        """Показать панель (выезд слева и раскрытие вниз)."""
        self.anim_group.stop()
        self.width_anim.setStartValue(self.width())
        self.width_anim.setEndValue(self.full_width)
        self.height_anim.setStartValue(self.height())
        self.height_anim.setEndValue(self.full_height)
        self.anim_group.start()

    def hide_panel(self):
        """Скрыть панель (заезд влево и схлопывание вверх)."""
        self.anim_group.stop()
        self.width_anim.setStartValue(self.width())
        self.width_anim.setEndValue(0)
        self.height_anim.setStartValue(self.height())
        self.height_anim.setEndValue(0)
        self.anim_group.start()