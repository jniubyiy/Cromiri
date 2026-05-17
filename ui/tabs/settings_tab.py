# ui/tabs/settings_tab.py
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QGroupBox, QListWidget, QListWidgetItem, QFileDialog, QMessageBox,
    QCheckBox, QFormLayout
)
from logger import browser_logger

class SettingsTab(QWidget):
    def __init__(self, browser):
        super().__init__()
        self.browser = browser
        self.settings = browser.settings
        self.profile = browser.profile

        layout = QVBoxLayout()

        # ---------- Группа "Профиль" ----------
        profile_group = QGroupBox("Профиль")
        profile_form = QFormLayout()
        self.profile_path_edit = QLineEdit()
        browse_btn = QPushButton("Обзор...")
        browse_btn.clicked.connect(self.browse_profile_path)
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.profile_path_edit)
        path_layout.addWidget(browse_btn)
        profile_form.addRow("Путь к данным:", path_layout)
        profile_group.setLayout(profile_form)
        layout.addWidget(profile_group)

        # ---------- Группа "Параметры браузера" ----------
        browser_group = QGroupBox("Параметры браузера")
        browser_form = QFormLayout()

        self.user_agent_edit = QLineEdit()
        browser_form.addRow("User-Agent:", self.user_agent_edit)

        self.js_checkbox = QCheckBox("Включён")
        browser_form.addRow("JavaScript:", self.js_checkbox)

        self.images_checkbox = QCheckBox("Включены")
        browser_form.addRow("Изображения:", self.images_checkbox)

        browser_group.setLayout(browser_form)
        layout.addWidget(browser_group)

        # ---------- Группа "WebEngine-расширения" ----------
        ext_group = QGroupBox("WebEngine-расширения")
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
        layout.addWidget(ext_group)

        # ---------- Группа "Встроенные расширения" ----------
        builtin_group = QGroupBox("Встроенные расширения")
        builtin_layout = QVBoxLayout()
        self.builtin_ext_list_widget = QListWidget()
        self.refresh_builtin_extensions_list()
        builtin_layout.addWidget(QLabel("Доступные встроенные расширения:"))
        builtin_layout.addWidget(self.builtin_ext_list_widget)
        builtin_group.setLayout(builtin_layout)
        layout.addWidget(builtin_group)

        save_btn = QPushButton("Сохранить все настройки")
        save_btn.clicked.connect(self.save_all_settings)
        layout.addWidget(save_btn)

        layout.addStretch()
        self.setLayout(layout)

        # Первоначальное заполнение
        self.refresh_all()

    def refresh_all(self):
        """Перечитывает настройки и обновляет все виджеты."""
        self.profile_path_edit.setText(self.settings.get("profile_path", ""))
        self.user_agent_edit.setText(self.settings.get("browser_config.user_agent") or "")
        self.js_checkbox.setChecked(self.settings.get("browser_config.javascript_enabled", True))
        self.images_checkbox.setChecked(self.settings.get("browser_config.images_enabled", True))
        self.refresh_extensions_list()
        self.refresh_builtin_extensions_list()

    def browse_profile_path(self):
        path = QFileDialog.getExistingDirectory(self, "Выберите папку профиля")
        if path:
            self.profile_path_edit.setText(path)

    def save_all_settings(self):
        try:
            self.settings.set("profile_path", self.profile_path_edit.text().strip())
            self.settings.set("browser_config.user_agent", self.user_agent_edit.text().strip() or None)
            self.settings.set("browser_config.javascript_enabled", self.js_checkbox.isChecked())
            self.settings.set("browser_config.images_enabled", self.images_checkbox.isChecked())
            if self.profile:
                self.profile.setHttpUserAgent(self.settings.get("browser_config.user_agent") or "")
                ws = self.profile.settings()
                ws.setAttribute(ws.WebAttribute.JavascriptEnabled, self.js_checkbox.isChecked())
                ws.setAttribute(ws.WebAttribute.AutoLoadImages, self.images_checkbox.isChecked())
            self.settings.save()
            QMessageBox.information(self, "Сохранено", "Настройки успешно сохранены.")
        except Exception as e:
            browser_logger.error(f"Ошибка сохранения настроек: {e}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить настройки:\n{e}")

    # Методы для WebEngine-расширений
    def refresh_extensions_list(self):
        self.ext_list_widget.clear()
        ext_manager = getattr(self.browser, 'ext_manager', None)
        if not ext_manager:
            return
        for name in ext_manager.get_installed_names():
            item = QListWidgetItem()
            widget = QWidget()
            h_layout = QHBoxLayout()
            h_layout.setContentsMargins(4, 2, 4, 2)
            cb = QCheckBox(name)
            cb.setChecked(ext_manager.is_enabled(name))
            cb.stateChanged.connect(lambda state, n=name: self.toggle_extension(n, state == Qt.CheckState.Checked))
            h_layout.addWidget(cb)
            h_layout.addStretch()
            widget.setLayout(h_layout)
            item.setSizeHint(widget.sizeHint())
            self.ext_list_widget.addItem(item)
            self.ext_list_widget.setItemWidget(item, widget)

    def toggle_extension(self, name, enabled):
        ext_manager = getattr(self.browser, 'ext_manager', None)
        if not ext_manager:
            return
        ext_manager.toggle_extension(name, enabled)
        self.refresh_extensions_list()
        self.browser.nav_toolbar.update_extension_icons()
        self.browser.session.log_setting_change(f"extension:{name}", not enabled, enabled)

    def add_extension_dialog(self):
        ext_manager = getattr(self.browser, 'ext_manager', None)
        if not ext_manager:
            QMessageBox.warning(self, "Ошибка", "Поддержка WebEngine расширений отключена")
            return
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку расширения")
        if folder:
            if ext_manager.add_extension(folder):
                self.refresh_extensions_list()
                self.browser.nav_toolbar.update_extension_icons()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось добавить расширение.")

    def remove_extension_dialog(self):
        ext_manager = getattr(self.browser, 'ext_manager', None)
        if not ext_manager:
            return
        item = self.ext_list_widget.currentItem()
        if not item:
            return
        cb = self.ext_list_widget.itemWidget(item).findChild(QCheckBox)
        if cb:
            name = cb.text()
            confirm = QMessageBox.question(self, "Удаление", f"Удалить расширение '{name}'?")
            if confirm == QMessageBox.StandardButton.Yes:
                ext_manager.remove_extension(name)
                self.refresh_extensions_list()
                self.browser.nav_toolbar.update_extension_icons()

    # Методы для встроенных расширений
    def refresh_builtin_extensions_list(self):
        if not hasattr(self, 'builtin_ext_list_widget'):
            return
        self.builtin_ext_list_widget.clear()
        mgr = getattr(self.browser, 'builtin_ext_mgr', None)
        if not mgr:
            return
        for name in mgr.get_available_extensions():
            item = QListWidgetItem()
            widget = QWidget()
            h_layout = QHBoxLayout()
            h_layout.setContentsMargins(4, 2, 4, 2)
            cb = QCheckBox(name)
            cb.setChecked(mgr.is_extension_activated(name))
            cb.stateChanged.connect(lambda state, n=name: self.toggle_builtin_extension(n, state == Qt.CheckState.Checked))
            h_layout.addWidget(cb)
            h_layout.addStretch()
            widget.setLayout(h_layout)
            item.setSizeHint(widget.sizeHint())
            self.builtin_ext_list_widget.addItem(item)
            self.builtin_ext_list_widget.setItemWidget(item, widget)

    def toggle_builtin_extension(self, name, enabled):
        mgr = getattr(self.browser, 'builtin_ext_mgr', None)
        if not mgr:
            return
        mgr.toggle_extension(name, enabled)
        self.refresh_builtin_extensions_list()
        self.browser.nav_toolbar.update_extension_icons()