# ui/page_tabs.py
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QTabBar, QStackedWidget, QPushButton
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineScript
from page_loader import PageLoader
from logger import browser_logger

class PageTabManager(QWidget):
    def __init__(self, parent=None, stack: QStackedWidget = None):
        super().__init__(parent)
        self.browser = parent
        self.stack = stack

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

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

        self.views = {}    # index -> QWebEngineView
        self.loaders = {}  # index -> PageLoader

    def add_new_page_tab(self, url=None):
        if self.stack is None:
            raise RuntimeError("Стек страниц не назначен.")

        view = QWebEngineView()
        loader = PageLoader(view)

        view.installEventFilter(self.browser)
        view.urlChanged.connect(lambda u, v=view: self.on_url_changed(u, v))
        view.page().javaScriptConsoleMessage = self.browser.on_console_message
        self.browser.style_manager.apply_styles(view)
        self._inject_session_script(view)
        self.browser.script_manager.inject_scripts(view, QUrl("about:blank"))

        index = self.stack.addWidget(view)
        self.views[index] = view
        self.loaders[index] = loader

        self.tab_bar.addTab("Новая вкладка")
        tab_index = self.tab_bar.count() - 1
        self.tab_bar.setCurrentIndex(tab_index)

        if url is not None:
            view.load(url)
            browser_logger.info(f"Создана новая вкладка с URL: {url.toString()}")

    def close_tab(self, tab_index):
        if self.tab_bar.count() <= 1:
            return
        widget = self.stack.widget(tab_index)
        view = self.views.get(tab_index)
        if view:
            browser_logger.info(f"Закрыта вкладка: {view.url().toString()}")
        self.stack.removeWidget(widget)
        widget.deleteLater()
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
            self.browser.nav_toolbar.update_for_view(view)

    def on_url_changed(self, url, view):
        self.update_tab_title(view)
        if self.active_view() == view:
            self.browser.nav_toolbar.update_address_bar(url)
        self.browser.log_navigation_event(url, view.title())
        browser_logger.debug(f"Навигация: {url.toString()}")

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