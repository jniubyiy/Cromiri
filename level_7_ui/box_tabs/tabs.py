from PyQt6.QtCore import QUrl, QTimer
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QTabBar,
    QStackedWidget, QPushButton
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from page_loader import PageLoader
from level_0.level_base import Box
from logger import browser_logger


class TabsBox(Box):
    def __init__(self, settings, session, style_script_wrapper, extensions_wrapper):
        super().__init__("tabs")
        self.settings = settings
        self.session = session
        self.style_script_wrapper = style_script_wrapper
        self.extensions_wrapper = extensions_wrapper
        self._widget = None
        self.tab_bar = None
        self.toggle_main_btn = None
        self.new_tab_btn = None
        self.stack = None
        self._loaders = {}
        self._reload_counts = {}
        self.resource_timer = None
        self._toggle_main_cb = None
        self.toolbar = None

    def set_stack(self, stack: QStackedWidget):
        self.stack = stack

    def set_toggle_main_callback(self, callback):
        self._toggle_main_cb = callback

    def set_toolbar(self, toolbar_box):
        self.toolbar = toolbar_box

    def _update_toolbar(self, url):
        if self.toolbar:
            self.toolbar.call("update_address_bar", url)

    def create_widget(self, parent=None) -> QWidget:
        self._widget = QWidget(parent)
        layout = QHBoxLayout(self._widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.toggle_main_btn = QPushButton("◻")
        self.toggle_main_btn.setFixedSize(28, 28)
        self.toggle_main_btn.setToolTip(self.settings.tr("tab.toggle_main"))
        self.toggle_main_btn.clicked.connect(self._on_toggle_main)
        layout.addWidget(self.toggle_main_btn)

        self.tab_bar = QTabBar()
        self.tab_bar.setMovable(True)
        self.tab_bar.setTabsClosable(True)
        self.tab_bar.setExpanding(False)
        self.tab_bar.currentChanged.connect(self.on_tab_changed)
        self.tab_bar.tabCloseRequested.connect(self.close_tab)
        layout.addWidget(self.tab_bar)

        self.new_tab_btn = QPushButton("+")
        self.new_tab_btn.setFixedSize(28, 28)
        self.new_tab_btn.setToolTip(self.settings.tr("tab.new_tab"))
        self.new_tab_btn.clicked.connect(lambda: self.add_new_page_tab(QUrl("about:blank")))
        layout.addWidget(self.new_tab_btn)

        layout.addStretch()

        self.resource_timer = QTimer()
        self._update_timer_interval()
        self.resource_timer.timeout.connect(self._check_resource_usage)
        self.resource_timer.start()

        return self._widget

    def _on_toggle_main(self):
        if self._toggle_main_cb:
            self._toggle_main_cb()

    def _update_timer_interval(self):
        interval = self.settings.get("resource_limits.monitor_interval_ms", 5000)
        if self.resource_timer:
            self.resource_timer.setInterval(interval)

    def apply_settings(self):
        self._update_timer_interval()

    def add_new_page_tab(self, url=None, title=None):
        if self.stack is None:
            return
        max_tabs = self.settings.get("tab_limits.max_tabs", 50)
        if self.tab_bar.count() >= max_tabs:
            browser_logger.warning("Достигнут лимит вкладок")
            return
        view = QWebEngineView()
        loader = PageLoader(view)
        self._loaders[view] = loader
        self._reload_counts[view] = 0

        view.urlChanged.connect(lambda u, v=view: self.on_url_changed(u, v))
        view.titleChanged.connect(lambda t, v=view: self._on_title_changed(t, v))
        view.loadProgress.connect(lambda p, v=view: self._on_load_progress(p, v))
        view.page().renderProcessTerminated.connect(
            lambda status, code, v=view: self._on_render_process_crashed(v)
        )

        self.style_script_wrapper.call("apply_styles", view)

        idx = self.stack.addWidget(view)
        tab_idx = self.tab_bar.addTab(self.settings.tr("tab.loading"))
        self.stack.setCurrentIndex(idx)
        self.tab_bar.setCurrentIndex(tab_idx)

        if url and url.isValid():
            loader.load_url(url.toString())
        else:
            loader.load_url("about:blank")

        # Инжекция скриптов расширений (сразу, как для пользовательских скриптов)
        self._inject_scripts_to_view(view)

    def _inject_scripts_to_view(self, view):
        url = view.url().toString()
        # Пользовательские скрипты
        self.style_script_wrapper.call("inject_scripts", view, view.url())
        # Встроенные расширения
        if self.extensions_wrapper:
            builtin_exts = self.extensions_wrapper.get_builtin_extensions()
            for ext_cls in builtin_exts:
                if not self.extensions_wrapper.is_builtin_extension_enabled(ext_cls.name):
                    continue
                if ext_cls.matches(url):
                    script = ext_cls.get_script()
                    view.page().runJavaScript(script)
                    browser_logger.info(f"Расширение '{ext_cls.name}' внедрено на {url}")

    def on_tab_changed(self, index):
        if index < 0 or not self.stack:
            return
        self.stack.setCurrentIndex(index)
        widget = self.stack.widget(index)
        if isinstance(widget, QWebEngineView):
            self._update_toolbar(widget.url())

    def on_url_changed(self, url, view):
        if self.stack and self.stack.currentWidget() is view:
            self._update_toolbar(url)
        self._inject_scripts_to_view(view)

    def close_tab(self, index):
        if index < 0 or not self.stack:
            return
        self.tab_bar.removeTab(index)
        widget = self.stack.widget(index)
        if widget:
            self.stack.removeWidget(widget)
            if widget in self._loaders:
                del self._loaders[widget]
            if widget in self._reload_counts:
                del self._reload_counts[widget]
            widget.deleteLater()
        if self.tab_bar.count() == 0:
            self.add_new_page_tab(QUrl("about:blank"))

    def active_loader(self):
        if self.stack and self.stack.currentWidget() in self._loaders:
            return self._loaders[self.stack.currentWidget()]
        return None

    def restore_session(self):
        states = self.session.get_tab_states()
        if states:
            for item in states:
                url = item.get("url") if isinstance(item, dict) else str(item)
                self.add_new_page_tab(QUrl(url))

    def save_session(self):
        urls = []
        for i in range(self.stack.count()):
            w = self.stack.widget(i)
            if isinstance(w, QWebEngineView):
                urls.append(w.url().toString())
        self.session.set_tab_states(urls)
        self.session.save_session()

    def _on_title_changed(self, title, view):
        if self.stack is None:
            return
        for i in range(self.stack.count()):
            if self.stack.widget(i) is view:
                self.tab_bar.setTabText(i, title[:30])
                break

    def _on_load_progress(self, progress, view):
        pass

    def _check_resource_usage(self):
        pass

    def _on_render_process_crashed(self, view):
        browser_logger.error(self.settings.tr("error.render_process"))
        reload_limit = self.settings.get("tab_limits.reload_limit", 5)
        if view in self._reload_counts:
            self._reload_counts[view] += 1
            if self._reload_counts[view] <= reload_limit:
                if view in self._loaders:
                    self._loaders[view].reload()
                return
        view.setHtml(f"<h1>{self.settings.tr('crash.title')}</h1><p>{self.settings.tr('crash.message')}</p>")

    def retranslate_ui(self):
        self.toggle_main_btn.setToolTip(self.settings.tr("tab.toggle_main"))
        self.new_tab_btn.setToolTip(self.settings.tr("tab.new_tab"))