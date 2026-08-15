from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

lines = t.split("\n")
out = []
in_block = False
fixed = 0
for ln in lines:
    if "lowered = [v.lower() for v in voices]" in ln:
        in_block = ln.startswith("            ")
    if in_block and ln.startswith("            "):
        ln = ln[4:]
        fixed += 1
    out.append(ln)
    if in_block and ln.strip() == "voices = dedup":
        in_block = False
t = "\n".join(out)
print(f"Lineas re-sangradas: {fixed}")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
