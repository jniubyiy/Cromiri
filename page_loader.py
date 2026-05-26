# page_loader.py
from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from logger import browser_logger

class PageLoader:
    def __init__(self, web_view: QWebEngineView):
        self.view = web_view

    def load_url(self, url: str):
        if not url.startswith('http'):
            url = 'https://' + url
        browser_logger.info(f"Загрузка URL: {url}")
        self.view.load(QUrl(url))

    def back(self):
        browser_logger.info("Выполнение перехода назад")
        self.view.back()

    def forward(self):
        browser_logger.info("Выполнение перехода вперёд")
        self.view.forward()

    def reload(self):
        browser_logger.info("Перезагрузка страницы")
        self.view.reload()

    def load_gelbooru_all(self):
        self.load_url("https://gelbooru.com/index.php?page=post&s=list&tags=all")