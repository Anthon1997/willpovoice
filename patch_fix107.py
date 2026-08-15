from pathlib import Path
import ast

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

old = """        self._build_ui()
        self._connect_signals()"""
new = """        self._build_ui()
        if not hasattr(self, "voice_combo"):
            self.voice_combo = QComboBox()
        self._connect_signals()"""

if old in t and "hasattr(self, \"voice_combo\")" not in t:
    t = t.replace(old, new, 1)
    print("Guard de voice_combo agregado tras _build_ui.")
else:
    print("AVISO: anchor no encontrado o guard ya existe.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
