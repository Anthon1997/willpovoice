from pathlib import Path
import re
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# Todas las funciones a nivel de modulo que reciben self
defs = re.findall(r"^def (\w+)\(self", t, re.M)
missing = [n for n in defs if f"MainWindow.{n} = {n}" not in t]

print(f"Funciones metodo: {len(defs)} | Asignaciones faltantes: {len(missing)}")
for n in missing:
    print("  FALTA:", n)

if missing:
    t += "\n" + "\n".join(f"MainWindow.{n} = {n}" for n in missing) + "\n"
    p.write_text(t, encoding="utf-8")
    print("Asignaciones restauradas.")
else:
    print("Nada que restaurar.")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
