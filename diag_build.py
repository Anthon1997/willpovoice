from pathlib import Path
import importlib.util, sys

print("Python:", sys.executable)
print("=== raiz ===")
for f in sorted(Path(".").iterdir()):
    print(" -", f.name)
print("=== assets ===")
if Path("assets").exists():
    for f in sorted(Path("assets").iterdir()):
        print(" -", f.name)
print("=== PyInstaller:", importlib.util.find_spec("PyInstaller") is not None)
