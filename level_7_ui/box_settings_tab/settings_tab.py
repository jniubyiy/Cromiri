from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QGroupBox, QListWidget, QListWidgetItem, QFileDialog, QMessageBox,
    QCheckBox, QFormLayout, QSpinBox, QScrollArea
)
from logger import browser_logger

class SettingsTabBox:
    def __init__(self, settings, ext_level):
        self.settings = settings
        self.ext_level = ext_level
        self._widget = None
        # элементы интерфейса будут созданы в create_widget
    def create_widget(self, parent=None):
        self._widget = QWidget(parent)
        main_scroll = QScrollArea()
        main_scroll.setWidgetResizable(True)
        container = QWidget()
        main_scroll.setWidget(container)
        layout = QVBoxLayout(container)

        # Профиль
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

        # Параметры браузера
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

        # Лимиты вкладок
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

        # Ресурсы
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

        # Расширения (отображение)
        ext_group = QGroupBox("Расширения")
        ext_layout = QVBoxLayout()
        self.ext_list_widget = QListWidget()
        self.refresh_extensions_list()
        ext_layout.addWidget(QLabel("Установленные расширения:"))
        ext_layout.addWidget(self.ext_list_widget)
        btn_add_ext = QPushButton("➕ Добавить расширение (папка)")
        btn_add_ext.clicked.connect(self.add_extension_dialog)
        ext_layout.addWidget(btn_add_ext)
        btn_rem_ext = QPushButton("➖ Удалить выбранное")
        btn_rem_ext.clicked.connect(self.remove_extension_dialog)
        ext_layout.addWidget(btn_rem_ext)
        ext_group.setLayout(ext_layout)
        layout.addWidget(ext_group)

        # Сохранение
        save_btn = QPushButton("Сохранить все настройки")
        save_btn.clicked.connect(self.save_all_settings)
        layout.addWidget(save_btn)

        main_layout = QVBoxLayout(self._widget)
        main_layout.addWidget(main_scroll)
        self.refresh_all()
        return self._widget

    def browse_profile_path(self):
        path = QFileDialog.getExistingDirectory(self._widget, "Выберите папку профиля")
        if path:
            self.profile_path_edit.setText(path)

    def refresh_all(self):
        self.profile_path_edit.setText(self.settings.get("profile_path", ""))
        self.user_agent_edit.setText(self.settings.get("browser_config.user_agent", ""))
        self.js_checkbox.setChecked(self.settings.get("browser_config.javascript_enabled", True))
        self.images_checkbox.setChecked(self.settings.get("browser_config.images_enabled", True))
        self.max_tabs_spin.setValue(self.settings.get("tab_limits.max_tabs", 50))
        self.reload_limit_spin.setValue(self.settings.get("tab_limits.reload_limit", 5))
        self.reload_interval_spin.setValue(self.settings.get("tab_limits.reload_interval_sec", 30))
        self.max_mem_spin.setValue(self.settings.get("resource_limits.max_memory_percent", 85))
        self.max_cpu_spin.setValue(self.settings.get("resource_limits.max_cpu_percent", 90))
        self.monitor_interval_spin.setValue(self.settings.get("resource_limits.monitor_interval_ms", 5000))
        self.refresh_extensions_list()

    def save_all_settings(self):
        try:
            self.settings.set("profile_path", self.profile_path_edit.text())
            self.settings.set("browser_config.user_agent", self.user_agent_edit.text())
            self.settings.set("browser_config.javascript_enabled", self.js_checkbox.isChecked())
            self.settings.set("browser_config.images_enabled", self.images_checkbox.isChecked())
            self.settings.set("tab_limits.max_tabs", self.max_tabs_spin.value())
            self.settings.set("tab_limits.reload_limit", self.reload_limit_spin.value())
            self.settings.set("tab_limits.reload_interval_sec", self.reload_interval_spin.value())
            self.settings.set("resource_limits.max_memory_percent", self.max_mem_spin.value())
            self.settings.set("resource_limits.max_cpu_percent", self.max_cpu_spin.value())
            self.settings.set("resource_limits.monitor_interval_ms", self.monitor_interval_spin.value())
            self.settings.save_settings()
            QMessageBox.information(self._widget, "Успех", "Настройки сохранены.")
        except Exception as e:
            browser_logger.exception(f"Ошибка сохранения настроек: {e}")
            QMessageBox.critical(self._widget, "Ошибка", f"Не удалось сохранить настройки:\n{e}")

    def refresh_extensions_list(self):
        self.ext_list_widget.clear()
        # В реальном коде нужно получать список из ext_level
        pass

    def add_extension_dialog(self):
        pass

    def remove_extension_dialog(self):
        pass