from PyQt6.QtCore import QUrl, QTimer
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QTabBar, QStackedWidget, QPushButton
from PyQt6.QtWebEngineWidgets import QWebEngineView
from page_loader import PageLoader
from logger import browser_logger

class TabsBox:
    def __init__(self, settings, session, style_script_box):
        self.settings = settings
        self.session = session
        self.style_script_box = style_script_box
        self._widget = None
        self.tab_bar = None
        self.toggle_main_btn = None
        self.new_tab_btn = None
        self.stack = None
        self._loaders = {}
        self._reload_counts = {}
        self.resource_timer = None
        self._toggle_main_cb = None

    def set_stack(self, stack: QStackedWidget):
        self.stack = stack

    def set_toggle_main_callback(self, callback):
        self._toggle_main_cb = callback

    def create_widget(self, parent=None) -> QWidget:
        self._widget = QWidget(parent)
        layout = QHBoxLayout(self._widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.toggle_main_btn = QPushButton("◻")
        self.toggle_main_btn.setFixedSize(28, 28)
        self.toggle_main_btn.setToolTip("Показать/скрыть главные вкладки")
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
        self.new_tab_btn.setToolTip("Новая вкладка")
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

    def add_new_page_tab(self, url=None, title=None):
        if self.stack is None:
            browser_logger.error("TabsBox: стек не назначен")
            return
        max_tabs = self.settings.get("tab_limits.max_tabs", 50)
        if self.tab_bar.count() >= max_tabs:
            browser_logger.warning(f"Достигнут лимит вкладок ({max_tabs})")
            return

        view = QWebEngineView()
        loader = PageLoader(view)

        view.urlChanged.connect(lambda u, v=view: self.on_url_changed(u, v))
        view.page().renderProcessTerminated.connect(
            lambda status, code, v=view: self._on_render_process_crashed(v)
        )

        self.style_script_box.apply_styles(view)
        self.style_script_box.inject_scripts(view, QUrl("about:blank"))

        self.stack.addWidget(view)
        self._loaders[view] = loader
        self._reload_counts[view] = 0

        tab_title = title or "Новая вкладка"
        tab_idx = self.tab_bar.addTab(tab_title)
        self.tab_bar.setCurrentIndex(tab_idx)

        if url:
            browser_logger.info(f"TabsBox: открываю URL: {url.toString()}")
            loader.load_url(url.toString() if hasattr(url, 'toString') else url)
        return view

    def on_tab_changed(self, index):
        if index < 0 or index >= self.stack.count():
            return
        view = self.stack.widget(index)
        if view:
            self.stack.setCurrentWidget(view)

    def on_url_changed(self, url, view):
        if view in self._loaders:
            title = view.page().title() or url.toString()
            for i in range(self.tab_bar.count()):
                if self.stack.widget(i) is view:
                    self.tab_bar.setTabText(i, title[:30])
                    break
            self.style_script_box.inject_scripts(view, url)

    def close_tab(self, index):
        if self.tab_bar.count() <= 1:
            return
        widget = self.stack.widget(index)
        if widget:
            self.stack.removeWidget(widget)
            if widget in self._loaders:
                del self._loaders[widget]
            if widget in self._reload_counts:
                del self._reload_counts[widget]
            widget.deleteLater()
        self.tab_bar.removeTab(index)

    def active_view(self):
        idx = self.tab_bar.currentIndex()
        if idx >= 0 and idx < self.stack.count():
            return self.stack.widget(idx)
        return None

    def active_loader(self):
        view = self.active_view()
        if view and view in self._loaders:
            return self._loaders[view]
        return None

    def _on_render_process_crashed(self, view):
        browser_logger.warning("Процесс рендеринга завершился аварийно. Перезагрузка...")
        if view in self._loaders:
            self._reload_counts[view] = self._reload_counts.get(view, 0) + 1
            limit = self.settings.get("tab_limits.reload_limit", 5)
            if self._reload_counts[view] > limit:
                browser_logger.error("Превышен лимит перезагрузок, вкладка заморожена")
                return
            view.reload()

    def _check_resource_usage(self):
        try:
            import psutil
            mem = psutil.virtual_memory().percent
            cpu = psutil.cpu_percent(interval=0.1)
            max_mem = self.settings.get("resource_limits.max_memory_percent", 85)
            max_cpu = self.settings.get("resource_limits.max_cpu_percent", 90)
            if mem > max_mem or cpu > max_cpu:
                browser_logger.warning(f"Высокая нагрузка: память {mem}%, CPU {cpu}%")
        except Exception as e:
            browser_logger.error(f"Ошибка мониторинга ресурсов: {e}")

    def restore_session(self):
        tab_states = self.session.get_tab_states()
        if tab_states:
            for state in tab_states:
                url = state.get("url", "about:blank")
                title = state.get("title", "Восстановленная вкладка")
                self.add_new_page_tab(QUrl(url), title=title)
            browser_logger.info(f"Восстановлено {len(tab_states)} вкладок")

    def save_session(self):
        tab_states = []
        for i in range(self.stack.count()):
            view = self.stack.widget(i)
            if view:
                url = view.url().toString()
                title = view.page().title() or url
                tab_states.append({"url": url, "title": title})
        self.session.set_tab_states(tab_states)
        self.session.save_session()