from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

old = "MainWindow._on_history_click = _on_history_click\n"
if old in t:
    t = t.replace(old, "", 1)
    print("Asignacion huerfana eliminada.")
else:
    print("AVISO: linea no encontrada.")

# Verificar que las nuevas si esten
for fn in ("_load_entry", "_delete_entry", "_load_history"):
    print(fn, "asignado:", f"MainWindow.{fn} = {fn}" in t)

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
