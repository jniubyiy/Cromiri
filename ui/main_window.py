# ui/main_window.py
import sys
import os
from PyQt6.QtCore import QUrl, Qt, QSize, QPropertyAnimation, QEasingCurve, QEvent
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QGroupBox, QListWidget, QListWidgetItem,
    QFileDialog, QMessageBox, QCheckBox, QToolButton, QMenu, QTextEdit,
    QTabBar, QStackedWidget, QFrame
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineScript

from settings import SettingsManager
from extensions import ExtensionManager
from page_loader import PageLoader
from style_manager import StyleManager
from site_scripts import SiteScriptManager
from session import SessionManager
from logger import browser_logger

from ui.main_tabs import MainTabManager
from ui.page_tabs import PageTabManager
from ui.toolbars import NavigationToolbar
from ui.dialogs import ScriptEditDialog


class BrowserUI(QMainWindow):
    def __init__(self):
        super().__init__()
        browser_logger.info("Инициализация главного окна браузера")
        self.setWindowTitle("Cromiri")   # <-- изменено здесь
        self.resize(1280, 800)

        # Менеджеры
        self.settings = SettingsManager()
        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.setPersistentStoragePath(self.settings.get("profile_path"))
        self.profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)

        self.ext_manager = ExtensionManager(self.profile, self.settings, "extensions")
        self.style_manager = StyleManager(self.settings)
        self.script_manager = SiteScriptManager(self.settings)
        self.session = SessionManager()

        # Основной layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Главные вкладки (сворачиваемые)
        self.main_tabs = MainTabManager(self)
        main_layout.addWidget(self.main_tabs)

        # Стек для страниц главных вкладок
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack, 1)

        # Инициализация страниц
        self.init_view_tab()
        self.init_settings_tab()
        self.init_scripts_tab()

        self.content_stack.addWidget(self.view_tab)      # index 0
        self.content_stack.addWidget(self.settings_tab)  # index 1
        self.content_stack.addWidget(self.scripts_tab)   # index 2

        self.main_tabs.tab_bar.currentChanged.connect(self.on_main_tab_changed)
        self.main_tabs.tab_bar.setCurrentIndex(0)

        # Расширения (устанавливаются после создания UI)
        self.ext_manager.install_all()
        # Обновляем значки расширений (nav_toolbar уже существует)
        self.nav_toolbar.update_extension_icons()

        # Первая вкладка страницы
        self.page_tabs.add_new_page_tab(QUrl("about:blank"))

        self.installEventFilter(self)

    def on_main_tab_changed(self, index):
        self.content_stack.setCurrentIndex(index)

    # ---------------------- Вкладка "Просмотр" ----------------------
    def init_view_tab(self):
        self.view_tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Стек для веб-страниц
        self.page_stack = QStackedWidget()

        self.page_tabs = PageTabManager(self, self.page_stack)
        layout.addWidget(self.page_tabs)

        self.nav_toolbar = NavigationToolbar(self)
        layout.addWidget(self.nav_toolbar)

        layout.addWidget(self.page_stack, 1)

        self.view_tab.setLayout(layout)

    # ---------------------- Вкладка "Настройки" ----------------------
    def init_settings_tab(self):
        self.settings_tab = QWidget()
        main_layout = QVBoxLayout()

        nav_group = QGroupBox("Навигация")
        nav_layout = QVBoxLayout()
        nav_layout.addWidget(QLabel("URL:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        nav_layout.addWidget(self.url_input)
        btn_go = QPushButton("🔗 Перейти")
        btn_go.clicked.connect(self.go_to_url)
        nav_layout.addWidget(btn_go)
        btn_gelbooru = QPushButton("🚀 Gelbooru (все посты)")
        btn_gelbooru.clicked.connect(self.open_gelbooru)
        nav_layout.addWidget(btn_gelbooru)
        nav_group.setLayout(nav_layout)
        main_layout.addWidget(nav_group)

        ext_group = QGroupBox("Расширения")
        ext_layout = QVBoxLayout()
        self.ext_list_widget = QListWidget()
        self.refresh_extensions_list()
        ext_layout.addWidget(QLabel("Установленные расширения:"))
        ext_layout.addWidget(self.ext_list_widget)

        btn_add = QPushButton("➕ Добавить расширение (папка)")
        btn_add.clicked.connect(self.add_extension_dialog)
        ext_layout.addWidget(btn_add)

        btn_remove = QPushButton("➖ Удалить выбранное")
        btn_remove.clicked.connect(self.remove_extension_dialog)
        ext_layout.addWidget(btn_remove)

        ext_group.setLayout(ext_layout)
        main_layout.addWidget(ext_group)

        main_layout.addStretch()
        self.settings_tab.setLayout(main_layout)

    # ---------------------- Вкладка "Скрипты" ----------------------
    def init_scripts_tab(self):
        self.scripts_tab = QWidget()
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
        self.scripts_tab.setLayout(layout)

    # ---------------------- Логика скриптов ----------------------
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
            desc_label = QLabel(script.description[:50] + "..." if len(script.description) > 50 else script.description)
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

    # ---------------------- Управление расширениями ----------------------
    def refresh_extensions_list(self):
        self.ext_list_widget.clear()
        for name in self.ext_manager.get_installed_names():
            item = QListWidgetItem()
            widget = QWidget()
            layout = QHBoxLayout()
            layout.setContentsMargins(4, 2, 4, 2)
            cb = QCheckBox(name)
            cb.setChecked(self.ext_manager.is_enabled(name))
            cb.stateChanged.connect(lambda state, n=name: self.toggle_extension(n, state == Qt.CheckState.Checked))
            layout.addWidget(cb)
            layout.addStretch()
            widget.setLayout(layout)
            item.setSizeHint(widget.sizeHint())
            self.ext_list_widget.addItem(item)
            self.ext_list_widget.setItemWidget(item, widget)

    def toggle_extension(self, name, enabled):
        old = not enabled
        self.ext_manager.toggle_extension(name, enabled)
        self.refresh_extensions_list()
        self.nav_toolbar.update_extension_icons()
        self.session.log_setting_change(f"extension:{name}", old, enabled)
        browser_logger.info(f"Расширение '{name}' {'включено' if enabled else 'отключено'}")

    def add_extension_dialog(self):
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку расширения")
        if folder:
            if self.ext_manager.add_extension(folder):
                self.refresh_extensions_list()
                self.nav_toolbar.update_extension_icons()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось добавить расширение.")

    def remove_extension_dialog(self):
        item = self.ext_list_widget.currentItem()
        if not item:
            return
        cb = self.ext_list_widget.itemWidget(item).findChild(QCheckBox)
        if cb:
            name = cb.text()
            confirm = QMessageBox.question(self, "Удаление", f"Удалить расширение '{name}'?")
            if confirm == QMessageBox.StandardButton.Yes:
                self.ext_manager.remove_extension(name)
                self.refresh_extensions_list()
                self.nav_toolbar.update_extension_icons()

    # ---------------------- Навигация из настроек ----------------------
    def go_to_url(self):
        url = self.url_input.text().strip()
        if url:
            self.page_tabs.active_loader().load_url(url)
            self.main_tabs.tab_bar.setCurrentIndex(0)

    def open_gelbooru(self):
        self.page_tabs.active_loader().load_gelbooru_all()
        self.main_tabs.tab_bar.setCurrentIndex(0)

    # ---------------------- Логирование событий страницы ----------------------
    def on_console_message(self, level, message, line, source):
        self.session.log_page_event("console", f"level={level}, msg={message}")

    def log_navigation_event(self, url: QUrl, title: str = ""):
        self.session.log_navigation(url.toString(), title)

    # ---------------------- Сессия и события ----------------------
    def eventFilter(self, obj, event):
        try:
            if event.type() == QEvent.Type.KeyPress:
                key = event.key()
                modifiers = event.modifiers()
                combo = ""
                if modifiers & Qt.KeyboardModifier.ControlModifier:
                    combo += "Ctrl+"
                if modifiers & Qt.KeyboardModifier.ShiftModifier:
                    combo += "Shift+"
                if modifiers & Qt.KeyboardModifier.AltModifier:
                    combo += "Alt+"
                text = event.text()
                if text and len(text) == 1:
                    combo += text
                else:
                    combo += str(key)
                self.session.log_action("key_press", combo)
            elif event.type() == QEvent.Type.MouseButtonPress:
                btn = event.button()
                self.session.log_action("mouse_click", f"button={btn}, pos=({event.pos().x()},{event.pos().y()})")
        except Exception as e:
            browser_logger.exception("Ошибка в eventFilter")
        return super().eventFilter(obj, event)

    def closeEvent(self, event):
        self.session.save()
        browser_logger.info("Завершение работы браузера")
        super().closeEvent(event)