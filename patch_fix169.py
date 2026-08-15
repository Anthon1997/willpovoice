from pathlib import Path
import ast

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

old = "        pwrap.setContentsMargins(20, 0, 20, 14)"
new = "        pwrap.setContentsMargins(26, 0, 26, 14)"
if old in t:
    t = t.replace(old, new, 1)
    print("Tarjeta Premium aun mas estrecha (margenes 26).")
else:
    print("AVISO: ancla no encontrada.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
