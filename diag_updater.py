from pathlib import Path

p = Path("core/updater.py")
if p.exists():
    print(p.read_text(encoding="utf-8"))
else:
    print("core/updater.py NO EXISTE")
