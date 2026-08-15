from pathlib import Path
import re, ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# 1. Badge Pro con tamano fijo (no se estira verticalmente)
old_badge = """        if premium:
            badge = QLabel("Pro")
            badge.setStyleSheet(
                f"background: {PURPLE}; color: white; border-radius: 6px;"
                " font-size: 9px; font-weight: 700; padding: 3px 6px;"
            )
            lay.addWidget(badge)"""
new_badge = """        if premium:
            badge = QLabel("Pro")
            badge.setStyleSheet(
                f"background: {PURPLE}; color: white; border-radius: 6px;"
                " font-size: 9px; font-weight: 700; padding: 3px 6px;"
            )
            badge.setFixedHeight(20)
            badge.setMaximumWidth(44)
            badge.setSizePolicy(
                QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
            )
            lay.addWidget(badge)"""
if old_badge in t:
    t = t.replace(old_badge, new_badge, 1)
    print("1. Badge Pro con tamano fijo.")
else:
    print("1. AVISO: badge no encontrado.")

# 2. Tabs compactas (menos padding, no se truncan)
n1 = len(re.findall(r"border-bottom: 2px solid", t))
t = re.sub(
    r"(border-bottom: 2px solid [^;\"]*; padding: )8px 14px",
    r"\g<1>6px 8px",
    t,
)
t = re.sub(
    r"(QPushButton \{ background: transparent; color: [^;]*; font-size: )13px(; [^}]*border-bottom)",
    r"\g<1>12px\2",
    t,
)
print(f"2. Tabs compactas ({n1} estilos ajustados).")

# 3. Tarjeta un poco mas baja y foto centrada (proporcion foto 2)
t = t.replace("self.setFixedHeight(84)", "self.setFixedHeight(78)", 1)
print("3. Altura de tarjeta 78px.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
