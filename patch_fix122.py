from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

old1 = """        texts = QVBoxLayout()
        texts.setSpacing(2)"""
new1 = """        texts = QVBoxLayout()
        texts.setSpacing(2)
        texts.setContentsMargins(0, 12, 0, 0)"""
if old1 in t:
    t = t.replace(old1, new1, 1)
    print("1. Margen superior del bloque de texto.")

old2 = """        lay.addWidget(self.icon, 0, Qt.AlignmentFlag.AlignVCenter)
        lay.addLayout(texts, 1)"""
new2 = """        lay.addWidget(self.icon, 0, Qt.AlignmentFlag.AlignVCenter)
        lay.addLayout(texts, 1, Qt.AlignmentFlag.AlignTop)"""
if old2 in t:
    t = t.replace(old2, new2, 1)
    print("2. Texto anclado arriba: numero a la par del icono.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
