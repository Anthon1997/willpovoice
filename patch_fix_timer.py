from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")
log = []

# 1) Dialogo mas alto
if "d.setFixedSize(520, 660)" in t:
    t = t.replace("d.setFixedSize(520, 660)", "d.setFixedSize(520, 700)", 1)
    log.append("alto 700")

# 2) Altura fija al contador (que nunca se comprima)
old = "ov.addWidget(cd)\n    cd_label"
new = "cd.setFixedHeight(58)\n    cd.setMinimumWidth(300)\n    ov.addWidget(cd)\n    cd_label"
if old in t and "cd.setFixedHeight" not in t:
    t = t.replace(old, new, 1)
    log.append("cd fijo 58px")

# 3) Proteger tambien precios y titulo de compresion
if "new_price.setStyleSheet" in t and "new_price.setFixedHeight" not in t:
    t = t.replace(
        "price_row.addWidget(new_price)",
        "new_price.setFixedHeight(44)\n    price_row.addWidget(new_price)", 1)
    log.append("precio fijo")

mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
print("OK", log)
