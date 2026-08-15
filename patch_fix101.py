from pathlib import Path

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

# 1. Quitar QPolygon del import de QtCore
t = t.replace(
    "from PySide6.QtCore import Qt, QThread, QTimer, QUrl, Signal, QSize, QPolygon",
    "from PySide6.QtCore import Qt, QThread, QTimer, QUrl, Signal, QSize",
    1,
)

# 2. Agregar QPolygon al import de QtGui
if "QPolygon" not in t.split("from PySide6.QtGui")[1].split(")")[0]:
    t = t.replace(
        "QPen, QPixmap,",
        "QPen, QPixmap, QPolygon,",
        1,
    )

p.write_text(t, encoding="utf-8")

import ast
ast.parse(t)
print("Imports corregidos - SINTAXIS OK")
