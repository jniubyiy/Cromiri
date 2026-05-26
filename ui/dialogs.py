from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QMessageBox
)

class ScriptEditDialog(QDialog):
    def __init__(self, parent=None, name="", description="", pattern="*", code="", settings=None):
        super().__init__(parent)
        self.settings = settings
        self.loc = settings if settings else None
        self.setWindowTitle(self.loc.tr("scripts.dialog.title") if self.loc else "Редактор скрипта")
        self.resize(600, 400)

        layout = QVBoxLayout()

        form_layout = QVBoxLayout()
        self.name_edit = QLineEdit(name)
        form_layout.addWidget(QLabel(self.loc.tr("scripts.dialog.name") if self.loc else "Название:"))
        form_layout.addWidget(self.name_edit)

        self.desc_edit = QLineEdit(description)
        form_layout.addWidget(QLabel(self.loc.tr("scripts.dialog.description") if self.loc else "Описание:"))
        form_layout.addWidget(self.desc_edit)

        self.pattern_edit = QLineEdit(pattern)
        form_layout.addWidget(QLabel(self.loc.tr("scripts.dialog.pattern") if self.loc else "URL-шаблон (glob или /regex/):"))
        form_layout.addWidget(self.pattern_edit)

        layout.addLayout(form_layout)

        self.code_edit = QTextEdit()
        self.code_edit.setPlainText(code)
        layout.addWidget(QLabel(self.loc.tr("scripts.dialog.code") if self.loc else "JavaScript-код:"))
        layout.addWidget(self.code_edit)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton(self.loc.tr("scripts.dialog.save") if self.loc else "Сохранить")
        save_btn.clicked.connect(self.accept)
        btn_layout.addWidget(save_btn)
        cancel_btn = QPushButton(self.loc.tr("scripts.dialog.cancel") if self.loc else "Отмена")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def get_data(self):
        return (
            self.name_edit.text().strip(),
            self.desc_edit.text().strip(),
            self.pattern_edit.text().strip(),
            self.code_edit.toPlainText()
        )

    def accept(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", self.loc.tr("scripts.error.empty_name") if self.loc else "Название не может быть пустым.")
            return
        super().accept()

    def reject(self):
        super().reject()