from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# 1. Scoped stylesheets: el borde ya no se filtra a los hijos
t = t.replace(
    'header.setStyleSheet(f"QFrame {{ background: {CARD}; border-radius: 16px; }}")',
    'header.setObjectName("headerCard")\n'
    '    header.setStyleSheet(f"QFrame#headerCard {{ background: {CARD}; border-radius: 16px; }}")',
    1,
)
t = t.replace(
    'card.setStyleSheet(f"QFrame {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 16px; }}")',
    'card.setObjectName("convCard")\n'
    '    card.setStyleSheet(f"QFrame#convCard {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 16px; }}")',
    1,
)
t = t.replace(
    'player.setStyleSheet(f"QFrame {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 14px; }}")',
    'player.setObjectName("playerBar")\n'
    '    player.setStyleSheet(f"QFrame#playerBar {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 14px; }}")',
    1,
)
print("1. Stylesheets con ID: sin rayas en 0:00/volumen/Idioma.")

# 2. Botones de accion expandibles hasta los cuadrados derechos
old_acts = """    acts.addWidget(self.speak_button)
    acts.addWidget(self.stop_button)
    acts.addWidget(self.export_button)
    acts.addStretch()
    acts.addWidget(self.copy_button)"""
new_acts = """    acts.addWidget(self.speak_button, 1)
    acts.addWidget(self.stop_button, 1)
    acts.addWidget(self.export_button, 1)
    acts.addSpacing(12)
    acts.addWidget(self.copy_button)"""
if old_acts in t:
    t = t.replace(old_acts, new_acts, 1)
    print("2. Botones de accion organicos (stretch 1).")

# 3. Centrar contenido dentro de ActionButton al expandirse
old_ab = """        lay.addWidget(box)
        lay.addWidget(self.label)
        self.setStyleSheet("""
new_ab = """        lay.addStretch()
        lay.addWidget(box)
        lay.addWidget(self.label)
        lay.addStretch()
        self.setStyleSheet("""
if old_ab in t:
    t = t.replace(old_ab, new_ab, 1)
    print("3. Contenido centrado en botones expandidos.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
