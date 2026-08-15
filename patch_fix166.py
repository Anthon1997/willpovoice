from pathlib import Path
import ast

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

cambios = [
    ("        self.setFixedSize(940, 660)",
     "        self.setFixedSize(860, 620)"),
    ("        left.setFixedWidth(260)",
     "        left.setFixedWidth(230)"),
    ("        lv.setContentsMargins(12, 12, 12, 12)",
     "        lv.setContentsMargins(8, 10, 8, 10)"),
    ("        rv.setContentsMargins(36, 18, 36, 12)",
     "        rv.setContentsMargins(30, 16, 30, 10)"),
]
for old, new in cambios:
    if old in t:
        t = t.replace(old, new, 1)
        print(f"OK: {old.strip()[:45]}...")
    else:
        print(f"AVISO: no encontrado: {old.strip()[:45]}")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
