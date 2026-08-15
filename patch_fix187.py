from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# ---- 1. Eliminar TODAS las inserciones previas del import ----
bad = "from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput\n"
cuantas = t.count(bad)
t = t.replace(bad, "")
print(f"1. Inserciones malas eliminadas: {cuantas}")

# ---- 2. Reinsertar en punto seguro (nivel de modulo) ----
imp = bad
anchor = t.find("def _lic_pix")
if anchor == -1:
    anchor = t.find("class UpdateWorker")
if anchor != -1:
    t = t[:anchor] + imp + "\n\n" + t[anchor:]
    print("2. Import reubicado antes de def _lic_pix.")
else:
    print("AVISO: sin ancla segura.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
