from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

old = "from PySide6.QtCore import QThread as _QThread, pyqtSignal as _pyqtSignal"
new = "from PySide6.QtCore import QThread as _QThread, Signal as _pyqtSignal"

if old in t:
    t = t.replace(old, new, 1)
    p.write_text(t, encoding="utf-8", newline="\n")
    ast.parse(t)
    print("OK: pyqtSignal -> Signal (PySide6)")
else:
    print("AVISO: linea no encontrada")
