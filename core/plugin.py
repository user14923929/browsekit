"""
Plugin system for browsekit.

To create a plugin:
    1. Subclass BrowserPlugin
    2. Override any hook methods you need
    3. Register it: browser.plugin_manager.register(MyPlugin())
"""


class BrowserPlugin:
    """
    Base class for all browsekit plugins.
    Override only the hooks you need.
    """

    name: str = "unnamed_plugin"
    version: str = "0.1.0"
    description: str = ""

    def on_load(self, browser) -> None:
        """Called once when the plugin is loaded."""
        pass

    def on_url_change(self, url: str) -> None:
        """Called every time the URL changes in any tab."""
        pass

    def on_page_loaded(self, url: str) -> None:
        """Called when a page finishes loading."""
        pass

    def on_new_tab(self, view) -> None:
        """Called when a new tab is opened. view is QWebEngineView."""
        pass

    def on_close(self) -> None:
        """Called when the browser is about to close."""
        pass


class PluginManager:
    """Manages registration and event dispatching for plugins."""

    def __init__(self, browser):
        self.browser = browser
        self._plugins: list[BrowserPlugin] = []

    def register(self, plugin: BrowserPlugin) -> None:
        """Register a plugin. Can be called before or after load_all()."""
        self._plugins.append(plugin)

    def load_all(self) -> None:
        """Call on_load() on every registered plugin."""
        for plugin in self._plugins:
            try:
                plugin.on_load(self.browser)
            except Exception as e:
                print(f"[browsekit] Plugin '{plugin.name}' failed to load: {e}")

    def emit(self, hook: str, *args) -> None:
        """Call a hook on every plugin, swallowing individual errors."""
        for plugin in self._plugins:
            method = getattr(plugin, hook, None)
            if callable(method):
                try:
                    method(*args)
                except Exception as e:
                    print(f"[browsekit] Plugin '{plugin.name}' error in {hook}: {e}")

    def get(self, name: str) -> BrowserPlugin | None:
        """Find a plugin by name."""
        return next((p for p in self._plugins if p.name == name), None)

    def list_plugins(self) -> list[str]:
        return [p.name for p in self._plugins]
