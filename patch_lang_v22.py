from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")

old = "    self.lang_combo.setCurrentIndex(3)"
new = "    self.lang_combo.setCurrentIndex(0)"
if old in t:
    t = t.replace(old, new, 1)
    mw.write_text(t, encoding="utf-8", newline="\n")
    ast.parse(t)
    print("OK: default lang_combo = indice 0 (Multilingue Premium)")
else:
    print("AVISO: linea no encontrada")
