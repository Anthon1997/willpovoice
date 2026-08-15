from pathlib import Path
import ast

p = Path("ui/main_window.py")
raw = p.read_text(encoding="utf-8-sig")
p.write_text(raw, encoding="utf-8")

try:
    ast.parse(raw)
    print("SINTAXIS OK")
except SyntaxError as e:
    print(f"Error en linea: {e.lineno} - {e.msg}")
    lines = raw.split("\n")
    for i in range(max(0, e.lineno - 45), min(len(lines), e.lineno + 6)):
        print(f"{i+1}: {lines[i]}")
