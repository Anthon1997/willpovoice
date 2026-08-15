from pathlib import Path
import ast

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

# ---- 1. Imagen pegada a los bordes (sin huecos) ----
old_lv = """        lv = QVBoxLayout(left)
        lv.setContentsMargins(8, 10, 8, 10)
        lv.setSpacing(12)"""
new_lv = """        lv = QVBoxLayout(left)
        lv.setContentsMargins(0, 0, 0, 0)
        lv.setSpacing(10)"""
if old_lv in t:
    t = t.replace(old_lv, new_lv, 1)
    print("1. Imagen pegada a ventana y rayita neon.")

# ---- 2. Tarjeta Premium con margenes externos como foto 1 ----
old_add = "        lv.addWidget(pcard, 0)"
new_add = """        pwrap = QHBoxLayout()
        pwrap.setContentsMargins(10, 0, 10, 12)
        pwrap.addWidget(pcard)
        lv.addLayout(pwrap, 0)"""
if old_add in t:
    t = t.replace(old_add, new_add, 1)
    print("2. Tarjeta con margenes 10/12 como el mockup.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
