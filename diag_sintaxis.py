from pathlib import Path
import ast

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("Error en linea:", e.lineno)
    lines = t.split("\n")
    for i in range(max(0, e.lineno - 40), min(len(lines), e.lineno + 5)):
        print(f"{i+1}: {lines[i]}")
