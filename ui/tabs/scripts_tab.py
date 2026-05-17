# ui/tabs/scripts_tab.py
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget,
    QListWidgetItem, QMessageBox, QCheckBox
)
from ui.dialogs import ScriptEditDialog
from logger import browser_logger

class ScriptsTab(QWidget):
    """Вкладка управления пользовательскими скриптами."""
    def __init__(self, browser):
        super().__init__()
        self.browser = browser
        self.script_manager = browser.script_manager
        self.session = browser.session

        layout = QVBoxLayout()
        self.scripts_list = QListWidget()
        self.refresh_scripts_list()
        layout.addWidget(QLabel("Пользовательские скрипты:"))
        layout.addWidget(self.scripts_list)

        btn_layout = QHBoxLayout()
        btn_add_script = QPushButton("➕ Добавить")
        btn_add_script.clicked.connect(self.add_script_dialog)
        btn_layout.addWidget(btn_add_script)
        btn_edit_script = QPushButton("✏️ Редактировать")
        btn_edit_script.clicked.connect(self.edit_script_dialog)
        btn_layout.addWidget(btn_edit_script)
        btn_remove_script = QPushButton("➖ Удалить")
        btn_remove_script.clicked.connect(self.remove_script_dialog)
        btn_layout.addWidget(btn_remove_script)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

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
            cb.stateChanged.connect(
                lambda state, i=idx: self.toggle_script(i, state == Qt.CheckState.Checked)
            )
            h_layout.addWidget(cb)
            desc_label = QLabel(
                script.description[:50] + "..." if len(script.description) > 50 else script.description
            )
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
        name = self.script_manager.get_scripts()[index].name
        self.session.log_setting_change(f"script:{name}", not enabled, enabled)
        browser_logger.info(f"Скрипт '{name}' {'включён' if enabled else 'отключён'}")

    def add_script_dialog(self):
        dialog = ScriptEditDialog(self)
        if dialog.exec():
            name, desc, pattern, code = dialog.get_data()
            self.script_manager.add_script(name, desc, pattern, code)
            self.refresh_scripts_list()
            browser_logger.info(f"Добавлен скрипт '{name}'")

    def edit_script_dialog(self):
        current_row = self.scripts_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите скрипт для редактирования.")
            return
        script = self.script_manager.get_scripts()[current_row]
        dialog = ScriptEditDialog(self, script.name, script.description, script.pattern, script.code)
        if dialog.exec():
            name, desc, pattern, code = dialog.get_data()
            self.script_manager.update_script(current_row, name, desc, pattern, code)
            self.refresh_scripts_list()
            browser_logger.info(f"Скрипт '{name}' изменён")

    def remove_script_dialog(self):
        current_row = self.scripts_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите скрипт для удаления.")
            return
        script = self.script_manager.get_scripts()[current_row]
        confirm = QMessageBox.question(self, "Удаление", f"Удалить скрипт '{script.name}'?")
        if confirm == QMessageBox.StandardButton.Yes:
            self.script_manager.remove_script(current_row)
            self.refresh_scripts_list()
            browser_logger.info(f"Скрипт '{script.name}' удалён")