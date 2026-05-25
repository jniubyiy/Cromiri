from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QMessageBox, QCheckBox
)
from ui.dialogs import ScriptEditDialog
from level_0.level_base import Box
from logger import browser_logger

class ScriptsTabBox(Box):
    def __init__(self, settings, session, script_manager):
        super().__init__("scripts_tab")
        self.settings = settings
        self.session = session
        self.script_manager = script_manager
        self._widget = None
        self.scripts_list = None

    def create_widget(self, parent=None):
        self._widget = QWidget(parent)
        layout = QVBoxLayout()
        self.scripts_list = QListWidget()
        self.refresh_scripts_list()
        layout.addWidget(QLabel("Пользовательские скрипты:"))
        layout.addWidget(self.scripts_list)

        btn_layout = QHBoxLayout()
        btn_add = QPushButton("➕ Добавить")
        btn_add.clicked.connect(self.add_script_dialog)
        btn_layout.addWidget(btn_add)
        btn_edit = QPushButton("✏️ Редактировать")
        btn_edit.clicked.connect(self.edit_script_dialog)
        btn_layout.addWidget(btn_edit)
        btn_remove = QPushButton("➖ Удалить")
        btn_remove.clicked.connect(self.remove_script_dialog)
        btn_layout.addWidget(btn_remove)
        layout.addLayout(btn_layout)
        self._widget.setLayout(layout)
        return self._widget

    def refresh_scripts_list(self):
        self.scripts_list.clear()
        scripts = self.script_manager.get_scripts()
        for idx, script in enumerate(scripts):
            item = QListWidgetItem()
            widget = QWidget()
            h_layout = QHBoxLayout()
            h_layout.setContentsMargins(4, 2, 4, 2)
            cb = QCheckBox(script.name)
            cb.setChecked(script.enabled)
            cb.stateChanged.connect(lambda state, i=idx: self.toggle_script(i, state == Qt.CheckState.Checked))
            h_layout.addWidget(cb)
            desc = script.description[:50] + "..." if len(script.description) > 50 else script.description
            desc_label = QLabel(desc)
            desc_label.setStyleSheet("color: gray; font-size: 10px;")
            h_layout.addWidget(desc_label)
            h_layout.addStretch()
            widget.setLayout(h_layout)
            item.setSizeHint(widget.sizeHint())
            self.scripts_list.addItem(item)
            self.scripts_list.setItemWidget(item, widget)

    def toggle_script(self, index, enabled):
        self.script_manager.toggle_script(index, enabled)
        self.refresh_scripts_list()

    def add_script_dialog(self):
        dialog = ScriptEditDialog(self._widget)
        if dialog.exec():
            name, desc, pattern, code = dialog.get_data()
            self.script_manager.add_script(name, desc, pattern, code)
            self.refresh_scripts_list()

    def edit_script_dialog(self):
        row = self.scripts_list.currentRow()
        if row < 0:
            QMessageBox.warning(self._widget, "Ошибка", "Выберите скрипт для редактирования.")
            return
        script = self.script_manager.get_scripts()[row]
        dialog = ScriptEditDialog(self._widget, script.name, script.description, script.pattern, script.code)
        if dialog.exec():
            name, desc, pattern, code = dialog.get_data()
            self.script_manager.update_script(row, name, desc, pattern, code)
            self.refresh_scripts_list()

    def remove_script_dialog(self):
        row = self.scripts_list.currentRow()
        if row < 0:
            QMessageBox.warning(self._widget, "Ошибка", "Выберите скрипт для удаления.")
            return
        script = self.script_manager.get_scripts()[row]
        reply = QMessageBox.question(
            self._widget, "Подтверждение",
            f"Удалить скрипт '{script.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.script_manager.remove_script(row)
            self.refresh_scripts_list()