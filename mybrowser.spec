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

a = Analysis(
    [str(ROOT / "app" / "main.py")],
    site_packages = sysconfig.get_paths()["purelib"],
    pathex=[str(ROOT)] + [site_packages],
    binaries=[],
    datas=[
        # Include QSS themes
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
    console=False,          # no terminal window
    # icon="app/icon.ico",  # uncomment and set your icon
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
