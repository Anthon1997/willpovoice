from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# ---- 1. Verificar si QDialog ya esta importado ----
lineas_import = [
    ln for ln in t.splitlines()
    if ln.startswith("from PySide6.QtWidgets import")
    or (ln.strip().startswith("QDialog") and ln.startswith(" "))
]
ya = any("QDialog" in ln for ln in lineas_import)
print("QDialog ya importado:", ya)

# ---- 2. Import de seguridad antes de UpdateWorker ----
anchor = "class UpdateWorker(QThread):"
seguro = ("from PySide6.QtWidgets import (QDialog, QPlainTextEdit,\n"
          "    QProgressBar)\n\n\n")
if not ya and anchor in t:
    t = t.replace(anchor, seguro + anchor, 1)
    print("2. Import de seguridad agregado (QDialog/QPlainTextEdit/QProgressBar).")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
