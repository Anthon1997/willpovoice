from pathlib import Path
import re

names = set()
for f in ["ui/modern_window.py", "ui/main_window.py"]:
    p = Path(f)
    if not p.exists():
        continue
    t = p.read_text(encoding="utf-8")
    names |= set(re.findall(r'make_icon\(\s*["\']([A-Za-z0-9_]+)["\']', t))
    names |= set(re.findall(r'IconLabel\(\s*["\']([A-Za-z0-9_]+)["\']', t))

print(f"=== {len(names)} iconos en uso ===")
for n in sorted(names):
    print("  ", n)

try:
    from PySide6.QtSvg import QSvgRenderer
    print("\nQtSvg: OK (puede renderizar SVG)")
except Exception as e:
    print("\nQtSvg FALTA:", e)
