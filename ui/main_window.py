# ui/main_window.py
import sys, os
from PyQt6.QtCore import QUrl, Qt, QTimer, QEvent
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QGroupBox, QListWidget, QListWidgetItem, QFileDialog,
    QMessageBox, QCheckBox, QToolButton, QStackedWidget
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile

from settings import SettingsManager
from extensions import ExtensionManager
from page_loader import PageLoader
from style_manager import StyleManager
from site_scripts import SiteScriptManager
from session import SessionManager
from logger import browser_logger
from extensions_loader import ExtensionsLoader

from ui.main_tabs import MainTabsPanel
from ui.page_tabs import PageTabManager
from ui.toolbars import NavigationToolbar
from ui.tabs.settings_tab import SettingsTab
from ui.tabs.scripts_tab import ScriptsTab


class BrowserUI(QMainWindow):
    def __init__(self, settings: SettingsManager, session: SessionManager, ext_loader: ExtensionsLoader):
        super().__init__()
        browser_logger.info("Инициализация главного окна браузера")
        self.setWindowTitle("Cromiri")
        self.resize(1280, 800)

        self.settings = settings
        self.session = session
        self.ext_loader = ext_loader

        self.session.max_size_mb = self.settings.get("session.max_size_mb", 5)
        self.session.max_restore_fails = self.settings.get("session.max_restore_fails", 3)

        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.setPersistentStoragePath(self.settings.get("profile_path"))
        self.profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)

        self.style_manager = StyleManager(self.settings)
        self.script_manager = SiteScriptManager(self.settings)

        try:
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            main_layout = QVBoxLayout(central_widget)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)

            self.main_tabs_panel = MainTabsPanel()
            main_layout.addWidget(self.main_tabs_panel)

            self.content_stack = QStackedWidget()
            main_layout.addWidget(self.content_stack, 1)

            self.init_view_tab()
            self.settings_tab = SettingsTab(self)
            self.scripts_tab = ScriptsTab(self)

            self.content_stack.addWidget(self.view_tab)      # index 0
            self.content_stack.addWidget(self.settings_tab)  # index 1
            self.content_stack.addWidget(self.scripts_tab)   # index 2

            self.main_tabs_panel.tab_bar.currentChanged.connect(self.on_main_tab_changed)
        except Exception as e:
            browser_logger.exception(f"Критическая ошибка построения GUI: {e}")
            raise SystemExit(1)

        self._restore_session()

        self.ext_manager = None
        self.builtin_ext_mgr = None
        QTimer.singleShot(0, self._load_extensions)

        if not self.page_tabs.views:
            self.page_tabs.add_new_page_tab(QUrl("about:blank"))

        self.installEventFilter(self)
        self.main_tabs_panel.tab_bar.currentChanged.connect(self._on_main_tab_changed_refresh)

        self.main_tabs_visible = True
        self._saved_main_tabs_visible = True

    def _on_main_tab_changed_refresh(self, index):
        if index == 1:
            try:
                self.settings_tab.refresh_all()
            except Exception as e:
                browser_logger.exception("Ошибка обновления вкладки настроек")

    def init_view_tab(self):
        self.view_tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.page_stack = QStackedWidget()
        self.page_tabs = PageTabManager(self, self.page_stack,
                                        toggle_main_tabs_callback=self.toggle_main_tabs)
        layout.addWidget(self.page_tabs)
        self.nav_toolbar = NavigationToolbar(self)
        layout.addWidget(self.nav_toolbar)
        layout.addWidget(self.page_stack, 1)
        self.view_tab.setLayout(layout)

    def toggle_main_tabs(self):
        if self.main_tabs_visible:
            self.main_tabs_panel.hide_panel()
            self.main_tabs_visible = False
        else:
            self.main_tabs_panel.show_panel()
            self.main_tabs_visible = True

    def on_main_tab_changed(self, index):
        self.content_stack.setCurrentIndex(index)
        if index == 0:
            if self._saved_main_tabs_visible and not self.main_tabs_visible:
                self.main_tabs_panel.show_panel()
                self.main_tabs_visible = True
            elif not self._saved_main_tabs_visible and self.main_tabs_visible:
                self.main_tabs_panel.hide_panel()
                self.main_tabs_visible = False
        else:
            self._saved_main_tabs_visible = self.main_tabs_visible
            if not self.main_tabs_visible:
                self.main_tabs_panel.show_panel()
                self.main_tabs_visible = True

    def _restore_session(self):
        # Попытка восстановить сохранённые вкладки
        tab_states = self.session.get_tab_states()
        if tab_states:
            browser_logger.info(f"Восстанавливаю {len(tab_states)} вкладок из сессии")
            self.page_tabs.restore_tabs(tab_states)
            return

        # Если нет сохранённых вкладок, используем старую логику (последний URL)
        if self.session.max_restore_fails <= 0:
            browser_logger.info("Восстановление сессии отключено настройками")
            return
        try:
            nav_history = self.session.history.get("navigation", [])
            if nav_history:
                last_url = nav_history[-1]["url"]
                self.page_tabs.add_new_page_tab(QUrl(last_url))
                browser_logger.info(f"Сессия восстановлена: {last_url}")
        except Exception as e:
            browser_logger.exception(f"Ошибка восстановления сессии: {e}")

    def _load_extensions(self):
        try:
            ext_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "extensions")
            self.ext_manager = ExtensionManager(self.profile, self.settings, ext_dir)
            self.ext_manager.install_all()
            browser_logger.info("WebEngine-расширения установлены")
        except Exception as e:
            browser_logger.exception(f"Ошибка загрузки WebEngine-расширений: {e}")
            self.ext_manager = None

        try:
            from builtin_extensions import BuiltinExtensionManager
            self.builtin_ext_mgr = BuiltinExtensionManager(self)
            for name in self.ext_loader.get_builtin_extension_names():
                try:
                    success = self.builtin_ext_mgr.activate_extension(name)
                    if not success:
                        browser_logger.warning(f"Встроенное расширение '{name}' не активировано")
                except Exception as e:
                    browser_logger.exception(f"Ошибка активации встроенного расширения '{name}': {e}")
            browser_logger.info("Встроенные расширения загружены")
        except Exception as e:
            browser_logger.exception(f"Ошибка загрузки встроенных расширений: {e}")
            self.builtin_ext_mgr = None

        try:
            if hasattr(self, 'settings_tab'):
                self.settings_tab.refresh_extensions_list()
                self.settings_tab.refresh_builtin_extensions_list()
        except Exception as e:
            browser_logger.exception(f"Ошибка обновления списков расширений: {e}")

        try:
            self.nav_toolbar.update_extension_icons()
        except Exception as e:
            browser_logger.exception(f"Ошибка обновления значков расширений: {e}")

    def go_to_url(self):
        if hasattr(self, 'settings_tab'):
            try:
                url = self.settings_tab.url_input.text().strip()
                if url:
                    self.page_tabs.active_loader().load_url(url)
                    self.content_stack.setCurrentIndex(0)
            except Exception as e:
                browser_logger.exception(f"Ошибка перехода по URL: {e}")

    def open_gelbooru(self):
        try:
            self.page_tabs.active_loader().load_gelbooru_all()
            self.content_stack.setCurrentIndex(0)
        except Exception as e:
            browser_logger.exception(f"Ошибка открытия Gelbooru: {e}")

    def on_console_message(self, level, message, line, source):
        try:
            self.session.log_page_event("console", f"level={level}, msg={message}")
        except Exception as e:
            browser_logger.exception(f"Ошибка логирования консольного сообщения: {e}")

    def log_navigation_event(self, url: QUrl, title: str = ""):
        try:
            self.session.log_navigation(url.toString(), title)
        except Exception as e:
            browser_logger.exception(f"Ошибка записи навигации в сессию: {e}")

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
        # Сохраняем состояния вкладок
        try:
            states = self.page_tabs.get_all_tab_states()
            self.session.save_tab_states(states)
        except Exception as e:
            browser_logger.exception(f"Ошибка сохранения состояний вкладок: {e}")

        if self.builtin_ext_mgr:
            try:
                for name in self.builtin_ext_mgr.get_activated_extensions():
                    try:
                        self.builtin_ext_mgr.deactivate_extension(name)
                    except Exception as e:
                        browser_logger.exception(f"Ошибка деактивации расширения {name}: {e}")
            except Exception as e:
                browser_logger.exception(f"Ошибка при деактивации встроенных расширений: {e}")
        try:
            self.session.save()
            browser_logger.info("Сессия сохранена")
        except Exception as e:
            browser_logger.exception(f"Ошибка сохранения сессии: {e}")
        browser_logger.info("Завершение работы браузера")
        super().closeEvent(event)