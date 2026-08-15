from pathlib import Path
import ast

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

# 1. set_collapsed sin tocar alineaciones (solo margenes)
old_sc = """    def set_collapsed(self, collapsed):
        self.label.setVisible(not collapsed)
        lay = self.layout()
        if collapsed:
            lay.setContentsMargins(0, 0, 0, 0)
            self.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            lay.setContentsMargins(16, 0, 12, 0)
            self.icon.setAlignment(Qt.AlignmentFlag.AlignLeft)"""
new_sc = """    def set_collapsed(self, collapsed):
        self.label.setVisible(not collapsed)
        lay = self.layout()
        if collapsed:
            lay.setContentsMargins(24, 0, 24, 0)
        else:
            lay.setContentsMargins(16, 0, 12, 0)"""
if old_sc in t:
    t = t.replace(old_sc, new_sc, 1)
    print("1. set_collapsed limpio (iconos siempre alineados).")

# 2. Portada encogible (no impone ancho minimo)
if "cover.setScaledContents(True)" not in t:
    t = t.replace(
        "hl.addWidget(cover)",
        "cover.setScaledContents(True)\n"
        "        cover.setMinimumWidth(0)\n"
        "        cover.setSizePolicy(\n"
        "            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)\n"
        "        hl.addWidget(cover)",
        1,
    )
    print("2. Portada encogible.")

# 3. Panel derecho con rangos flexibles
t = t.replace(
    "self.right_panel.setMinimumWidth(300)",
    "self.right_panel.setMinimumWidth(240)",
    1,
)
t = t.replace(
    "self.right_panel.setMaximumWidth(360)",
    "self.right_panel.setMaximumWidth(340)",
    1,
)
print("3. Panel derecho flexible (240-340).")

# 4. Tamano minimo de ventana razonable
if "self.setMinimumSize(980, 640)" not in t:
    t = t.replace(
        "self.resize(1280, 800)",
        "self.resize(1280, 800)\n        self.setMinimumSize(980, 640)",
        1,
    )
    print("4. Ventana minima 980x640.")

# 5. Controles centrales encogibles
if "self.text_edit.setMinimumWidth(150)" not in t:
    t = t.replace(
        "self.text_edit.setFixedHeight(150)",
        "self.text_edit.setFixedHeight(150)\n"
        "        self.text_edit.setMinimumWidth(150)",
        1,
    )
    t = t.replace(
        'self.lang_combo.addItems(["Español (España)", "Inglés (EEUU)", "Todos"])',
        'self.lang_combo.addItems(["Español (España)", "Inglés (EEUU)", "Todos"])\n'
        "        self.lang_combo.setMinimumWidth(120)\n"
        "        self.voice_combo.setMinimumWidth(160)",
        1,
    )
    print("5. Controles centrales encogibles.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
