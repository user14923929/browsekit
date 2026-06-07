"""
TabManager — manages browser tabs backed by QTabWidget.
"""

from PyQt6.QtWidgets import QTabWidget
from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile


class TabManager:
    """
    Wraps a QTabWidget and provides a simple API for opening,
    closing, and switching tabs.

    Each tab is a QWebEngineView sharing a single QWebEngineProfile
    (so cookies and cache are shared across tabs, like a real browser).
    """

    def __init__(self, browser):
        self.browser = browser

        # All tabs share one profile → shared cookies / cache / storage
        self.profile = QWebEngineProfile("browsekit", browser)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self._close_tab)
        self.tab_widget.currentChanged.connect(self._on_tab_switched)

        # Open a default tab so the window is never empty
        self.open_tab("about:blank")

    def open_tab(self, url: str = "about:blank") -> QWebEngineView:
        """Create a new tab, navigate to url, return the view."""
        from PyQt6.QtWebEngineCore import QWebEnginePage

        view = QWebEngineView()
        page = QWebEnginePage(self.profile, view)
        view.setPage(page)
        view.setUrl(QUrl(url))
        view.titleChanged.connect(lambda t: self._update_tab_title(view, t))

        index = self.tab_widget.addTab(view, "New Tab")
        self.tab_widget.setCurrentIndex(index)
        return view

    def close_current(self):
        index = self.tab_widget.currentIndex()
        self._close_tab(index)

    def current_view(self) -> QWebEngineView | None:
        widget = self.tab_widget.currentWidget()
        return widget if isinstance(widget, QWebEngineView) else None

    def view_at(self, index: int) -> QWebEngineView | None:
        widget = self.tab_widget.widget(index)
        return widget if isinstance(widget, QWebEngineView) else None

    def count(self) -> int:
        return self.tab_widget.count()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _close_tab(self, index: int):
        if self.tab_widget.count() == 1:
            # Never close the last tab — navigate home instead
            view = self.view_at(0)
            if view:
                view.setUrl(QUrl("about:blank"))
            return
        widget = self.tab_widget.widget(index)
        self.tab_widget.removeTab(index)
        if widget:
            widget.deleteLater()

    def _update_tab_title(self, view: QWebEngineView, title: str):
        index = self.tab_widget.indexOf(view)
        if index >= 0:
            label = title[:20] + "…" if len(title) > 20 else title
            self.tab_widget.setTabText(index, label or "New Tab")

    def _on_tab_switched(self, index: int):
        view = self.view_at(index)
        if view:
            self.browser._on_url_changed(view.url().toString())
            self.browser._on_title_changed(view.title())
