from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

print("lang fixedHeight:", t.count("lang_combo.setFixedHeight"))
print("voice fixedHeight:", t.count("voice_combo.setFixedHeight"))

# 1. Quitar min-height del QSS (posible inflador)
t = t.replace(" font-size: 13px; min-height: 18px; }",
              " font-size: 13px; }", 1)
t = t.replace(" font-size: 13px; min-height: 22px; }",
              " font-size: 13px; }", 1)
print("1. min-height eliminado del QSS.")

# 2. Bucle de igualdad total tras el installEventFilter
old_anchor = "    self.voice_combo.installEventFilter(self)"
new_block = old_anchor + """
    for _cb in (self.lang_combo, self.voice_combo):
        _cb.setFixedHeight(38)
        _cb.setIconSize(QSize(18, 14))
        _cb.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)"""
if old_anchor in t and "for _cb in (self.lang_combo" not in t:
    t = t.replace(old_anchor, new_block, 1)
    print("2. Bucle de igualdad de combos insertado.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
