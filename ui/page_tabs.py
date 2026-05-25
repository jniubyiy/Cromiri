# ui/page_tabs.py
import time
from PyQt6.QtCore import QUrl, QTimer
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QTabBar, QStackedWidget, QPushButton
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineScript
from page_loader import PageLoader
from logger import browser_logger

class PageTabManager(QWidget):
    def __init__(self, parent=None, stack: QStackedWidget = None, toggle_main_tabs_callback=None):
        super().__init__(parent)
        self.browser = parent
        self.stack = stack
        self.toggle_main_tabs_callback = toggle_main_tabs_callback
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.toggle_main_btn = QPushButton("◻")
        self.toggle_main_btn.setFixedSize(28, 28)
        self.toggle_main_btn.setToolTip("Показать/скрыть главные вкладки")
        self.toggle_main_btn.clicked.connect(self.on_toggle_main)
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

        self.views = {}
        self.loaders = {}
        self._reload_counts = {}

        self.resource_timer = QTimer(self)
        self._update_timer_interval()
        self.resource_timer.timeout.connect(self._check_resource_usage)
        self.resource_timer.start()

    def on_toggle_main(self):
        if self.toggle_main_tabs_callback:
            self.toggle_main_tabs_callback()

    def _update_timer_interval(self):
        interval = self.browser.settings.get("resource_limits.monitor_interval_ms", 5000)
        self.resource_timer.setInterval(interval)

    def add_new_page_tab(self, url=None, suspended=False, title=None):
        max_tabs = self.browser.settings.get("tab_limits.max_tabs", 50)
        if self.tab_bar.count() >= max_tabs:
            browser_logger.warning(f"Достигнут лимит вкладок ({max_tabs}), новая не создана")
            return
        if self.stack is None:
            raise RuntimeError("Стек страниц не назначен.")
        view = QWebEngineView()
        loader = PageLoader(view)
        view.installEventFilter(self.browser)
        view.urlChanged.connect(lambda u, v=view: self.on_url_changed(u, v))
        view.page().javaScriptConsoleMessage = self.browser.on_console_message
        view.page().renderProcessTerminated.connect(
            lambda status, code, v=view: self._on_render_process_crashed(v)
        )
        self.browser.style_manager.apply_styles(view)
        self._inject_session_script(view)
        self.browser.script_manager.inject_scripts(view, QUrl("about:blank"))
        index = self.stack.addWidget(view)
        self.views[index] = view
        self.loaders[index] = loader

        tab_title = title or "Новая вкладка"
        self.tab_bar.addTab(tab_title)
        tab_index = self.tab_bar.count() - 1
        self.tab_bar.setCurrentIndex(tab_index)

        if suspended and url:
            # Восстанавливаем приостановленную вкладку
            view.setProperty("suspended_url", QUrl(url))
            view.load(QUrl("about:blank"))
        elif url:
            view.load(QUrl(url))
        browser_logger.info(f"Создана вкладка: url={url}, suspended={suspended}")

    def close_tab(self, tab_index):
        if self.tab_bar.count() <= 1:
            return
        widget = self.stack.widget(tab_index)
        view = self.views.get(tab_index)
        if view:
            browser_logger.info(f"Закрыта вкладка: {view.url().toString()}")
            view.stop()
        self.stack.removeWidget(widget)
        if view:
            view.deleteLater()
        del self.views[tab_index]
        del self.loaders[tab_index]
        self.tab_bar.removeTab(tab_index)
        new_views = {}
        new_loaders = {}
        for i, v in self.views.items():
            new_i = i if i < tab_index else i - 1
            new_views[new_i] = v
            new_loaders[new_i] = self.loaders[i]
        self.views = new_views
        self.loaders = new_loaders
        if self.tab_bar.count() > 0:
            self.tab_bar.setCurrentIndex(0)

    def on_tab_changed(self, index):
        if index < 0 or self.stack is None or index >= self.stack.count():
            return
        self.stack.setCurrentIndex(index)
        view = self.views.get(index)
        if view:
            suspended_url = view.property("suspended_url")
            if suspended_url and isinstance(suspended_url, QUrl):
                view.load(suspended_url)
                view.setProperty("suspended_url", None)
                browser_logger.info(f"Вкладка {index} восстановлена")
            self.browser.nav_toolbar.update_for_view(view)

    def on_url_changed(self, url, view):
        self.update_tab_title(view)
        self._track_reload(view)
        if self.active_view() == view:
            self.browser.nav_toolbar.update_address_bar(url)
            self.browser.log_navigation_event(url, view.title())

    def update_tab_title(self, view):
        for idx, v in self.views.items():
            if v == view:
                title = view.title() or view.url().toString() or "Новая вкладка"
                self.tab_bar.setTabText(idx, title[:50])
                break

    def active_view(self):
        if self.stack is None:
            return None
        return self.views.get(self.stack.currentIndex())

    def active_loader(self):
        idx = self.stack.currentIndex() if self.stack else -1
        return self.loaders.get(idx)

    def _inject_session_script(self, view):
        js = """
        window.addEventListener('scroll', function() {
            console.log('PAGE_SCROLL: ' + window.scrollY);
        });
        document.addEventListener('click', function(e) {
            if (e.target.matches('.menu, .menu *, [class*="menu"]')) {
                console.log('MENU_CLICK: ' + e.target.textContent.trim().substring(0, 50));
            }
        });
        """
        script = QWebEngineScript()
        script.setSourceCode(js)
        script.setName("session_tracker")
        script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentReady)
        script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
        script.setRunsOnSubFrames(True)
        view.page().scripts().insert(script)

    def _on_render_process_crashed(self, view):
        browser_logger.error(f"Процесс рендеринга вкладки завершился аварийно: {view.url().toString()}")
        html = "<html><body><h3>Вкладка была перезагружена из-за ошибки</h3></body></html>"
        view.setHtml(html)
        crashed_url = view.url()
        QTimer.singleShot(3000, lambda: view.load(crashed_url))

    def _track_reload(self, view):
        now = time.time()
        reload_limit = self.browser.settings.get("tab_limits.reload_limit", 5)
        reload_interval = self.browser.settings.get("tab_limits.reload_interval_sec", 30)
        if view not in self._reload_counts:
            self._reload_counts[view] = []
        self._reload_counts[view] = [t for t in self._reload_counts[view] if now - t < reload_interval]
        self._reload_counts[view].append(now)
        if len(self._reload_counts[view]) > reload_limit:
            browser_logger.warning("Вкладка перезагружается слишком часто, загрузка заблокирована")
            view.setHtml("<html><body><h3>Слишком много перезагрузок. Вкладка приостановлена.</h3></body></html>")
            view.stop()

    def _check_resource_usage(self):
        try:
            import psutil
            mem = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=0.1)
            max_mem = self.browser.settings.get("resource_limits.max_memory_percent", 85)
            max_cpu = self.browser.settings.get("resource_limits.max_cpu_percent", 90)

            if mem.percent > max_mem or cpu > max_cpu:
                browser_logger.warning(f"Высокая загрузка: память {mem.percent}%, CPU {cpu}%. Приостанавливаем фоновые вкладки.")
                current_idx = self.stack.currentIndex()
                for idx, view in self.views.items():
                    if idx != current_idx:
                        url = view.url()
                        if url.isValid() and url.scheme() not in ('about', 'chrome', 'data'):
                            view.setProperty("suspended_url", url)
                            view.setUrl(QUrl('about:blank'))
                            browser_logger.info(f"Вкладка {idx} приостановлена")
        except Exception as e:
            browser_logger.exception(f"Ошибка мониторинга ресурсов: {e}")

    def get_all_tab_states(self):
        """Возвращает список состояний всех вкладок для сохранения в сессию."""
        states = []
        for idx in sorted(self.views.keys()):
            view = self.views[idx]
            suspended_url = view.property("suspended_url")
            if suspended_url and isinstance(suspended_url, QUrl):
                url = suspended_url.toString()
                suspended = True
            else:
                url = view.url().toString()
                suspended = False
            title = view.title() or self.tab_bar.tabText(idx)
            states.append({
                "url": url,
                "title": title,
                "suspended": suspended
            })
        return states

    def restore_tabs(self, states):
        """Удаляет все существующие вкладки и создаёт новые из списка состояний."""
        # Закрываем все текущие вкладки, кроме последней? Проще очистить полностью.
        while self.tab_bar.count() > 0:
            self.close_tab(0)
        for state in states:
            self.add_new_page_tab(
                url=state.get("url", "about:blank"),
                suspended=state.get("suspended", False),
                title=state.get("title", "")
            )