from pathlib import Path
import ast

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

# 1. Textos encogibles para que play y + siempre quepan
old = """        texts.addWidget(name_label)
        texts.addWidget(sub_label)
        layout.addWidget(texts_widget, 1)"""
new = """        name_label.setMinimumWidth(0)
        name_label.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred
        )
        sub_label.setMinimumWidth(0)
        sub_label.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred
        )
        texts_widget.setMinimumWidth(0)
        texts.addWidget(name_label)
        texts.addWidget(sub_label)
        layout.addWidget(texts_widget, 1)"""
if old in t:
    t = t.replace(old, new, 1)
    print("1. Textos encogibles (play y + siempre visibles).")
else:
    print("1. AVISO: anchor textos no encontrado.")

# 2. Dock mas ancho: 340px para filas completas
if "[panel], [320], Qt.Orientation.Horizontal" in t:
    t = t.replace(
        "[panel], [320], Qt.Orientation.Horizontal",
        "[panel], [340], Qt.Orientation.Horizontal",
        1,
    )
    print("2a. resizeDocks 340.")
if "panel.setMinimumWidth(320)" in t:
    t = t.replace("panel.setMinimumWidth(320)", "panel.setMinimumWidth(340)", 1)
    print("2b. minWidth 340.")

# 3. Filas un poco mas compactas horizontalmente
old = "        layout.setContentsMargins(10, 8, 8, 8)"
new = "        layout.setContentsMargins(8, 8, 6, 8)"
if old in t:
    t = t.replace(old, new, 1)
    print("3. Margenes de fila compactos.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(p.read_text(encoding="utf-8"))
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
