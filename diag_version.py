from pathlib import Path

p = Path("app/version.py")
if p.exists():
    print(p.read_text(encoding="utf-8"))
else:
    print("app/version.py NO EXISTE")
