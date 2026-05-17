# page_loader.py
from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView

class PageLoader:
    def __init__(self, web_view: QWebEngineView):
        self.view = web_view

    def load_url(self, url: str):
        if not url.startswith('http'):
            url = 'https://' + url
        self.view.load(QUrl(url))

    def back(self):
        self.view.back()

    def forward(self):
        self.view.forward()

    def reload(self):
        self.view.reload()

    def load_gelbooru_all(self):
        self.load_url("https://gelbooru.com/index.php?page=post&s=list&tags=all")