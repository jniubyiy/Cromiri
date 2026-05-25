# ui/tabs/settings_tab.py
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QGroupBox, QListWidget, QListWidgetItem, QFileDialog, QMessageBox,
    QCheckBox, QFormLayout, QSpinBox, QScrollArea
)
from logger import browser_logger

class SettingsTab(QWidget):
    def __init__(self, browser):
        super().__init__()
        self.browser = browser
        self.settings = browser.settings
        self.profile = browser.profile

        main_scroll = QScrollArea()
        main_scroll.setWidgetResizable(True)
        container = QWidget()
        main_scroll.setWidget(container)

        layout = QVBoxLayout(container)

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

        # ---------- Группа "Лимиты вкладок" ----------
        tabs_limits_group = QGroupBox("Лимиты вкладок")
        tabs_form = QFormLayout()
        self.max_tabs_spin = QSpinBox()
        self.max_tabs_spin.setRange(1, 200)
        tabs_form.addRow("Максимум вкладок:", self.max_tabs_spin)
        self.reload_limit_spin = QSpinBox()
        self.reload_limit_spin.setRange(1, 50)
        tabs_form.addRow("Лимит перезагрузок:", self.reload_limit_spin)
        self.reload_interval_spin = QSpinBox()
        self.reload_interval_spin.setRange(5, 300)
        self.reload_interval_spin.setSuffix(" сек")
        tabs_form.addRow("Интервал перезагрузок:", self.reload_interval_spin)
        tabs_limits_group.setLayout(tabs_form)
        layout.addWidget(tabs_limits_group)

        # ---------- Группа "Лимиты ресурсов" ----------
        resource_group = QGroupBox("Лимиты ресурсов")
        resource_form = QFormLayout()
        self.max_mem_spin = QSpinBox()
        self.max_mem_spin.setRange(30, 100)
        self.max_mem_spin.setSuffix(" %")
        resource_form.addRow("Макс. память:", self.max_mem_spin)
        self.max_cpu_spin = QSpinBox()
        self.max_cpu_spin.setRange(30, 100)
        self.max_cpu_spin.setSuffix(" %")
        resource_form.addRow("Макс. CPU:", self.max_cpu_spin)
        self.monitor_interval_spin = QSpinBox()
        self.monitor_interval_spin.setRange(1000, 60000)
        self.monitor_interval_spin.setSingleStep(1000)
        self.monitor_interval_spin.setSuffix(" мс")
        resource_form.addRow("Интервал проверки:", self.monitor_interval_spin)
        resource_group.setLayout(resource_form)
        layout.addWidget(resource_group)

        # ---------- Группа "Лимиты расширений" ----------
        ext_limits_group = QGroupBox("Лимиты расширений")
        ext_limits_form = QFormLayout()
        self.max_ext_size_spin = QSpinBox()
        self.max_ext_size_spin.setRange(10, 1000)
        self.max_ext_size_spin.setSuffix(" МБ")
        ext_limits_form.addRow("Макс. размер расширения:", self.max_ext_size_spin)
        self.max_errors_spin = QSpinBox()
        self.max_errors_spin.setRange(1, 100)
        ext_limits_form.addRow("Макс. ошибок в интервале:", self.max_errors_spin)
        self.error_interval_spin = QSpinBox()
        self.error_interval_spin.setRange(1, 300)
        self.error_interval_spin.setSuffix(" сек")
        ext_limits_form.addRow("Интервал ошибок:", self.error_interval_spin)
        ext_limits_group.setLayout(ext_limits_form)
        layout.addWidget(ext_limits_group)

        # ---------- Группа "Интерфейс" ----------
        interface_group = QGroupBox("Интерфейс")
        interface_form = QFormLayout()
        self.anim_timeout_spin = QSpinBox()
        self.anim_timeout_spin.setRange(100, 5000)
        self.anim_timeout_spin.setSuffix(" мс")
        interface_form.addRow("Таймаут анимации:", self.anim_timeout_spin)
        interface_group.setLayout(interface_form)
        layout.addWidget(interface_group)

        # ---------- Группа "Сессия" ----------
        session_group = QGroupBox("Сессия")
        session_form = QFormLayout()
        self.session_max_size_spin = QSpinBox()
        self.session_max_size_spin.setRange(1, 100)
        self.session_max_size_spin.setSuffix(" МБ")
        session_form.addRow("Макс. размер файла сессии:", self.session_max_size_spin)
        self.session_max_fails_spin = QSpinBox()
        self.session_max_fails_spin.setRange(0, 10)
        session_form.addRow("Макс. попыток восстановления:", self.session_max_fails_spin)
        session_group.setLayout(session_form)
        layout.addWidget(session_group)

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

        outer_layout = QVBoxLayout(self)
        outer_layout.addWidget(main_scroll)
        self.setLayout(outer_layout)

        self.refresh_all()

    def refresh_all(self):
        """Перечитывает все настройки из менеджера и обновляет виджеты."""
        self.profile_path_edit.setText(self.settings.get("profile_path", ""))
        self.user_agent_edit.setText(self.settings.get("browser_config.user_agent") or "")
        self.js_checkbox.setChecked(self.settings.get("browser_config.javascript_enabled", True))
        self.images_checkbox.setChecked(self.settings.get("browser_config.images_enabled", True))

        # Лимиты вкладок
        self.max_tabs_spin.setValue(self.settings.get("tab_limits.max_tabs"))
        self.reload_limit_spin.setValue(self.settings.get("tab_limits.reload_limit"))
        self.reload_interval_spin.setValue(self.settings.get("tab_limits.reload_interval_sec"))

        # Лимиты ресурсов
        self.max_mem_spin.setValue(self.settings.get("resource_limits.max_memory_percent"))
        self.max_cpu_spin.setValue(self.settings.get("resource_limits.max_cpu_percent"))
        self.monitor_interval_spin.setValue(self.settings.get("resource_limits.monitor_interval_ms"))

        # Лимиты расширений
        self.max_ext_size_spin.setValue(self.settings.get("extension_limits.max_size_mb"))
        self.max_errors_spin.setValue(self.settings.get("extension_limits.max_errors_per_interval"))
        self.error_interval_spin.setValue(self.settings.get("extension_limits.error_interval_sec"))

        # Интерфейс
        self.anim_timeout_spin.setValue(self.settings.get("interface.animation_timeout_ms"))

        # Сессия
        self.session_max_size_spin.setValue(self.settings.get("session.max_size_mb"))
        self.session_max_fails_spin.setValue(self.settings.get("session.max_restore_fails"))

        self.refresh_extensions_list()
        self.refresh_builtin_extensions_list()

    def browse_profile_path(self):
        path = QFileDialog.getExistingDirectory(self, "Выберите папку профиля")
        if path:
            self.profile_path_edit.setText(path)

    def save_all_settings(self):
        try:
            # Профиль и браузер
            self.settings.set("profile_path", self.profile_path_edit.text().strip())
            self.settings.set("browser_config.user_agent", self.user_agent_edit.text().strip() or None)
            self.settings.set("browser_config.javascript_enabled", self.js_checkbox.isChecked())
            self.settings.set("browser_config.images_enabled", self.images_checkbox.isChecked())

            # Лимиты вкладок
            self.settings.set("tab_limits.max_tabs", self.max_tabs_spin.value())
            self.settings.set("tab_limits.reload_limit", self.reload_limit_spin.value())
            self.settings.set("tab_limits.reload_interval_sec", self.reload_interval_spin.value())

            # Лимиты ресурсов
            self.settings.set("resource_limits.max_memory_percent", self.max_mem_spin.value())
            self.settings.set("resource_limits.max_cpu_percent", self.max_cpu_spin.value())
            self.settings.set("resource_limits.monitor_interval_ms", self.monitor_interval_spin.value())

            # Лимиты расширений
            self.settings.set("extension_limits.max_size_mb", self.max_ext_size_spin.value())
            self.settings.set("extension_limits.max_errors_per_interval", self.max_errors_spin.value())
            self.settings.set("extension_limits.error_interval_sec", self.error_interval_spin.value())

            # Интерфейс
            self.settings.set("interface.animation_timeout_ms", self.anim_timeout_spin.value())

            # Сессия
            self.settings.set("session.max_size_mb", self.session_max_size_spin.value())
            self.settings.set("session.max_restore_fails", self.session_max_fails_spin.value())

            self.settings.save()

            # Применяем настройки к профилю
            if self.profile:
                self.profile.setHttpUserAgent(self.settings.get("browser_config.user_agent") or "")
                ws = self.profile.settings()
                ws.setAttribute(ws.WebAttribute.JavascriptEnabled, self.js_checkbox.isChecked())
                ws.setAttribute(ws.WebAttribute.AutoLoadImages, self.images_checkbox.isChecked())

            QMessageBox.information(self, "Сохранено", "Настройки успешно сохранены.")
        except Exception as e:
            browser_logger.error(f"Ошибка сохранения настроек: {e}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить настройки:\n{e}")

    # ================== WebEngine-расширения ==================
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

    # ================== Встроенные расширения ==================
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