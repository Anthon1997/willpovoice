import ast, shutil
from pathlib import Path

root = Path(".")
borrados = 0

# 1) borrar scripts de parche/diag/scan/test/build (solo raiz)
pats = ("patch_", "fix_", "scan_", "diag_", "test_", "build_",
        "rebuild_", "show_")
for f in sorted(root.glob("*.py")):
    if f.name.startswith(pats):
        f.unlink()
        borrados += 1
print("scripts de parche eliminados:", borrados)

# 2) borrar __pycache__ (sin tocar .venv)
for d in root.rglob("__pycache__"):
    if ".venv" not in str(d):
        shutil.rmtree(d, ignore_errors=True)
print("__pycache__ limpiados")

# 3) borrar caches de PyInstaller
for d in ("build", "build_kg"):
    if Path(d).exists():
        shutil.rmtree(d, ignore_errors=True)
        print("cache build eliminada:", d)

# 4) validacion estatica
ok = True
for f in list(root.glob("*.py")) + list(Path("core").glob("*.py")) + \
        list(Path("ui").glob("*.py")) + list(Path("scripts").glob("*.py")):
    try:
        ast.parse(f.read_text(encoding="utf-8"))
    except Exception as e:
        ok = False
        print("SYNTAX ERROR:", f, e)
print("validacion ast:", "OK" if ok else "FALLOS")

# 5) import smoke test
try:
    import ui.modern_window  # noqa
    print("import ui.modern_window: OK")
except Exception as e:
    print("import FALLO:", e)

# 6) detectar spec e instalador
print("\nspec files:", [f.name for f in root.glob("*.spec")])
print("inno scripts:", [f.name for f in root.glob("*.iss")])
print("nsis scripts:", [f.name for f in root.glob("*.nsi")])
for p in (r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
          r"C:\Program Files\Inno Setup 6\ISCC.exe"):
    if Path(p).exists():
        print("ISCC encontrado:", p)
