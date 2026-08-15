from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# 1. Eliminar la barra del contador (etiqueta simple)
old_counter = """    counter_bar = QFrame()
    counter_bar.setObjectName("counterBar")
    counter_bar.setFixedHeight(26)
    counter_bar.setStyleSheet(
        f"QFrame#counterBar {{ background: #0d1424; border: 1px solid"
        f" {BORDER}; border-radius: 8px; }}"
    )
    cbl = QHBoxLayout(counter_bar)
    cbl.setContentsMargins(10, 0, 10, 0)
    self.counter_label = QLabel("0 / 5000")
    self.counter_label.setAlignment(Qt.AlignmentFlag.AlignRight)
    self.counter_label.setStyleSheet(
        f"color: {MUTED}; font-size: 10px; background: transparent;"
    )
    cbl.addWidget(self.counter_label)
    cl.addWidget(counter_bar)"""
new_counter = """    self.counter_label = QLabel("0 / 5000")
    self.counter_label.setAlignment(Qt.AlignmentFlag.AlignRight)
    self.counter_label.setStyleSheet(
        f"color: {MUTED}; font-size: 10px; background: transparent;"
    )
    cl.addWidget(self.counter_label)"""
if old_counter in t:
    t = t.replace(old_counter, new_counter, 1)
    print("1. Barra del contador eliminada.")

# 2. Combos con geometria identica (guia: voz seleccionada)
old_geo = """    self.lang_combo.setFixedHeight(38)"""
new_geo = """    self.lang_combo.setFixedHeight(38)
    self.lang_combo.setSizePolicy(
        QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    self.lang_combo.setMinimumWidth(0)"""
if old_geo in t and "setSizePolicy" not in t.split("lang_combo.setFixedHeight")[1][:200]:
    t = t.replace(old_geo, new_geo, 1)
    print("2a. Lang combo con politica fija.")

old_geo2 = """    self.voice_combo.setFixedHeight(38)"""
new_geo2 = """    self.voice_combo.setFixedHeight(38)
    self.voice_combo.setSizePolicy(
        QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    self.voice_combo.setMinimumWidth(0)"""
if old_geo2 in t:
    t = t.replace(old_geo2, new_geo2, 1)
    print("2b. Voice combo con politica fija.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
