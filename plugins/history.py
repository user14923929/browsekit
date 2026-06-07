"""
History plugin — tracks visited URLs with timestamps.

Usage:
    from plugins.history import HistoryPlugin
    plugin = HistoryPlugin()
    browser.plugin_manager.register(plugin)

    # Later:
    entries = plugin.get_history()   # list of (url, title, timestamp)
    plugin.clear()
"""

import json
from datetime import datetime
from pathlib import Path
from core.plugin import BrowserPlugin


class HistoryPlugin(BrowserPlugin):
    name = "history"
    version = "1.0.0"
    description = "Tracks browsing history with timestamps."

    def __init__(self, max_entries: int = 10_000):
        self.max_entries = max_entries
        self._entries: list[dict] = []
        self._history_file: Path | None = None

    def on_load(self, browser) -> None:
        data_dir = Path.home() / ".browsekit" / browser.app_name.lower().replace(" ", "_")
        data_dir.mkdir(parents=True, exist_ok=True)
        self._history_file = data_dir / "history.json"
        self._load_from_disk()

    def on_page_loaded(self, url: str) -> None:
        if url.startswith("about:"):
            return
        self._entries.append({
            "url": url,
            "timestamp": datetime.now().isoformat(),
        })
        # Keep within limit
        if len(self._entries) > self.max_entries:
            self._entries = self._entries[-self.max_entries:]
        self._save_to_disk()

    def on_close(self) -> None:
        self._save_to_disk()

    def get_history(self) -> list[dict]:
        """Return all history entries, newest first."""
        return list(reversed(self._entries))

    def search(self, query: str) -> list[dict]:
        """Return entries whose URL contains query."""
        q = query.lower()
        return [e for e in reversed(self._entries) if q in e["url"].lower()]

    def clear(self) -> None:
        self._entries = []
        self._save_to_disk()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _load_from_disk(self) -> None:
        if self._history_file and self._history_file.exists():
            try:
                with open(self._history_file, "r", encoding="utf-8") as f:
                    self._entries = json.load(f)
            except Exception:
                self._entries = []

    def _save_to_disk(self) -> None:
        if not self._history_file:
            return
        try:
            with open(self._history_file, "w", encoding="utf-8") as f:
                json.dump(self._entries, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[history] Failed to save: {e}")
