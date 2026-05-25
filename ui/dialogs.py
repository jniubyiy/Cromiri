from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QMessageBox
)

class ScriptEditDialog(QWidget):
    def __init__(self, parent=None, name="", description="", pattern="*", code=""):
        super().__init__(parent)
        self.setWindowTitle("Редактор скрипта")
        self.resize(600, 400)
        layout = QVBoxLayout()
        form_layout = QVBoxLayout()
        self.name_edit = QLineEdit(name)
        form_layout.addWidget(QLabel("Название:"))
        form_layout.addWidget(self.name_edit)
        self.desc_edit = QLineEdit(description)
        form_layout.addWidget(QLabel("Описание:"))
        form_layout.addWidget(self.desc_edit)
        self.pattern_edit = QLineEdit(pattern)
        form_layout.addWidget(QLabel("URL-шаблон (glob или /regex/):"))
        form_layout.addWidget(self.pattern_edit)
        layout.addLayout(form_layout)
        self.code_edit = QTextEdit()
        self.code_edit.setPlainText(code)
        layout.addWidget(QLabel("JavaScript-код:"))
        layout.addWidget(self.code_edit)
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.accept)
        btn_layout.addWidget(save_btn)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    def get_data(self):
        return (self.name_edit.text().strip(), self.desc_edit.text().strip(),
                self.pattern_edit.text().strip(), self.code_edit.toPlainText())
    def accept(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Название не может быть пустым.")
            return
        self.close()
    def reject(self):
        self.close()