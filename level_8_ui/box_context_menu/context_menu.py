from PyQt6.QtCore import Qt, QUrl, QPoint
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMenu, QApplication
from PyQt6.QtWebEngineWidgets import QWebEngineView
import json
from level_0.level_base import Box
from logger import browser_logger

class ContextMenuBox(Box):
    def __init__(self, settings):
        super().__init__("context_menu")
        self.settings = settings
        self._views = set()
        self.new_tab_callback = None

    def setup_view(self, view: QWebEngineView):
        """Подключает кастомное контекстное меню к QWebEngineView."""
        if view in self._views:
            return
        view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        view.customContextMenuRequested.connect(
            lambda pos, v=view: self._show_menu(pos, v)
        )
        self._views.add(view)
        browser_logger.debug(f"Контекстное меню подключено к view {id(view)}")

    def set_new_tab_callback(self, callback):
        """Коллбэк для открытия URL в новой вкладке."""
        self.new_tab_callback = callback

    def _show_menu(self, pos: QPoint, view: QWebEngineView):
        """Запрашивает контекстную информацию у страницы через JavaScript."""
        js = """
        (function() {
            var el = document.elementFromPoint(%d, %d);
            if (!el) return '{}';
            var info = {};
            var link = el.closest('a');
            if (link) {
                info.linkUrl = link.href;
                info.linkText = link.textContent.trim().substring(0, 100);
            }
            if (el.tagName === 'IMG') {
                info.imageUrl = el.src;
                info.imageAlt = el.alt || '';
            } else {
                var img = el.querySelector('img');
                if (img) {
                    info.imageUrl = img.src;
                    info.imageAlt = img.alt || '';
                }
            }
            var selection = window.getSelection();
            if (selection && selection.rangeCount > 0) {
                info.selectedText = selection.toString().substring(0, 500);
            }
            return JSON.stringify(info);
        })();
        """ % (pos.x(), pos.y())
        view.page().runJavaScript(js, lambda result: self._on_context_info(result, view, pos))

    def _on_context_info(self, js_result, view, pos):
        try:
            info = json.loads(js_result) if js_result else {}
        except Exception:
            info = {}
        menu = QMenu()
        self._populate_menu(menu, view, pos, info)
        menu.exec(view.mapToGlobal(pos))

    def _populate_menu(self, menu: QMenu, view: QWebEngineView, pos: QPoint, info: dict):
        cfg = self.settings.get("context_menu", {
            "back": True, "forward": True, "reload": True,
            "separator1": True, "save_page": True, "print": True,
            "separator2": True, "copy": True, "paste": True,
            "select_all": True, "separator3": True,
            "open_link_new_tab": True, "open_link_new_window": True,
            "copy_link": True, "save_image": True, "copy_image": True
        })

        if cfg.get("back", True):
            menu.addAction(self.settings.tr("context_menu.back"), view.back)
        if cfg.get("forward", True):
            menu.addAction(self.settings.tr("context_menu.forward"), view.forward)
        if cfg.get("reload", True):
            menu.addAction(self.settings.tr("context_menu.reload"), view.reload)

        if cfg.get("separator1", True):
            menu.addSeparator()

        if cfg.get("save_page", True):
            menu.addAction(self.settings.tr("context_menu.save_page"),
                           lambda: view.page().save(view.url().toString()))
        if cfg.get("print", True):
            menu.addAction(self.settings.tr("context_menu.print"),
                           lambda: view.page().printToPdf("output.pdf"))

        if cfg.get("separator2", True):
            menu.addSeparator()

        if cfg.get("copy", True):
            action = menu.addAction(self.settings.tr("context_menu.copy"))
            action.triggered.connect(lambda: view.triggerPageAction(view.page().WebAction.Copy))
            if not info.get("selectedText"):
                action.setEnabled(False)
        if cfg.get("paste", True):
            menu.addAction(self.settings.tr("context_menu.paste"),
                           lambda: view.triggerPageAction(view.page().WebAction.Paste))
        if cfg.get("select_all", True):
            menu.addAction(self.settings.tr("context_menu.select_all"),
                           lambda: view.triggerPageAction(view.page().WebAction.SelectAll))

        if cfg.get("separator3", True):
            menu.addSeparator()

        link_url = info.get("linkUrl")
        image_url = info.get("imageUrl")

        # Открыть ссылку в новой вкладке
        if cfg.get("open_link_new_tab", True):
            action = menu.addAction(self.settings.tr("context_menu.open_link_new_tab"))
            if link_url:
                action.triggered.connect(lambda checked, u=link_url: self._open_in_new_tab(u))
            else:
                action.setEnabled(False)

        # Открыть в новом окне (заглушка)
        if cfg.get("open_link_new_window", True):
            action = menu.addAction(self.settings.tr("context_menu.open_link_new_window"))
            action.setEnabled(False)

        # Копировать ссылку
        if cfg.get("copy_link", True):
            action = menu.addAction(self.settings.tr("context_menu.copy_link"))
            if link_url:
                action.triggered.connect(lambda checked, u=link_url: QApplication.clipboard().setText(u))
            else:
                action.setEnabled(False)

        # Сохранить изображение
        if cfg.get("save_image", True):
            action = menu.addAction(self.settings.tr("context_menu.save_image"))
            if image_url:
                action.triggered.connect(lambda checked, u=image_url: view.page().download(QUrl(u)))
            else:
                action.setEnabled(False)

        # Копировать изображение (URL)
        if cfg.get("copy_image", True):
            action = menu.addAction(self.settings.tr("context_menu.copy_image"))
            if image_url:
                action.triggered.connect(lambda checked, u=image_url: QApplication.clipboard().setText(u))
            else:
                action.setEnabled(False)

    def _open_in_new_tab(self, url):
        if self.new_tab_callback:
            self.new_tab_callback(url)
        else:
            browser_logger.warning("Коллбэк для новой вкладки не задан")