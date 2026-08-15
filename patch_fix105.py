from pathlib import Path
import ast

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

seg = t.split("from PySide6.QtWidgets import (")[1].split(")")[0]
if "QSizePolicy" not in seg:
    t = t.replace(
        "from PySide6.QtWidgets import (",
        "from PySide6.QtWidgets import (\n    QSizePolicy,",
        1,
    )
    print("QSizePolicy importado.")
else:
    print("QSizePolicy ya estaba.")

p.write_text(t, encoding="utf-8")
ast.parse(t)
print("SINTAXIS OK")
