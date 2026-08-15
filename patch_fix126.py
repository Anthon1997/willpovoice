from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# 1. Combos mas compactos (la fila ya no empuja al editor)
t = t.replace(
    "border-radius: 10px; padding: 10px 12px; font-size: 13px; min-height: 22px; }",
    "border-radius: 10px; padding: 7px 12px; font-size: 13px; min-height: 18px; }",
    1,
)
t = t.replace(
    "QComboBox { padding: 10px 84px 10px 12px; }",
    "QComboBox { padding: 7px 84px 7px 12px; }",
    1,
)
print("1. Combos compactos.")

# 2. Editor de texto recupera altura
t = t.replace(
    "self.text_edit.setFixedHeight(150)",
    "self.text_edit.setFixedHeight(170)",
    1,
)
print("2. Editor a 170px.")

# 3. Espaciados internos de la fila sel mas ajustados
t = t.replace("sel.setSpacing(14)", "sel.setSpacing(12)", 1)
t = t.replace("col1.setSpacing(6)", "col1.setSpacing(4)", 1)
t = t.replace("col2.setSpacing(6)", "col2.setSpacing(4)", 1)
print("3. Espaciados ajustados.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
