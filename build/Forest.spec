# -*- mode: python ; coding: utf-8 -*-
# Forest CUS — PyInstaller spec
# Build: source venv/bin/activate && pyinstaller build/Forest.spec

import sys
from pathlib import Path

PROJECT = Path(SPECPATH).parent   # Forest/ root (spec is in Forest/build/)

a = Analysis(
    [str(PROJECT / "build" / "ForestLauncher.py")],
    pathex=[str(PROJECT)],
    binaries=[],
    datas=[],
    hiddenimports=[
        "tkinter",
        "tkinter.ttk",
        "tkinter.font",
        "tkinter.filedialog",
        "tkinter.messagebox",
        "psutil",
        "_tkinter",
        "urllib.request",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude everything Forest CUS runs via subprocess (keeps bundle small)
        "streamlit", "langgraph", "langchain", "ollama",
        "pandas", "numpy", "matplotlib",
        "PIL", "cv2", "torch", "tensorflow",
    ],
    noarchive=False,
    optimize=1,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Forest",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,          # UPX causes issues on macOS sometimes
    console=False,      # windowed app — no Terminal window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,   # build for current arch (arm64 on M-series)
    codesign_identity=None,
    entitlements_file=None,
    icon=None,          # add your own .icns here for a custom icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="Forest",
)

app = BUNDLE(
    coll,
    name="Forest.app",
    icon=None,
    bundle_identifier="com.forest.cus",
    info_plist={
        "CFBundleName":              "Forest CUS",
        "CFBundleDisplayName":       "Forest CUS",
        "CFBundleShortVersionString": "1.0.0",
        "CFBundleVersion":           "1.0.0",
        "NSHighResolutionCapable":   True,
        "LSUIElement":               False,   # show in Dock
        "NSRequiresAquaSystemAppearance": False,  # support dark mode
    },
)
