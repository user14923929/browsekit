"""
Example: a full browser built on browsekit.

This is what YOUR app/main.py should look like after forking.
It demonstrates:
    - Custom toolbar with back/forward/reload/address bar
    - Dark theme
    - AdBlock + History plugins
    - JS bridge usage
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLineEdit, QStatusBar,
)
from PyQt6.QtCore import Qt

# browsekit imports (adjust path if running from project root)
sys.path.insert(0, "..")
from core import BrowserBase
from ui import load_theme
from plugins import AdBlockPlugin, HistoryPlugin


class MyBrowser(BrowserBase):
    """A full browser built on top of browsekit."""

    def __init__(self):
        # Register plugins BEFORE calling super().__init__()
        # so they are loaded during initialisation
        super().__init__(app_name="MyBrowser")

        self.plugin_manager.register(AdBlockPlugin())
        self.plugin_manager.register(HistoryPlugin())
        self.plugin_manager.load_all()

        # Attach JS bridge to the first tab
        self.js_bridge.register("getTitle", lambda _: self.windowTitle())
        self.js_bridge.attach(self.tab_manager.current_view())

        self.navigate("https://www.google.com")

    # ------------------------------------------------------------------
    # Override: build a real toolbar
    # ------------------------------------------------------------------

    def setup_ui(self):
        from PyQt6.QtWidgets import QToolBar
        from PyQt6.QtGui import QKeySequence

        super().setup_ui()  # sets up tab_widget as central widget

        toolbar = self._build_toolbar()
        self.addToolBar(toolbar)

        status = QStatusBar()
        self.setStatusBar(status)
        self.url_changed.connect(lambda url: status.showMessage(url, 3000))

    def _build_toolbar(self):
        from PyQt6.QtWidgets import QToolBar

        toolbar = QToolBar("Navigation")
        toolbar.setMovable(False)

        # Back / Forward / Reload
        btn_back    = QPushButton("←")
        btn_forward = QPushButton("→")
        btn_reload  = QPushButton("⟳")
        btn_new_tab = QPushButton("+")

        btn_back.setFixedWidth(32)
        btn_forward.setFixedWidth(32)
        btn_reload.setFixedWidth(32)
        btn_new_tab.setFixedWidth(32)

        btn_back.clicked.connect(self.back)
        btn_forward.clicked.connect(self.forward)
        btn_reload.clicked.connect(self.reload)
        btn_new_tab.clicked.connect(self.new_tab)

        # Address bar
        self.address_bar = QLineEdit()
        self.address_bar.setPlaceholderText("Enter URL or search…")
        self.address_bar.returnPressed.connect(
            lambda: self.navigate(self.address_bar.text())
        )
        self.url_changed.connect(self._update_address_bar)

        for widget in (btn_back, btn_forward, btn_reload,
                       self.address_bar, btn_new_tab):
            toolbar.addWidget(widget)

        return toolbar

    # ------------------------------------------------------------------
    # Override: react to navigation events
    # ------------------------------------------------------------------

    def on_url_changed(self, url: str):
        self._update_address_bar(url)

    def _update_address_bar(self, url: str):
        if hasattr(self, "address_bar") and not self.address_bar.hasFocus():
            self.address_bar.setText(url)


# ------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("MyBrowser")

    load_theme("dark")  # or "light", or path to your own .qss

    window = MyBrowser()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
