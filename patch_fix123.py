from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

old = """        lay.addWidget(self.icon, 0, Qt.AlignmentFlag.AlignVCenter)
        lay.addLayout(texts, 1, Qt.AlignmentFlag.AlignTop)"""
new = """        texts_widget = QWidget()
        texts_widget.setLayout(texts)
        texts_widget.setStyleSheet("background: transparent;")
        lay.addWidget(self.icon, 0, Qt.AlignmentFlag.AlignVCenter)
        lay.addWidget(texts_widget, 1, Qt.AlignmentFlag.AlignTop)"""

if old in t:
    t = t.replace(old, new, 1)
    print("Textos en QWidget con AlignTop (addLayout sin alineacion).")
else:
    print("AVISO: patron no encontrado.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
