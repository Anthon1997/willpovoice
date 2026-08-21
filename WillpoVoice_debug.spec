# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all, collect_data_files

datas = [("assets", "assets")]
for pkg in ("docx", "lxml"):
    try:
        datas += collect_data_files(pkg)
    except Exception:
        pass

binaries, datas_pyside, hiddenimports = collect_all("PySide6")
datas += datas_pyside

a = Analysis(
    ["run.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports + [
        "comtypes", "comtypes.client",
        "win32com", "win32com.client",
        "pythoncom", "pywintypes", "win32timezone",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="WillpoVoice",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    icon="assets/icons/app.ico",
)

