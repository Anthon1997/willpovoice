from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# 1. Fondo azul marino en toda la ventana
old_central = """    central = QWidget()
    self.setCentralWidget(central)"""
new_central = """    central = QWidget()
    central.setObjectName("centralMain")
    central.setStyleSheet(
        "QWidget#centralMain { background: #0d1424; }"
    )
    self.setCentralWidget(central)
    self.setStyleSheet("QMainWindow { background: #0d1424; }")"""
if old_central in t:
    t = t.replace(old_central, new_central, 1)
    print("1. Fondo azul marino #0d1424 restaurado.")

# 2. Panel derecho con ID (las rayitas desaparecen)
old_rp = 'self.right_panel.setStyleSheet(f"QFrame {{ background: {BG}; border-left: 1px solid {BORDER}; }}")'
new_rp = ('self.right_panel.setObjectName("rightPanel")\n'
          '    self.right_panel.setStyleSheet(f"QFrame#rightPanel {{ background: {BG}; border-left: 1px solid {BORDER}; }}")')
if old_rp in t:
    t = t.replace(old_rp, new_rp, 1)
    print("2. Panel derecho con ID: sin rayas heredadas.")

# 3. Sidebar con ID (por limpieza)
old_sb = 'self.sidebar.setStyleSheet(f"QFrame {{ background: {SIDE_BG}; border: none; }}")'
new_sb = ('self.sidebar.setObjectName("sideBar")\n'
          '    self.sidebar.setStyleSheet(f"QFrame#sideBar {{ background: {SIDE_BG}; border: none; }}")')
if old_sb in t:
    t = t.replace(old_sb, new_sb, 1)
    print("3. Sidebar con ID.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
