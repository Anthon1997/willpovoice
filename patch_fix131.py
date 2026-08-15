from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

old = '''        f" {BORDER}; border-radius: 10px; padding: 10px 12px; font-size: 13px;"
        " min-height: 22px; }"'''
new = '''        f" {BORDER}; border-radius: 10px; padding: 7px 12px;"
        " font-size: 13px; }"'''

if old in t:
    t = t.replace(old, new, 1)
    print("QSS igualado: padding 7px y sin min-height en AMBOS combos.")
else:
    print("AVISO: texto QSS no encontrado.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
