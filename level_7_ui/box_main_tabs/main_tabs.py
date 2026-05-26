from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QParallelAnimationGroup
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QTabBar
from level_0.level_base import Box

class MainTabsBox(Box):
    def __init__(self, settings):
        super().__init__("main_tabs")
        self.settings = settings
        self._widget = None
        self.tab_bar = None
        self.anim_group = None
        self.full_width = 0
        self.full_height = 0

    def get_tab_bar(self):
        return self.tab_bar

    def create_widget(self, parent=None):
        self._widget = QWidget(parent)
        layout = QHBoxLayout(self._widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.tab_bar = QTabBar()
        self.tab_bar.addTab(self.settings.tr("main_tabs.view"))
        self.tab_bar.addTab(self.settings.tr("main_tabs.settings"))
        self.tab_bar.addTab(self.settings.tr("main_tabs.scripts"))
        layout.addWidget(self.tab_bar)
        layout.addStretch()

        self.full_width = self.tab_bar.sizeHint().width() + 8
        self.full_height = self.tab_bar.sizeHint().height() + 4
        self._widget.setMaximumWidth(self.full_width)
        self._widget.setMaximumHeight(self.full_height)

        self.width_anim = QPropertyAnimation(self._widget, b"maximumWidth")
        self.width_anim.setDuration(300)
        self.width_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.height_anim = QPropertyAnimation(self._widget, b"maximumHeight")
        self.height_anim.setDuration(300)
        self.height_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self.anim_group = QParallelAnimationGroup()
        self.anim_group.addAnimation(self.width_anim)
        self.anim_group.addAnimation(self.height_anim)

        return self._widget

    def show_panel(self):
        self.anim_group.stop()
        self.width_anim.setStartValue(self._widget.width())
        self.width_anim.setEndValue(self.full_width)
        self.height_anim.setStartValue(self._widget.height())
        self.height_anim.setEndValue(self.full_height)
        self.anim_group.start()

    def hide_panel(self):
        self.anim_group.stop()
        self.width_anim.setStartValue(self._widget.width())
        self.width_anim.setEndValue(0)
        self.height_anim.setStartValue(self._widget.height())
        self.height_anim.setEndValue(0)
        self.anim_group.start()

    def retranslate_ui(self):
        if self.tab_bar:
            self.tab_bar.setTabText(0, self.settings.tr("main_tabs.view"))
            self.tab_bar.setTabText(1, self.settings.tr("main_tabs.settings"))
            self.tab_bar.setTabText(2, self.settings.tr("main_tabs.scripts"))