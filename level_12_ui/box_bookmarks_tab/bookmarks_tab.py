from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QListWidgetItem, QLabel, QLineEdit, QMessageBox, QInputDialog
)
from PyQt6.QtCore import QUrl
from level_0.level_base import Box

class BookmarksTabBox(Box):
    def __init__(self, session_wrapper, settings):
        super().__init__("bookmarks_tab")
        self.session = session_wrapper
        self.settings = settings
        self._widget = None
        self.bookmarks_list = None

    def create_widget(self, parent=None):
        self._widget = QWidget(parent)
        layout = QVBoxLayout(self._widget)

        title_label = QLabel(self.settings.tr("bookmarks.title"))
        layout.addWidget(title_label)

        self.bookmarks_list = QListWidget()
        layout.addWidget(self.bookmarks_list)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton(self.settings.tr("bookmarks.add"))
        add_btn.clicked.connect(self.add_bookmark_dialog)
        btn_layout.addWidget(add_btn)

        remove_btn = QPushButton(self.settings.tr("bookmarks.remove"))
        remove_btn.clicked.connect(self.remove_bookmark)
        btn_layout.addWidget(remove_btn)

        open_btn = QPushButton(self.settings.tr("bookmarks.open"))
        open_btn.clicked.connect(self.open_bookmark)
        btn_layout.addWidget(open_btn)

        layout.addLayout(btn_layout)

        self.refresh()
        return self._widget

    def refresh(self):
        self.bookmarks_list.clear()
        bookmarks = self.session.get_all_bookmarks()
        for bm in bookmarks:
            item = QListWidgetItem(f"{bm['title']}  —  {bm['url']}")
            self.bookmarks_list.addItem(item)

    def add_bookmark_dialog(self):
        # Диалог ввода названия и URL
        title, ok1 = QInputDialog.getText(self._widget, "Новая закладка", "Название:")
        if not ok1 or not title.strip():
            return
        url, ok2 = QInputDialog.getText(self._widget, "Новая закладка", "URL:")
        if not ok2 or not url.strip():
            return
        title = title.strip()
        url = url.strip()
        if not url.startswith('http'):
            url = 'https://' + url
        if self.session.add_bookmark(title, url):
            self.refresh()
        else:
            QMessageBox.warning(self._widget, "Ошибка", "Закладка с таким URL уже существует.")

    def remove_bookmark(self):
        row = self.bookmarks_list.currentRow()
        if row < 0:
            QMessageBox.warning(self._widget, "Ошибка", "Выберите закладку для удаления.")
            return
        if self.session.remove_bookmark(row):
            self.refresh()
        else:
            QMessageBox.warning(self._widget, "Ошибка", "Не удалось удалить закладку.")

    def open_bookmark(self):
        row = self.bookmarks_list.currentRow()
        if row < 0:
            QMessageBox.warning(self._widget, "Ошибка", "Выберите закладку для открытия.")
            return
        bookmarks = self.session.get_all_bookmarks()
        if row < len(bookmarks):
            url = bookmarks[row]['url']
            # Используем центральный механизм открытия вкладки через TabsBox
            # Для этого получаем ссылку на TabsBox через внешний вызов из WindowBox
            # Предполагаем, что window_box передаст коллбэк или прямой доступ к tabs_wrapper
            # Пока реализуем простой вызов через внешнюю функцию, которая будет установлена
            if hasattr(self, 'open_url_callback'):
                self.open_url_callback(url)
            else:
                # Запасной вариант: открыть в новой вкладке через родительское окно (если доступно)
                # Но лучше передать коллбэк из WindowBox при создании
                pass

    def set_open_url_callback(self, callback):
        """Устанавливает функцию для открытия URL в браузере."""
        self.open_url_callback = callback

    def retranslate_ui(self):
        pass