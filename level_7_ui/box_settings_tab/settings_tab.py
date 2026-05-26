from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QFileDialog, QMessageBox, QCheckBox,
    QFormLayout, QSpinBox, QScrollArea, QSizePolicy, QComboBox,
    QDoubleSpinBox, QInputDialog
)
from level_0.level_base import Box
from logger import browser_logger

class CollapsibleSection(QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.toggle_btn = QPushButton(title)
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(False)
        self.toggle_btn.clicked.connect(self._toggle)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                text-align: left; padding: 8px; border: 1px solid #999; border-radius: 4px; background-color: #f0f0f0; font-weight: bold;
            }
            QPushButton:checked {
                background-color: #e0e0e0; border-bottom-left-radius: 0px; border-bottom-right-radius: 0px;
            }
        """)
        layout.addWidget(self.toggle_btn)

        self.content_area = QWidget()
        self.content_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.content_area.setVisible(False)
        layout.addWidget(self.content_area)

        self._animation = None

    def setContentLayout(self, layout):
        self.content_area.setLayout(layout)
        self.content_area.adjustSize()

    def _toggle(self):
        if self.toggle_btn.isChecked():
            self._expand()
        else:
            self._collapse()

    def _expand(self):
        self._animate(True)

    def _collapse(self):
        self._animate(False)

    def _animate(self, expand):
        if self._animation and self._animation.state() == QParallelAnimationGroup.State.Running:
            self._animation.stop()
        if expand:
            self.content_area.setVisible(True)
            self.content_area.adjustSize()
            target_height = self.content_area.sizeHint().height()
            start_height = 0
        else:
            target_height = 0
            start_height = self.content_area.height()

        self._animation = QParallelAnimationGroup()
        anim = QPropertyAnimation(self.content_area, b"maximumHeight")
        anim.setDuration(300)
        anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        anim.setStartValue(start_height)
        anim.setEndValue(target_height)
        self._animation.addAnimation(anim)
        if not expand:
            self._animation.finished.connect(lambda: self.content_area.setVisible(False))
        self._animation.start()

class SettingsTabBox(Box):
    def __init__(self, settings, ext_level, session_wrapper):
        super().__init__("settings_tab")
        self.settings = settings
        self.ext_level = ext_level
        self.session = session_wrapper
        self._widget = None
        self.user_changed_callback = None
        self.settings_saved_callback = None

        # Существующие поля
        self.homepage_edit = None
        self.restore_session_check = None
        self.profile_path_edit = None
        self.user_agent_edit = None
        self.js_checkbox = None
        self.images_checkbox = None
        self.popup_block_check = None
        self.dnt_check = None
        self.cookies_combo = None
        self.search_url_edit = None
        self.font_size_spin = None
        self.default_zoom_spin = None
        self.theme_combo = None
        self.download_path_edit = None
        self.download_ask_check = None
        self.proxy_type_combo = None
        self.proxy_host_edit = None
        self.proxy_port_spin = None
        self.max_tabs_spin = None
        self.reload_limit_spin = None
        self.reload_interval_spin = None
        self.max_mem_spin = None
        self.max_cpu_spin = None
        self.monitor_interval_spin = None
        self.users_list = None
        self.active_user_label = None
        self.language_combo = None

        # Поля для контекстного меню
        self.ctx_back = None
        self.ctx_forward = None
        self.ctx_reload = None
        self.ctx_save_page = None
        self.ctx_print = None
        self.ctx_copy = None
        self.ctx_paste = None
        self.ctx_select_all = None
        self.ctx_open_link_new_tab = None
        self.ctx_open_link_new_window = None
        self.ctx_copy_link = None
        self.ctx_save_image = None
        self.ctx_copy_image = None

    def get_settings(self):
        return self.settings

    def set_user_changed_callback(self, callback):
        self.user_changed_callback = callback

    def set_settings_saved_callback(self, callback):
        self.settings_saved_callback = callback

    def create_widget(self, parent=None):
        self._widget = QWidget(parent)
        main_scroll = QScrollArea()
        main_scroll.setWidgetResizable(True)
        container = QWidget()
        main_scroll.setWidget(container)
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(8)

        # --- Пользователи ---
        users_section = CollapsibleSection(self.settings.tr("settings.section.users"))
        users_layout = QVBoxLayout()
        self.active_user_label = QLabel()
        users_layout.addWidget(self.active_user_label)
        self.users_list = QListWidget()
        self.users_list.currentRowChanged.connect(self.on_user_selected)
        users_layout.addWidget(self.users_list)
        btn_layout = QHBoxLayout()
        add_btn = QPushButton(self.settings.tr("settings.create_user"))
        add_btn.clicked.connect(self.create_user)
        btn_layout.addWidget(add_btn)
        delete_btn = QPushButton(self.settings.tr("settings.delete_user"))
        delete_btn.clicked.connect(self.delete_user)
        btn_layout.addWidget(delete_btn)
        switch_btn = QPushButton(self.settings.tr("settings.switch_user"))
        switch_btn.clicked.connect(self.switch_to_user)
        btn_layout.addWidget(switch_btn)
        users_layout.addLayout(btn_layout)
        users_section.setContentLayout(users_layout)
        main_layout.addWidget(users_section)

        # --- Локализация ---
        locale_section = CollapsibleSection(self.settings.tr("settings.section.locale"))
        locale_form = QFormLayout()
        self.language_combo = QComboBox()
        available = self.settings.available_languages()
        self.language_combo.addItems(available)
        locale_form.addRow(self.settings.tr("settings.language"), self.language_combo)
        locale_section.setContentLayout(locale_form)
        main_layout.addWidget(locale_section)

        # --- Запуск ---
        startup_section = CollapsibleSection(self.settings.tr("settings.section.startup"))
        startup_form = QFormLayout()
        self.homepage_edit = QLineEdit()
        startup_form.addRow(self.settings.tr("settings.homepage"), self.homepage_edit)
        self.restore_session_check = QCheckBox(self.settings.tr("settings.restore_session"))
        startup_form.addRow(self.restore_session_check)
        startup_section.setContentLayout(startup_form)
        main_layout.addWidget(startup_section)

        # --- Профиль ---
        profile_section = CollapsibleSection(self.settings.tr("settings.section.profile"))
        profile_form = QFormLayout()
        self.profile_path_edit = QLineEdit()
        browse_btn = QPushButton(self.settings.tr("settings.browse"))
        browse_btn.clicked.connect(self.browse_profile_path)
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.profile_path_edit)
        path_layout.addWidget(browse_btn)
        profile_form.addRow(self.settings.tr("settings.profile_path"), path_layout)
        profile_section.setContentLayout(profile_form)
        main_layout.addWidget(profile_section)

        # --- Параметры браузера ---
        browser_section = CollapsibleSection(self.settings.tr("settings.section.browser"))
        browser_form = QFormLayout()
        self.user_agent_edit = QLineEdit()
        browser_form.addRow(self.settings.tr("settings.user_agent"), self.user_agent_edit)
        self.js_checkbox = QCheckBox(self.settings.tr("settings.javascript"))
        self.js_checkbox.setChecked(True)
        browser_form.addRow("", self.js_checkbox)
        self.images_checkbox = QCheckBox(self.settings.tr("settings.images"))
        self.images_checkbox.setChecked(True)
        browser_form.addRow("", self.images_checkbox)
        browser_section.setContentLayout(browser_form)
        main_layout.addWidget(browser_section)

        # --- Приватность и безопасность ---
        privacy_section = CollapsibleSection(self.settings.tr("settings.section.privacy"))
        privacy_form = QFormLayout()
        self.popup_block_check = QCheckBox(self.settings.tr("settings.block_popups"))
        privacy_form.addRow(self.popup_block_check)
        self.dnt_check = QCheckBox(self.settings.tr("settings.do_not_track"))
        privacy_form.addRow(self.dnt_check)
        self.cookies_combo = QComboBox()
        self.cookies_combo.addItems([
            self.settings.tr("cookies.all"),
            self.settings.tr("cookies.third_party"),
            self.settings.tr("cookies.none")
        ])
        privacy_form.addRow(self.settings.tr("settings.cookies"), self.cookies_combo)
        privacy_section.setContentLayout(privacy_form)
        main_layout.addWidget(privacy_section)

        # --- Контекстное меню ---
        context_menu_section = CollapsibleSection(self.settings.tr("settings.section.context_menu"))
        context_form = QFormLayout()
        self.ctx_back = QCheckBox(self.settings.tr("settings.context_menu.back"))
        self.ctx_forward = QCheckBox(self.settings.tr("settings.context_menu.forward"))
        self.ctx_reload = QCheckBox(self.settings.tr("settings.context_menu.reload"))
        self.ctx_save_page = QCheckBox(self.settings.tr("settings.context_menu.save_page"))
        self.ctx_print = QCheckBox(self.settings.tr("settings.context_menu.print"))
        self.ctx_copy = QCheckBox(self.settings.tr("settings.context_menu.copy"))
        self.ctx_paste = QCheckBox(self.settings.tr("settings.context_menu.paste"))
        self.ctx_select_all = QCheckBox(self.settings.tr("settings.context_menu.select_all"))
        self.ctx_open_link_new_tab = QCheckBox(self.settings.tr("settings.context_menu.open_link_new_tab"))
        self.ctx_open_link_new_window = QCheckBox(self.settings.tr("settings.context_menu.open_link_new_window"))
        self.ctx_copy_link = QCheckBox(self.settings.tr("settings.context_menu.copy_link"))
        self.ctx_save_image = QCheckBox(self.settings.tr("settings.context_menu.save_image"))
        self.ctx_copy_image = QCheckBox(self.settings.tr("settings.context_menu.copy_image"))

        # Группируем по смыслу
        context_form.addRow(self.settings.tr("context_menu.back"), self.ctx_back)
        context_form.addRow(self.settings.tr("context_menu.forward"), self.ctx_forward)
        context_form.addRow(self.settings.tr("context_menu.reload"), self.ctx_reload)
        context_form.addRow(self.settings.tr("context_menu.save_page"), self.ctx_save_page)
        context_form.addRow(self.settings.tr("context_menu.print"), self.ctx_print)
        context_form.addRow(self.settings.tr("context_menu.copy"), self.ctx_copy)
        context_form.addRow(self.settings.tr("context_menu.paste"), self.ctx_paste)
        context_form.addRow(self.settings.tr("context_menu.select_all"), self.ctx_select_all)
        context_form.addRow(self.settings.tr("context_menu.open_link_new_tab"), self.ctx_open_link_new_tab)
        context_form.addRow(self.settings.tr("context_menu.open_link_new_window"), self.ctx_open_link_new_window)
        context_form.addRow(self.settings.tr("context_menu.copy_link"), self.ctx_copy_link)
        context_form.addRow(self.settings.tr("context_menu.save_image"), self.ctx_save_image)
        context_form.addRow(self.settings.tr("context_menu.copy_image"), self.ctx_copy_image)

        context_menu_section.setContentLayout(context_form)
        main_layout.addWidget(context_menu_section)

        # --- Поиск ---
        search_section = CollapsibleSection(self.settings.tr("settings.section.search"))
        search_form = QFormLayout()
        self.search_url_edit = QLineEdit()
        search_form.addRow(self.settings.tr("settings.search_url"), self.search_url_edit)
        search_section.setContentLayout(search_form)
        main_layout.addWidget(search_section)

        # --- Внешний вид ---
        appearance_section = CollapsibleSection(self.settings.tr("settings.section.appearance"))
        appearance_form = QFormLayout()
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 72)
        appearance_form.addRow(self.settings.tr("settings.font_size"), self.font_size_spin)
        self.default_zoom_spin = QDoubleSpinBox()
        self.default_zoom_spin.setRange(0.25, 5.0)
        self.default_zoom_spin.setSingleStep(0.1)
        self.default_zoom_spin.setDecimals(1)
        appearance_form.addRow(self.settings.tr("settings.default_zoom"), self.default_zoom_spin)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems([
            self.settings.tr("theme.light"),
            self.settings.tr("theme.dark"),
            self.settings.tr("theme.system")
        ])
        appearance_form.addRow(self.settings.tr("settings.theme"), self.theme_combo)
        appearance_section.setContentLayout(appearance_form)
        main_layout.addWidget(appearance_section)

        # --- Загрузки ---
        downloads_section = CollapsibleSection(self.settings.tr("settings.section.downloads"))
        downloads_form = QFormLayout()
        self.download_path_edit = QLineEdit()
        dl_browse_btn = QPushButton(self.settings.tr("settings.browse"))
        dl_browse_btn.clicked.connect(self.browse_download_path)
        dl_path_layout = QHBoxLayout()
        dl_path_layout.addWidget(self.download_path_edit)
        dl_path_layout.addWidget(dl_browse_btn)
        downloads_form.addRow(self.settings.tr("settings.download_path"), dl_path_layout)
        self.download_ask_check = QCheckBox(self.settings.tr("settings.ask_before_save"))
        downloads_form.addRow(self.download_ask_check)
        downloads_section.setContentLayout(downloads_form)
        main_layout.addWidget(downloads_section)

        # --- Прокси ---
        proxy_section = CollapsibleSection(self.settings.tr("settings.section.proxy"))
        proxy_form = QFormLayout()
        self.proxy_type_combo = QComboBox()
        self.proxy_type_combo.addItems([
            self.settings.tr("proxy.none"), "HTTP", "SOCKS5"
        ])
        proxy_form.addRow(self.settings.tr("settings.proxy_type"), self.proxy_type_combo)
        self.proxy_host_edit = QLineEdit()
        proxy_form.addRow(self.settings.tr("settings.proxy_host"), self.proxy_host_edit)
        self.proxy_port_spin = QSpinBox()
        self.proxy_port_spin.setRange(1, 65535)
        proxy_form.addRow(self.settings.tr("settings.proxy_port"), self.proxy_port_spin)
        proxy_section.setContentLayout(proxy_form)
        main_layout.addWidget(proxy_section)

        # --- Лимиты вкладок ---
        tabs_limits_section = CollapsibleSection(self.settings.tr("settings.section.tabs_limits"))
        tabs_form = QFormLayout()
        self.max_tabs_spin = QSpinBox()
        self.max_tabs_spin.setRange(1, 200)
        tabs_form.addRow(self.settings.tr("settings.max_tabs"), self.max_tabs_spin)
        self.reload_limit_spin = QSpinBox()
        self.reload_limit_spin.setRange(1, 50)
        tabs_form.addRow(self.settings.tr("settings.reload_limit"), self.reload_limit_spin)
        self.reload_interval_spin = QSpinBox()
        self.reload_interval_spin.setRange(5, 300)
        tabs_form.addRow(self.settings.tr("settings.reload_interval"), self.reload_interval_spin)
        tabs_limits_section.setContentLayout(tabs_form)
        main_layout.addWidget(tabs_limits_section)

        # --- Лимиты ресурсов ---
        resource_section = CollapsibleSection(self.settings.tr("settings.section.resource_limits"))
        resource_form = QFormLayout()
        self.max_mem_spin = QSpinBox()
        self.max_mem_spin.setRange(30, 100)
        resource_form.addRow(self.settings.tr("settings.max_memory"), self.max_mem_spin)
        self.max_cpu_spin = QSpinBox()
        self.max_cpu_spin.setRange(30, 100)
        resource_form.addRow(self.settings.tr("settings.max_cpu"), self.max_cpu_spin)
        self.monitor_interval_spin = QSpinBox()
        self.monitor_interval_spin.setRange(1000, 60000)
        self.monitor_interval_spin.setSingleStep(1000)
        resource_form.addRow(self.settings.tr("settings.monitor_interval"), self.monitor_interval_spin)
        resource_section.setContentLayout(resource_form)
        main_layout.addWidget(resource_section)

        # Кнопки действий
        button_layout = QHBoxLayout()
        save_btn = QPushButton(self.settings.tr("settings.save"))
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        reset_btn = QPushButton(self.settings.tr("settings.reset"))
        reset_btn.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(reset_btn)
        main_layout.addLayout(button_layout)
        main_layout.addStretch()

        self._widget.setLayout(QVBoxLayout())
        self._widget.layout().addWidget(main_scroll)
        self.refresh_all()
        return self._widget

    def browse_profile_path(self):
        path = QFileDialog.getExistingDirectory(self._widget, "Выберите папку профиля")
        if path:
            self.profile_path_edit.setText(path)

    def browse_download_path(self):
        path = QFileDialog.getExistingDirectory(self._widget, "Выберите папку для загрузок")
        if path:
            self.download_path_edit.setText(path)

    def refresh_all(self):
        if not self.settings:
            return
        self.refresh_users_list()
        lang = self.settings.get_current_lang()
        idx = self.language_combo.findText(lang)
        if idx >= 0:
            self.language_combo.setCurrentIndex(idx)
        self.homepage_edit.setText(self.settings.get("startup.homepage", "about:blank"))
        self.restore_session_check.setChecked(self.settings.get("startup.restore_session", True))
        self.profile_path_edit.setText(self.settings.get("profile_path", "browser_data"))
        self.user_agent_edit.setText(self.settings.get("user_agent", ""))
        self.js_checkbox.setChecked(self.settings.get("enable_javascript", True))
        self.images_checkbox.setChecked(self.settings.get("enable_images", True))
        self.popup_block_check.setChecked(self.settings.get("privacy.block_popups", True))
        self.dnt_check.setChecked(self.settings.get("privacy.do_not_track", False))
        cookies_idx = self.settings.get("privacy.cookie_policy", 0)
        if 0 <= cookies_idx < self.cookies_combo.count():
            self.cookies_combo.setCurrentIndex(cookies_idx)
        self.search_url_edit.setText(self.settings.get("search.url", "https://www.google.com/search?q=%s"))
        self.font_size_spin.setValue(self.settings.get("appearance.font_size", 16))
        self.default_zoom_spin.setValue(self.settings.get("appearance.default_zoom", 1.0))
        theme = self.settings.get("appearance.theme", self.settings.tr("theme.system"))
        t_idx = self.theme_combo.findText(theme)
        if t_idx >= 0:
            self.theme_combo.setCurrentIndex(t_idx)
        self.download_path_edit.setText(self.settings.get("downloads.path", ""))
        self.download_ask_check.setChecked(self.settings.get("downloads.ask_before_save", True))
        proxy_type = self.settings.get("proxy.type", self.settings.tr("proxy.none"))
        p_idx = self.proxy_type_combo.findText(proxy_type)
        if p_idx >= 0:
            self.proxy_type_combo.setCurrentIndex(p_idx)
        self.proxy_host_edit.setText(self.settings.get("proxy.host", ""))
        self.proxy_port_spin.setValue(self.settings.get("proxy.port", 8080))
        self.max_tabs_spin.setValue(self.settings.get("tab_limits.max_tabs", 50))
        self.reload_limit_spin.setValue(self.settings.get("tab_limits.reload_limit", 5))
        self.reload_interval_spin.setValue(self.settings.get("tab_limits.reload_interval_sec", 30))
        self.max_mem_spin.setValue(self.settings.get("resource_limits.max_memory_percent", 80))
        self.max_cpu_spin.setValue(self.settings.get("resource_limits.max_cpu_percent", 90))
        self.monitor_interval_spin.setValue(self.settings.get("resource_limits.monitor_interval_ms", 5000))

        # Контекстное меню
        ctx_defaults = {
            "back": True, "forward": True, "reload": True, "save_page": True,
            "print": True, "copy": True, "paste": True, "select_all": True,
            "open_link_new_tab": True, "open_link_new_window": True,
            "copy_link": True, "save_image": True, "copy_image": True
        }
        ctx = self.settings.get("context_menu", ctx_defaults)
        self.ctx_back.setChecked(ctx.get("back", True))
        self.ctx_forward.setChecked(ctx.get("forward", True))
        self.ctx_reload.setChecked(ctx.get("reload", True))
        self.ctx_save_page.setChecked(ctx.get("save_page", True))
        self.ctx_print.setChecked(ctx.get("print", True))
        self.ctx_copy.setChecked(ctx.get("copy", True))
        self.ctx_paste.setChecked(ctx.get("paste", True))
        self.ctx_select_all.setChecked(ctx.get("select_all", True))
        self.ctx_open_link_new_tab.setChecked(ctx.get("open_link_new_tab", True))
        self.ctx_open_link_new_window.setChecked(ctx.get("open_link_new_window", True))
        self.ctx_copy_link.setChecked(ctx.get("copy_link", True))
        self.ctx_save_image.setChecked(ctx.get("save_image", True))
        self.ctx_copy_image.setChecked(ctx.get("copy_image", True))

    def save_settings(self):
        if not self.settings:
            QMessageBox.warning(self._widget, "Ошибка", self.settings.tr("settings.error.no_settings"))
            return

        old_values = {
            "locale": self.settings.get_current_lang(),
            "startup.homepage": self.settings.get("startup.homepage", "about:blank"),
            "startup.restore_session": self.settings.get("startup.restore_session", True),
            "profile_path": self.settings.get("profile_path", "browser_data"),
            "user_agent": self.settings.get("user_agent", ""),
            "enable_javascript": self.settings.get("enable_javascript", True),
            "enable_images": self.settings.get("enable_images", True),
            "privacy.block_popups": self.settings.get("privacy.block_popups", True),
            "privacy.do_not_track": self.settings.get("privacy.do_not_track", False),
            "privacy.cookie_policy": self.settings.get("privacy.cookie_policy", 0),
            "search.url": self.settings.get("search.url", "https://www.google.com/search?q=%s"),
            "appearance.font_size": self.settings.get("appearance.font_size", 16),
            "appearance.default_zoom": self.settings.get("appearance.default_zoom", 1.0),
            "appearance.theme": self.settings.get("appearance.theme", self.settings.tr("theme.system")),
            "downloads.path": self.settings.get("downloads.path", ""),
            "downloads.ask_before_save": self.settings.get("downloads.ask_before_save", True),
            "proxy.type": self.settings.get("proxy.type", self.settings.tr("proxy.none")),
            "proxy.host": self.settings.get("proxy.host", ""),
            "proxy.port": self.settings.get("proxy.port", 8080),
            "tab_limits.max_tabs": self.settings.get("tab_limits.max_tabs", 50),
            "tab_limits.reload_limit": self.settings.get("tab_limits.reload_limit", 5),
            "tab_limits.reload_interval_sec": self.settings.get("tab_limits.reload_interval_sec", 30),
            "resource_limits.max_memory_percent": self.settings.get("resource_limits.max_memory_percent", 80),
            "resource_limits.max_cpu_percent": self.settings.get("resource_limits.max_cpu_percent", 90),
            "resource_limits.monitor_interval_ms": self.settings.get("resource_limits.monitor_interval_ms", 5000),
            "context_menu": self.settings.get("context_menu", {})
        }

        new_lang = self.language_combo.currentText()
        old_lang = self.settings.get_current_lang()
        if new_lang != old_lang:
            self.settings.load_language(new_lang)

        self.settings.set("startup.homepage", self.homepage_edit.text().strip())
        self.settings.set("startup.restore_session", self.restore_session_check.isChecked())
        self.settings.set("profile_path", self.profile_path_edit.text().strip())
        self.settings.set("user_agent", self.user_agent_edit.text().strip())
        self.settings.set("enable_javascript", self.js_checkbox.isChecked())
        self.settings.set("enable_images", self.images_checkbox.isChecked())
        self.settings.set("privacy.block_popups", self.popup_block_check.isChecked())
        self.settings.set("privacy.do_not_track", self.dnt_check.isChecked())
        self.settings.set("privacy.cookie_policy", self.cookies_combo.currentIndex())
        self.settings.set("search.url", self.search_url_edit.text().strip())
        self.settings.set("appearance.font_size", self.font_size_spin.value())
        self.settings.set("appearance.default_zoom", self.default_zoom_spin.value())
        self.settings.set("appearance.theme", self.theme_combo.currentText())
        self.settings.set("downloads.path", self.download_path_edit.text().strip())
        self.settings.set("downloads.ask_before_save", self.download_ask_check.isChecked())
        self.settings.set("proxy.type", self.proxy_type_combo.currentText())
        self.settings.set("proxy.host", self.proxy_host_edit.text().strip())
        self.settings.set("proxy.port", self.proxy_port_spin.value())
        self.settings.set("tab_limits.max_tabs", self.max_tabs_spin.value())
        self.settings.set("tab_limits.reload_limit", self.reload_limit_spin.value())
        self.settings.set("tab_limits.reload_interval_sec", self.reload_interval_spin.value())
        self.settings.set("resource_limits.max_memory_percent", self.max_mem_spin.value())
        self.settings.set("resource_limits.max_cpu_percent", self.max_cpu_spin.value())
        self.settings.set("resource_limits.monitor_interval_ms", self.monitor_interval_spin.value())

        ctx = {
            "back": self.ctx_back.isChecked(),
            "forward": self.ctx_forward.isChecked(),
            "reload": self.ctx_reload.isChecked(),
            "save_page": self.ctx_save_page.isChecked(),
            "print": self.ctx_print.isChecked(),
            "copy": self.ctx_copy.isChecked(),
            "paste": self.ctx_paste.isChecked(),
            "select_all": self.ctx_select_all.isChecked(),
            "open_link_new_tab": self.ctx_open_link_new_tab.isChecked(),
            "open_link_new_window": self.ctx_open_link_new_window.isChecked(),
            "copy_link": self.ctx_copy_link.isChecked(),
            "save_image": self.ctx_save_image.isChecked(),
            "copy_image": self.ctx_copy_image.isChecked()
        }
        self.settings.set("context_menu", ctx)

        changes = {}
        for key, old_val in old_values.items():
            new_val = self.settings.get(key)
            if str(old_val) != str(new_val):
                changes[key] = {"old": str(old_val), "new": str(new_val)}

        if changes:
            self.session.record_settings_change(changes)

        self.settings.save_settings()
        QMessageBox.information(self._widget, "Сохранено", self.settings.tr("settings.saved"))
        browser_logger.info("Настройки сохранены через UI")
        if self.settings_saved_callback:
            self.settings_saved_callback()

    def reset_to_defaults(self):
        defaults = {
            "locale": "ru",
            "startup.homepage": "about:blank",
            "startup.restore_session": True,
            "profile_path": "browser_data",
            "user_agent": "",
            "enable_javascript": True,
            "enable_images": True,
            "privacy.block_popups": True,
            "privacy.do_not_track": False,
            "privacy.cookie_policy": 0,
            "search.url": "https://www.google.com/search?q=%s",
            "appearance.font_size": 16,
            "appearance.default_zoom": 1.0,
            "appearance.theme": self.settings.tr("theme.system"),
            "downloads.path": "",
            "downloads.ask_before_save": True,
            "proxy.type": self.settings.tr("proxy.none"),
            "proxy.host": "",
            "proxy.port": 8080,
            "tab_limits.max_tabs": 50,
            "tab_limits.reload_limit": 5,
            "tab_limits.reload_interval_sec": 30,
            "resource_limits.max_memory_percent": 80,
            "resource_limits.max_cpu_percent": 90,
            "resource_limits.monitor_interval_ms": 5000,
            "context_menu": {
                "back": True, "forward": True, "reload": True, "save_page": True,
                "print": True, "copy": True, "paste": True, "select_all": True,
                "open_link_new_tab": True, "open_link_new_window": True,
                "copy_link": True, "save_image": True, "copy_image": True
            }
        }
        for k, v in defaults.items():
            self.settings.set(k, v)
        self.settings.save_settings()
        self.refresh_all()
        QMessageBox.information(self._widget, "Сброс", self.settings.tr("settings.reset_done"))
        browser_logger.info("Настройки сброшены к значениям по умолчанию")

    def get_users(self):
        return self.settings.get("users.list", ["Default"])

    def get_active_user(self):
        return self.settings.get("users.active", "Default")

    def set_users(self, users):
        self.settings.set("users.list", users)
        self.settings.save_settings()

    def set_active_user(self, name):
        self.settings.set("users.active", name)
        self.settings.save_settings()

    def refresh_users_list(self):
        self.users_list.clear()
        users = self.get_users()
        active = self.get_active_user()
        for user in users:
            self.users_list.addItem(user)
        self.active_user_label.setText(f"{self.settings.tr('settings.active_user')} {active}")
        for i in range(self.users_list.count()):
            if self.users_list.item(i).text() == active:
                self.users_list.setCurrentRow(i)
                break

    def on_user_selected(self, row):
        pass

    def create_user(self):
        name, ok = QInputDialog.getText(self._widget, "Новый пользователь", "Имя:")
        if ok and name.strip():
            name = name.strip()
            users = self.get_users()
            if name in users:
                QMessageBox.warning(self._widget, "Ошибка", self.settings.tr("settings.error.user_exists"))
                return
            users.append(name)
            self.set_users(users)
            self.refresh_users_list()

    def delete_user(self):
        current = self.users_list.currentItem()
        if not current:
            QMessageBox.warning(self._widget, "Ошибка", self.settings.tr("settings.error.select_user"))
            return
        name = current.text()
        if name == "Default":
            QMessageBox.warning(self._widget, "Ошибка", self.settings.tr("settings.error.cant_delete_default"))
            return
        users = self.get_users()
        users.remove(name)
        self.set_users(users)
        if self.get_active_user() == name:
            self.set_active_user("Default")
        self.refresh_users_list()

    def switch_to_user(self):
        current = self.users_list.currentItem()
        if not current:
            QMessageBox.warning(self._widget, "Ошибка", self.settings.tr("settings.error.select_user_switch"))
            return
        name = current.text()
        if name == self.get_active_user():
            return
        self.set_active_user(name)
        self.refresh_users_list()
        if self.user_changed_callback:
            self.user_changed_callback(name)

    def retranslate_ui(self):
        pass

    def refresh_extensions_list(self, ext_list_widget=None):
        pass