from pathlib import Path
import ast

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

old = """        self.header_widget.layout().addWidget(
            self.voices_button, 0, Qt.AlignmentFlag.AlignVCenter
        )"""

new = """        self.header_widget.layout().insertWidget(
            0,
            self.voices_button,
            0,
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
        )"""

if old in t:
    t = t.replace(old, new, 1)
    print("Boton Voces movido a la esquina superior izquierda.")
else:
    print("AVISO: patron no encontrado.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(p.read_text(encoding="utf-8"))
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
