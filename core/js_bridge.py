"""
JSBridge — bidirectional Python ↔ JavaScript communication.

Uses QWebChannel under the hood.
JavaScript side needs qwebchannel.js (shipped with Qt).

JS usage:
    new QWebChannel(qt.webChannelTransport, function(channel) {
        const bridge = channel.objects.bridge;
        bridge.callPython("hello", function(response) {
            console.log(response);
        });
    });
"""

from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtWebEngineWidgets import QWebEngineView


class _BridgeObject(QObject):
    """
    The actual QObject exposed to JavaScript.
    Extend this if you need more slots.
    """

    # Signal from Python → JavaScript
    message_to_js = pyqtSignal(str)

    def __init__(self, bridge):
        super().__init__()
        self._bridge = bridge
        self._handlers: dict = {}

    def register_handler(self, name: str, fn) -> None:
        """Register a Python function callable from JS."""
        self._handlers[name] = fn

    @pyqtSlot(str, result=str)
    def callPython(self, payload: str) -> str:
        """
        Generic entry point from JavaScript.
        payload: JSON string {"action": "...", "data": ...}
        returns: JSON string
        """
        import json
        try:
            msg = json.loads(payload)
            action = msg.get("action", "")
            data = msg.get("data", None)
            handler = self._handlers.get(action)
            if handler:
                result = handler(data)
                return json.dumps({"ok": True, "result": result})
            return json.dumps({"ok": False, "error": f"No handler for '{action}'"})
        except Exception as e:
            return json.dumps({"ok": False, "error": str(e)})

    @pyqtSlot(str)
    def log(self, message: str) -> None:
        """Simple JS → Python logging."""
        print(f"[JS] {message}")


class JSBridge:
    """
    High-level wrapper. Attach to a QWebEngineView to enable JS ↔ Python.

    Usage:
        bridge.register("greet", lambda name: f"Hello, {name}!")
        bridge.attach(view)
    """

    def __init__(self, browser):
        self.browser = browser
        self._obj = _BridgeObject(self)
        self._channel = QWebChannel()
        self._channel.registerObject("bridge", self._obj)

    def register(self, action: str, handler) -> None:
        """Register a Python handler callable from JS via bridge.callPython."""
        self._obj.register_handler(action, handler)

    def attach(self, view: QWebEngineView) -> None:
        """Attach the bridge to a specific QWebEngineView."""
        view.page().setWebChannel(self._channel)

    def send(self, message: str) -> None:
        """Emit a signal from Python to JavaScript."""
        self._obj.message_to_js.emit(message)
