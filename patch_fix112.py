from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# 1. Panel derecho mas ancho (las tarjetas necesitan ~320px)
t = t.replace("self.right_panel.setMinimumWidth(240)",
              "self.right_panel.setMinimumWidth(320)", 1)
t = t.replace("self.right_panel.setMaximumWidth(340)",
              "self.right_panel.setMaximumWidth(380)", 1)
print("1. Panel derecho 320-380px.")

# 2. Tarjeta: texto con prioridad de espacio
t = t.replace("tw.setMinimumWidth(0)", "tw.setMinimumWidth(90)", 1)
t = t.replace(
    "tw.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)",
    "tw.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)",
    1,
)
print("2. Texto de tarjeta con espacio garantizado.")

# 3. Margenes/espaciados compactos y controles menores
t = t.replace("lay.setContentsMargins(12, 0, 10, 0)",
              "lay.setContentsMargins(10, 0, 8, 0)", 1)
t = t.replace("photo.setFixedSize(46, 46)", "photo.setFixedSize(44, 44)", 1)
t = t.replace("self.heart.setFixedSize(34, 34)",
              "self.heart.setFixedSize(30, 30)", 1)
print("3. Tarjeta compacta (foto 44, corazon 30).")

# 4. Titulo del panel sin truncar
t = t.replace(
    'rt.setStyleSheet(f"color: {TEXT}; font-size: 14px; font-weight: 700;")',
    'rt.setStyleSheet(f"color: {TEXT}; font-size: 13px; font-weight: 700;")',
    1,
)
print("4. Titulo del panel compacto.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
