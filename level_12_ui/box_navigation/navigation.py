from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from level_0.level_base import Box
from logger import browser_logger

class NavigationBox(Box):
    def __init__(self):
        super().__init__("navigation")
        # Словарь для хранения ссылок на view (используется для логирования)
        self._views = {}

    def setup_loader(self, view: QWebEngineView):
        """
        Регистрирует view в боксе навигации и возвращает сам view.
        Теперь навигация выполняется напрямую через этот бокс без отдельного PageLoader.
        """
        self._views[view] = view
        return view

    def load_url(self, view: QWebEngineView, url: str):
        if not url.startswith('http'):
            url = 'https://' + url
        browser_logger.info(f"Загрузка URL: {url}")
        view.load(QUrl(url))

    def back(self, view: QWebEngineView):
        browser_logger.info("Выполнение перехода назад")
        view.back()

    def forward(self, view: QWebEngineView):
        browser_logger.info("Выполнение перехода вперёд")
        view.forward()

    def reload(self, view: QWebEngineView):
        browser_logger.info("Перезагрузка страницы")
        view.reload()