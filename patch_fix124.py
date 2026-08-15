from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

if "IconLabel(glyph, 26, color)" not in t:
    t = t.replace(
        "self.icon = IconLabel(glyph, 22, color)",
        "self.icon = IconLabel(glyph, 26, color)",
        1,
    )
    t = t.replace(
        "self.icon.setFixedSize(30, 30)",
        "self.icon.setFixedSize(36, 36)",
        1,
    )
    t = t.replace(
        "eff.setBlurRadius(12)",
        "eff.setBlurRadius(14)",
        1,
    )
    print("Iconos de stats agrandados (26/36) con neon 14.")
else:
    print("Ya estaban agrandados.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
