# browsekit

> A base for building PyQt6 browsers — like Chromium, but in Python.

Fork this repo. Build your browser on top. Ship it.

browsekit is **not** a library you install — it's a project you fork and extend.
The `core/` layer handles tabs, plugins, settings, and JS↔Python communication.
You write your toolbar, your features, your UI in `app/main.py`.

---

## What's inside

```
browsekit/
├── core/               ← Don't touch unless you know what you're doing
│   ├── browser.py      ← BrowserBase — the class you subclass
│   ├── tab_manager.py  ← Tab lifecycle, QWebEngineProfile
│   ├── plugin.py       ← Plugin base class + manager
│   ├── settings.py     ← Persistent key-value store (QSettings)
│   └── js_bridge.py    ← Python ↔ JavaScript via QWebChannel
│
├── ui/                 ← Customize freely
│   ├── theme.py        ← load_theme("dark") / load_theme("light")
│   └── themes/
│       ├── dark.qss
│       └── light.qss
│
├── plugins/            ← Optional built-in plugins, use what you need
│   ├── adblock.py      ← Blocks ad/tracker domains
│   └── history.py      ← Tracks visited URLs
│
└── app/
    └── main.py         ← YOUR browser lives here
```

---

## Requirements

- Python 3.11 or newer
- PyQt6
- PyQt6-WebEngine (ships Chromium under the hood)

---

## Setup

### 1. Fork or clone

```bash
git clone https://github.com/user14923929/browsekit.git my-browser
cd my-browser
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
.venv\Scripts\activate      # Windows
```

### 3. Install dependencies

```bash
pip install PyQt6 PyQt6-WebEngine
```

That's it. No build step, no compilation.

### 4. Run the example browser

```bash
python app/main.py
```

---

## Tutorial: building your own browser

### Step 1 — Subclass BrowserBase

Open `app/main.py`. Everything starts here.

```python
import sys
from PyQt6.QtWidgets import QApplication
from core import BrowserBase
from ui import load_theme

class MyBrowser(BrowserBase):
    def __init__(self):
        super().__init__(app_name="MyBrowser")
        self.navigate("https://www.google.com")

app = QApplication(sys.argv)
load_theme("dark")
window = MyBrowser()
window.show()
sys.exit(app.exec())
```

`BrowserBase` gives you a working browser with tabs and shortcuts.
Run it — it already works.

---

### Step 2 — Add a toolbar

Override `setup_ui()` to build your own chrome (the browser chrome, not Google Chrome):

```python
from PyQt6.QtWidgets import QLineEdit, QPushButton, QToolBar

class MyBrowser(BrowserBase):
    def setup_ui(self):
        super().setup_ui()          # sets up tab widget

        toolbar = QToolBar()
        toolbar.setMovable(False)

        self.address_bar = QLineEdit()
        self.address_bar.returnPressed.connect(
            lambda: self.navigate(self.address_bar.text())
        )

        btn_back    = QPushButton("←")
        btn_forward = QPushButton("→")
        btn_reload  = QPushButton("⟳")

        btn_back.clicked.connect(self.back)
        btn_forward.clicked.connect(self.forward)
        btn_reload.clicked.connect(self.reload)

        for w in (btn_back, btn_forward, btn_reload, self.address_bar):
            toolbar.addWidget(w)

        self.addToolBar(toolbar)

        # Keep address bar in sync
        self.url_changed.connect(
            lambda url: self.address_bar.setText(url)
        )
```

---

### Step 3 — React to navigation events

Override any of these hooks in your subclass:

```python
def on_url_changed(self, url: str):
    # Called every time the URL changes
    print(f"Navigated to: {url}")

def on_title_changed(self, title: str):
    # Called when the page title changes
    self.setWindowTitle(title)

def on_page_loaded(self, url: str):
    # Called when the page finishes loading
    self.statusBar().showMessage("Done", 2000)
```

---

### Step 4 — Use plugins

Plugins extend behaviour without touching `core/`.

```python
from plugins import AdBlockPlugin, HistoryPlugin

class MyBrowser(BrowserBase):
    def __init__(self):
        super().__init__(app_name="MyBrowser")
        self.plugin_manager.register(AdBlockPlugin())
        self.plugin_manager.register(HistoryPlugin())
        self.plugin_manager.load_all()
```

#### Writing your own plugin

```python
from core import BrowserPlugin

class DarkModePlugin(BrowserPlugin):
    name = "dark_mode"

    def on_load(self, browser):
        # Inject CSS into every page that loads
        pass

    def on_page_loaded(self, url: str):
        view = self._browser.tab_manager.current_view()
        view.page().runJavaScript("""
            document.body.style.filter = 'invert(1) hue-rotate(180deg)';
        """)

    def on_load(self, browser):
        self._browser = browser
```

Drop your plugin file into `plugins/` and register it — that's all.

---

### Step 5 — Python ↔ JavaScript bridge

browsekit includes a two-way bridge between Python and JavaScript via `QWebChannel`.

**Python side — register a handler:**

```python
def __init__(self):
    super().__init__(app_name="MyBrowser")

    # Register a Python function callable from JS
    self.js_bridge.register("ping", lambda data: "pong")
    self.js_bridge.register("getOS", lambda _: sys.platform)

    # Attach to the current tab
    self.js_bridge.attach(self.tab_manager.current_view())
```

**JavaScript side — call Python:**

```javascript
// qwebchannel.js must be loaded first (ships with Qt)
new QWebChannel(qt.webChannelTransport, function(channel) {
    const bridge = channel.objects.bridge;

    bridge.callPython(
        JSON.stringify({ action: "ping", data: null }),
        function(response) {
            console.log(JSON.parse(response).result); // "pong"
        }
    );
});
```

**Python → JavaScript (push message):**

```python
self.js_bridge.send("hello from Python")
```

In JS, listen with:

```javascript
bridge.message_to_js.connect(function(msg) {
    console.log("Python says:", msg);
});
```

---

### Step 6 — Themes

Apply a built-in theme:

```python
from ui import load_theme

load_theme("dark")   # or "light"
```

Create your own: copy `ui/themes/dark.qss`, edit it, then:

```python
load_theme("/path/to/my_theme.qss")
```

All Qt widgets are styled via QSS (Qt Style Sheets — similar to CSS).

---

### Step 7 — Settings

Persist any value across sessions:

```python
# Save
self.settings.set("homepage", "https://example.com")
self.settings.set("zoom_level", 1.25)

# Read (with default)
homepage = self.settings.get("homepage", "about:blank")
zoom     = self.settings.get("zoom_level", 1.0)
```

Settings are saved automatically when the window closes.
They live in `~/.config/browsekit/YourAppName/`.

---

## Built-in shortcuts

| Shortcut     | Action              |
|-------------|---------------------|
| `Ctrl+T`    | New tab             |
| `Ctrl+W`    | Close current tab   |
| `Ctrl+R`    | Reload              |
| `Alt+Left`  | Back                |
| `Alt+Right` | Forward             |

Override `setup_shortcuts()` to add or replace them.

---

## Building a standalone executable with PyInstaller

### Install PyInstaller

```bash
pip install pyinstaller
```

### Build

```bash
pyinstaller mybrowser.spec
```

The output goes into `dist/MyBrowser/`.
Distribute the entire folder — it contains the executable and all Qt libraries.

### Linux: single folder (recommended)

```
dist/
└── MyBrowser/
    ├── MyBrowser          ← run this
    ├── libQt6WebEngine*.so
    └── ...
```

### Notes on QtWebEngine + PyInstaller

- QtWebEngine spawns a **renderer subprocess** (`QtWebEngineProcess`).
  PyInstaller handles this automatically — don't bundle it manually.
- On Linux, the executable needs `--no-sandbox` if running as root
  (don't run as root).
- On Windows, add `console=False` in the `.spec` to suppress the terminal
  window (already set in the provided `mybrowser.spec`).
- If you get `Could not find QtWebEngineProcess`, make sure PyQt6-WebEngine
  is installed in the same virtualenv you run PyInstaller from.

---

## Who owns what

| Component | File | Your role |
|---|---|---|
| Browser lifecycle | `core/browser.py` | Subclass, override hooks |
| Tab management | `core/tab_manager.py` | Use via `self.tab_manager` |
| Plugin system | `core/plugin.py` | Subclass `BrowserPlugin`, register |
| Settings | `core/settings.py` | Use via `self.settings` |
| JS bridge | `core/js_bridge.py` | Register handlers, call `attach()` |
| Themes | `ui/themes/*.qss` | Edit or add your own `.qss` |
| Your browser | `app/main.py` | **This is your canvas** |

---

## License

GPL v3 — free to use, modify, and distribute, but any project built on
browsekit must also be released under GPL v3 (or a compatible license).
See [LICENSE](LICENSE) for the full text.
