from pathlib import Path
import re, ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# Corregir el stylesheet del boton de opciones avanzadas
t = re.sub(
    r"self\.adv_button\.setStyleSheet\([\s\S]*?\n    \)",
    'self.adv_button.setStyleSheet(\n'
    '        f"QPushButton {{ background: {CARD2}; color: {TEXT}; '
    'border: 1px solid {BORDER}; border-radius: 10px; '
    'padding: 8px 14px; text-align: left; }}"\n'
    '    )',
    t,
    count=1,
)
print("adv_button corregido. Ocurrencias de .format( restantes:",
      t.count(".format("))

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
