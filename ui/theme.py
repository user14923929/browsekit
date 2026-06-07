"""
ThemeEngine — loads QSS stylesheets from the themes/ directory.
"""

import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication


THEMES_DIR = Path(__file__).parent / "themes"


def load_theme(name: str = "dark") -> None:
    """
    Apply a QSS theme to the entire QApplication.

    Built-in themes: "dark", "light"
    Custom theme: pass the full path to a .qss file.

    Usage:
        load_theme("dark")
        load_theme("/path/to/my_theme.qss")
    """
    app = QApplication.instance()
    if not app:
        return

    # Check if it's a full path first
    path = Path(name)
    if not path.exists():
        path = THEMES_DIR / f"{name}.qss"

    if not path.exists():
        print(f"[browsekit] Theme '{name}' not found at {path}")
        return

    with open(path, "r", encoding="utf-8") as f:
        qss = f.read()

    app.setStyleSheet(qss)


def list_themes() -> list[str]:
    """Return names of all built-in themes."""
    return [p.stem for p in THEMES_DIR.glob("*.qss")]
