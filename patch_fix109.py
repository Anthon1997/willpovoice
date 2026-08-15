from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

if "self._rtab = " not in t:
    t = t.replace(
        "self.export_worker = None",
        "self.export_worker = None\n"
        '        self._rtab = "todas"\n'
        '        self._selected_voice = ""\n'
        "        self._voices = []",
        1,
    )
    print("Atributos _rtab/_selected_voice/_voices inicializados.")
else:
    print("Ya estaban inicializados.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
