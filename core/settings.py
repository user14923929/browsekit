"""
Settings — thin wrapper around QSettings with dict-like API.
Values are persisted automatically on browser close.
"""

import json
from PyQt6.QtCore import QSettings


class Settings:
    """
    Persistent key-value store backed by QSettings.

    Usage:
        settings = Settings("MyBrowser")
        settings.set("homepage", "https://example.com")
        settings.get("homepage", "about:blank")
        settings.save()   # called automatically on close
    """

    def __init__(self, app_name: str = "browsekit"):
        self._qs = QSettings("browsekit", app_name)
        self._cache: dict = {}
        self._load()

    def get(self, key: str, default=None):
        return self._cache.get(key, default)

    def set(self, key: str, value) -> None:
        self._cache[key] = value

    def delete(self, key: str) -> None:
        self._cache.pop(key, None)

    def all(self) -> dict:
        return dict(self._cache)

    def save(self) -> None:
        for key, value in self._cache.items():
            if isinstance(value, (dict, list)):
                self._qs.setValue(key, json.dumps(value))
            else:
                self._qs.setValue(key, value)
        self._qs.sync()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _load(self) -> None:
        for key in self._qs.allKeys():
            raw = self._qs.value(key)
            # Try to parse JSON for complex types
            if isinstance(raw, str):
                try:
                    self._cache[key] = json.loads(raw)
                    continue
                except (json.JSONDecodeError, ValueError):
                    pass
            self._cache[key] = raw
