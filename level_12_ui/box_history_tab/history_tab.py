from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QListWidgetItem, QComboBox, QLabel
)
from PyQt6.QtCore import Qt
from level_0.level_base import Box

class HistoryTabBox(Box):
    def __init__(self, session_wrapper, settings):
        super().__init__("history_tab")
        self.session = session_wrapper
        self.settings = settings
        self._widget = None
        self.filter_combo = None
        self.history_list = None

    def create_widget(self, parent=None):
        self._widget = QWidget(parent)
        layout = QVBoxLayout(self._widget)

        # Заголовок и фильтр
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel(self.settings.tr("history.title")))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            self.settings.tr("history.filter.all"),
            self.settings.tr("history.filter.visits"),
            self.settings.tr("history.filter.actions"),
            self.settings.tr("history.filter.downloads"),
            self.settings.tr("history.filter.settings")
        ])
        self.filter_combo.currentIndexChanged.connect(self.refresh)
        top_layout.addWidget(self.filter_combo)
        layout.addLayout(top_layout)

        self.history_list = QListWidget()
        layout.addWidget(self.history_list)

        self.refresh()
        return self._widget

    def refresh(self):
        self.history_list.clear()
        filter_type = self.filter_combo.currentText()
        if filter_type == self.settings.tr("history.filter.all"):
            event_type = None
        elif filter_type == self.settings.tr("history.filter.visits"):
            event_type = "visit"
        elif filter_type == self.settings.tr("history.filter.actions"):
            event_type = "action"
        elif filter_type == self.settings.tr("history.filter.downloads"):
            event_type = "download"
        elif filter_type == self.settings.tr("history.filter.settings"):
            event_type = "settings_change"
        else:
            event_type = None

        events = self.session.get_all_history_events(event_type)
        for ev in events[::-1]:  # новые сверху
            item_text = self._format_event(ev)
            item = QListWidgetItem(item_text)
            self.history_list.addItem(item)

    def _format_event(self, ev):
        ts = ev.get("timestamp", "")[:19]
        etype = ev.get("type", "")
        if etype == "visit":
            return f"[{ts}] Посещение: {ev.get('url','')} ({ev.get('title','')})"
        elif etype == "action":
            return f"[{ts}] Действие: {ev.get('action','')} {ev.get('details','')}"
        elif etype == "download":
            return f"[{ts}] Загрузка: {ev.get('file_name','')}"
        elif etype == "settings_change":
            changes = ev.get("changes", {})
            lines = []
            for key, vals in changes.items():
                lines.append(f"{key}: {vals.get('old','?')} → {vals.get('new','?')}")
            return f"[{ts}] Изменены настройки: {', '.join(lines)}"
        else:
            return f"[{ts}] {ev}"

    def retranslate_ui(self):
        # Заглушка, можно обновить при необходимости
        pass