"""
BrowserBase — the heart of browsekit.
Fork this repo and subclass BrowserBase to build your own browser.
"""

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PyQt6.QtCore import QUrl, pyqtSignal
from PyQt6.QtWebEngineWidgets import QWebEngineView

from .tab_manager import TabManager
from .settings import Settings
from .js_bridge import JSBridge
from .plugin import PluginManager


class BrowserBase(QMainWindow):
    """
    The base class for every browsekit-based browser.

    Subclass this and override:
        - setup_ui()       → build your own toolbar / layout
        - setup_shortcuts()→ add / replace keyboard shortcuts
        - on_url_changed() → react to navigation events
        - on_title_changed()→ react to page title changes

    Everything else (tabs, plugins, JS bridge, settings) is ready to use.
    """

    url_changed = pyqtSignal(str)
    title_changed = pyqtSignal(str)
    page_loaded = pyqtSignal(str)

    def __init__(self, app_name: str = "BrowserKit App"):
        super().__init__()
        self.app_name = app_name
        self.setWindowTitle(app_name)

        # Core systems — available to subclasses
        self.settings = Settings(app_name)
        self.tab_manager = TabManager(self)
        self.js_bridge = JSBridge(self)
        self.plugin_manager = PluginManager(self)

        # Build the UI (override this in your subclass)
        self.setup_ui()
        self.setup_shortcuts()

        # Load plugins registered before __init__ finishes
        self.plugin_manager.load_all()

        # Restore last session if enabled
        if self.settings.get("restore_session", False):
            last_url = self.settings.get("last_url", "about:blank")
            self.navigate(last_url)

    # ------------------------------------------------------------------
    # UI setup — override in subclass
    # ------------------------------------------------------------------

    def setup_ui(self):
        """
        Default UI: just a bare web view, no toolbar.
        Override this entirely in your subclass.
        """
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.tab_manager.tab_widget)
        self.setCentralWidget(container)
        self.resize(
            self.settings.get("window_width", 1280),
            self.settings.get("window_height", 800),
        )

    def setup_shortcuts(self):
        """Override to add or change keyboard shortcuts."""
        from PyQt6.QtGui import QKeySequence, QShortcut

        QShortcut(QKeySequence("Ctrl+T"), self).activated.connect(
            lambda: self.new_tab()
        )
        QShortcut(QKeySequence("Ctrl+W"), self).activated.connect(
            self.close_current_tab
        )
        QShortcut(QKeySequence("Ctrl+R"), self).activated.connect(
            self.reload
        )
        QShortcut(QKeySequence("Alt+Left"), self).activated.connect(
            self.back
        )
        QShortcut(QKeySequence("Alt+Right"), self).activated.connect(
            self.forward
        )

    # ------------------------------------------------------------------
    # Navigation API — use these in your subclass
    # ------------------------------------------------------------------

    def navigate(self, url: str):
        """Navigate the current tab to a URL."""
        if not url.startswith(("http://", "https://", "file://", "about:")):
            url = "https://" + url
        view = self.tab_manager.current_view()
        if view:
            view.setUrl(QUrl(url))

    def new_tab(self, url: str = "about:blank") -> QWebEngineView:
        """Open a new tab and return its QWebEngineView."""
        view = self.tab_manager.open_tab(url)
        view.urlChanged.connect(lambda q: self._on_url_changed(q.toString()))
        view.titleChanged.connect(self._on_title_changed)
        view.loadFinished.connect(lambda _: self._on_page_loaded(
            view.url().toString()
        ))
        return view

    def close_current_tab(self):
        self.tab_manager.close_current()

    def reload(self):
        view = self.tab_manager.current_view()
        if view:
            view.reload()

    def back(self):
        view = self.tab_manager.current_view()
        if view:
            view.back()

    def forward(self):
        view = self.tab_manager.current_view()
        if view:
            view.forward()

    def current_url(self) -> str:
        view = self.tab_manager.current_view()
        return view.url().toString() if view else ""

    # ------------------------------------------------------------------
    # Event hooks — override for custom behaviour
    # ------------------------------------------------------------------

    def on_url_changed(self, url: str):
        """Called every time the URL changes. Override in subclass."""
        pass

    def on_title_changed(self, title: str):
        """Called when the page title changes. Override in subclass."""
        self.setWindowTitle(f"{title} — {self.app_name}")

    def on_page_loaded(self, url: str):
        """Called when a page finishes loading. Override in subclass."""
        pass

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _on_url_changed(self, url: str):
        self.url_changed.emit(url)
        self.plugin_manager.emit("on_url_change", url)
        self.on_url_changed(url)

    def _on_title_changed(self, title: str):
        self.title_changed.emit(title)
        self.on_title_changed(title)

    def _on_page_loaded(self, url: str):
        self.page_loaded.emit(url)
        self.plugin_manager.emit("on_page_loaded", url)
        self.on_page_loaded(url)
        self.settings.set("last_url", url)

    def closeEvent(self, event):
        self.settings.set("window_width", self.width())
        self.settings.set("window_height", self.height())
        self.settings.save()
        super().closeEvent(event)
