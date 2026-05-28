# level_12_ui/box_scripts_tab/scripts_tab.py

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QMessageBox, QCheckBox
)
from ui.dialogs import ScriptEditDialog
from level_0.level_base import Box

class ScriptsTabBox(Box):
    def __init__(self, settings, session, script_wrapper):
        super().__init__("scripts_tab")
        self.settings = settings
        self.session = session
        self.script = script_wrapper   # обёртка ScriptLevelWrapper
        self._widget = None
        self.scripts_list = None

    def create_widget(self, parent=None):
        self._widget = QWidget(parent)
        layout = QVBoxLayout()
        self.scripts_list = QListWidget()
        self.refresh_scripts_list()
        layout.addWidget(QLabel(self.settings.tr("scripts.section")))
        layout.addWidget(self.scripts_list)
        btn_layout = QHBoxLayout()
        btn_add = QPushButton(self.settings.tr("scripts.add"))
        btn_add.clicked.connect(self.add_script_dialog)
        btn_layout.addWidget(btn_add)
        btn_edit = QPushButton(self.settings.tr("scripts.edit"))
        btn_edit.clicked.connect(self.edit_script_dialog)
        btn_layout.addWidget(btn_edit)
        btn_remove = QPushButton(self.settings.tr("scripts.remove"))
        btn_remove.clicked.connect(self.remove_script_dialog)
        btn_layout.addWidget(btn_remove)
        layout.addLayout(btn_layout)
        self._widget.setLayout(layout)
        return self._widget

    def refresh_scripts_list(self):
        self.scripts_list.clear()
        scripts = self.script.get_scripts()   # публичный метод уровня
        for idx, script in enumerate(scripts):
            item = QListWidgetItem()
            widget = QWidget()
            h_layout = QHBoxLayout()
            h_layout.setContentsMargins(4, 2, 4, 2)
            cb = QCheckBox(script["name"])
            cb.setChecked(script.get("enabled", True))
            cb.stateChanged.connect(lambda state, i=idx: self.toggle_script(i, state == Qt.CheckState.Checked))
            h_layout.addWidget(cb)
            desc = script.get("description", "")[:50]
            if len(script.get("description", "")) > 50:
                desc += "..."
            desc_label = QLabel(desc)
            desc_label.setStyleSheet("color: gray; font-size: 10px;")
            h_layout.addWidget(desc_label)
            h_layout.addStretch()
            widget.setLayout(h_layout)
            item.setSizeHint(widget.sizeHint())
            self.scripts_list.addItem(item)
            self.scripts_list.setItemWidget(item, widget)

    def toggle_script(self, index, enabled):
        self.script.toggle_script(index, enabled)
        self.refresh_scripts_list()

    def add_script_dialog(self):
        dialog = ScriptEditDialog(self._widget, settings=self.settings)
        if dialog.exec():
            name, desc, pattern, code = dialog.get_data()
            self.script.add_script(name, desc, pattern, code)   # публичный метод
            self.refresh_scripts_list()

    def edit_script_dialog(self):
        row = self.scripts_list.currentRow()
        if row < 0:
            QMessageBox.warning(self._widget, "Ошибка", self.settings.tr("scripts.error.no_selection"))
            return
        scripts = self.script.get_scripts()
        script = scripts[row]
        dialog = ScriptEditDialog(self._widget, script["name"], script.get("description", ""),
                                  script["pattern"], script["code"], settings=self.settings)
        if dialog.exec():
            name, desc, pattern, code = dialog.get_data()
            self.script.update_script(row, name, desc, pattern, code)
            self.refresh_scripts_list()

    def remove_script_dialog(self):
        row = self.scripts_list.currentRow()
        if row < 0:
            QMessageBox.warning(self._widget, "Ошибка", self.settings.tr("scripts.error.no_selection_remove"))
            return
        self.script.remove_script(row)
        self.refresh_scripts_list()

    def retranslate_ui(self):
        pass