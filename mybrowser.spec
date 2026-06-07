# mybrowser.spec
# PyInstaller build spec for a browsekit-based browser.
#
# Usage:
#   pyinstaller mybrowser.spec
#
# Output: dist/MyBrowser/  (folder with executable + Qt libs)

import sys
from pathlib import Path

block_cipher = None

ROOT = Path(SPECPATH)

# Collect all site-packages directories visible to the running Python.
# Handles both venv and system-wide installs (common on Arch/CachyOS).
site_paths = [p for p in sys.path if "site-packages" in p]

a = Analysis(
    [str(ROOT / "app" / "main.py")],
    pathex=[str(ROOT)] + site_paths,
    binaries=[],
    datas=[
        (str(ROOT / "ui" / "themes"), "ui/themes"),
    ],
    hiddenimports=[
        "PyQt6.QtWebEngineWidgets",
        "PyQt6.QtWebEngineCore",
        "PyQt6.QtWebChannel",
        "PyQt6.QtNetwork",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="MyBrowser",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    # icon="app/icon.ico",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="MyBrowser",
)