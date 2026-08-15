from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# ---- 1. RECOPILACION ----
i = t.find("tl.addWidget(n)")
print("--- zona textos actual ---")
print(t[i - 200:i + 120])

# ---- 2. Sello dorado entre nombre y acento ----
old = """        tl.addWidget(n)
        tl.addWidget(s)"""
new = """        tl.addWidget(n)
        if premium:
            g = QLabel("WillpoVoice Premium")
            g.setStyleSheet(
                "color: #f5b301; font-size: 9px; font-weight: 600;"
                " background: transparent;"
            )
            tl.addWidget(g)
        tl.addWidget(s)"""
if old in t:
    t = t.replace(old, new, 1)
    print("2. Sello dorado intermedio agregado.")

# ---- 3. Tarjeta un poco mas alta para 3 lineas ----
t = t.replace("self.setFixedHeight(70)", "self.setFixedHeight(78)", 1)
print("3. Tarjeta 78px.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
