from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# 1. Nuevos iconos "text" y "doc" en make_icon
if '"text"' not in t.split("def make_icon")[1].split("class IconLabel")[0]:
    old_else = """    else:
        p.setBrush(QColor(color))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(int(s * 0.3), int(s * 0.3), int(s * 0.4), int(s * 0.4))"""
    new_elifs = """    elif kind == "text":
        p.drawLine(pt(0.3, 0.25), pt(0.7, 0.25))
        p.drawLine(pt(0.5, 0.25), pt(0.5, 0.78))
        p.drawLine(pt(0.38, 0.78), pt(0.62, 0.78))
    elif kind == "doc":
        p.drawRoundedRect(int(s * 0.28), int(s * 0.15), int(s * 0.44), int(s * 0.7), 3, 3)
        p.drawLine(pt(0.38, 0.35), pt(0.62, 0.35))
        p.drawLine(pt(0.38, 0.5), pt(0.62, 0.5))
        p.drawLine(pt(0.38, 0.65), pt(0.55, 0.65))
    else:
        p.setBrush(QColor(color))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(int(s * 0.3), int(s * 0.3), int(s * 0.4), int(s * 0.4))"""
    if old_else in t:
        t = t.replace(old_else, new_elifs, 1)
        print("1. Iconos text/doc agregados.")

# 2. Tabs con iconos (foto 2)
old_tabs = """    self.tab_text = TabButton("Texto manual")
    self.tab_file = TabButton("Importar archivo")
    self.tab_text.set_active(True)"""
new_tabs = old_tabs + """
    self.tab_text.setIcon(QIcon(make_icon("text", BLUE, 14)))
    self.tab_text.setIconSize(QSize(14, 14))
    self.tab_file.setIcon(QIcon(make_icon("doc", MUTED, 14)))
    self.tab_file.setIconSize(QSize(14, 14))"""
if old_tabs in t:
    t = t.replace(old_tabs, new_tabs, 1)
    print("2. Tabs con iconos.")

# 3. Contador dentro de barra fina redondeada
old_counter = """    self.counter_label = QLabel("0 / 5000")
    self.counter_label.setAlignment(Qt.AlignmentFlag.AlignRight)
    self.counter_label.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
    cl.addWidget(self.counter_label)"""
new_counter = """    counter_bar = QFrame()
    counter_bar.setObjectName("counterBar")
    counter_bar.setFixedHeight(26)
    counter_bar.setStyleSheet(
        f"QFrame#counterBar {{ background: #0d1424; border: 1px solid"
        f" {BORDER}; border-radius: 8px; }}"
    )
    cbl = QHBoxLayout(counter_bar)
    cbl.setContentsMargins(10, 0, 10, 0)
    self.counter_label = QLabel("0 / 5000")
    self.counter_label.setAlignment(Qt.AlignmentFlag.AlignRight)
    self.counter_label.setStyleSheet(
        f"color: {MUTED}; font-size: 10px; background: transparent;"
    )
    cbl.addWidget(self.counter_label)
    cl.addWidget(counter_bar)"""
if old_counter in t:
    t = t.replace(old_counter, new_counter, 1)
    print("3. Barra de contador como foto 2.")

# 4. Alturas compactas: combos 38, editor 120
t = t.replace("self.lang_combo.setFixedHeight(42)",
              "self.lang_combo.setFixedHeight(38)", 1)
t = t.replace("self.voice_combo.setFixedHeight(42)",
              "self.voice_combo.setFixedHeight(38)", 1)
t = t.replace("self.text_edit.setFixedHeight(140)",
              "self.text_edit.setFixedHeight(120)", 1)
print("4. Alturas compactas (combos 38, editor 120).")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
