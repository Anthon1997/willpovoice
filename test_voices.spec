a = Analysis(["test_voices_min.py"], pathex=[], binaries=[], datas=[],
    hiddenimports=[], hookspath=[], hooksconfig={}, runtime_hooks=[],
    excludes=[], noarchive=False, optimize=0)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name="test_voices",
    debug=False, strip=False, upx=False, console=True)
