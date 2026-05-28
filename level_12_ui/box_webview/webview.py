from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from level_0.level_base import Box
from logger import browser_logger

class WebViewBox(Box):
    """
    Бокс, предоставляющий доступ к активному QWebEngineView и управление им.
    Использует TabsBox для получения текущей вкладки и NavigationBox для навигации.
    """
    def __init__(self, tabs_wrapper, navigation_wrapper):
        super().__init__("webview")
        self._tabs = tabs_wrapper      # обёртка TabsBox
        self._navigation = navigation_wrapper

    def get_active_view(self) -> QWebEngineView:
        """Возвращает QWebEngineView активной вкладки."""
        loader = self._tabs.call("active_loader")
        if loader and hasattr(loader, 'view'):
            return loader.view
        return None

    def get_current_url(self) -> str:
        """Возвращает URL текущей страницы или пустую строку."""
        view = self.get_active_view()
        if view:
            return view.url().toString()
        return ""

    def load_url(self, url: str):
        """Загружает URL в активной вкладке."""
        view = self.get_active_view()
        if view:
            self._navigation.call("load_url", view, url)
        else:
            browser_logger.warning("WebViewBox: нет активного view для загрузки URL")

    def back(self):
        view = self.get_active_view()
        if view:
            self._navigation.call("back", view)

    def forward(self):
        view = self.get_active_view()
        if view:
            self._navigation.call("forward", view)

    def reload(self):
        view = self.get_active_view()
        if view:
            self._navigation.call("reload", view)