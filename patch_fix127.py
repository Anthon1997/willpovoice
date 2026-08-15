from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# 1. Editor mas bajo (el usuario lo autoriza)
t = t.replace(
    "self.text_edit.setFixedHeight(170)",
    "self.text_edit.setFixedHeight(140)",
    1,
)
print("1. Editor a 140px.")

# 2. Ambos combos con la MISMA altura fija
if "self.lang_combo.setFixedHeight(42)" not in t:
    t = t.replace(
        "self.lang_combo.setStyleSheet(combo_qss)",
        "self.lang_combo.setStyleSheet(combo_qss)\n"
        "    self.lang_combo.setFixedHeight(42)",
        1,
    )
    print("2a. Lang combo 42px.")

if "self.voice_combo.setFixedHeight(42)" not in t:
    t = t.replace(
        "self.voice_combo.installEventFilter(self)",
        "self.voice_combo.setFixedHeight(42)\n"
        "    self.voice_combo.installEventFilter(self)",
        1,
    )
    print("2b. Voice combo 42px.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
