from pathlib import Path
import re, ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# ---- 1. RECOPILACION ----
for marker in ("lay.addStretch()\n        self.set_active(False)",
               "def set_collapsed",
               '("help", "Ayuda", self.show_help)'):
    i = t.find(marker)
    print(f"--- marcador {marker[:30]!r} en indice {i}")

# ---- 2. Import QSpacerItem ----
if "from PySide6.QtWidgets import QSpacerItem" not in t:
    t = t.replace(
        "from app.config import load_settings, save_settings",
        "from PySide6.QtWidgets import QSpacerItem\n"
        "from app.config import load_settings, save_settings",
        1,
    )
    print("2. QSpacerItem importado.")

# ---- 3. NavButton: spacer guardado en vez de addStretch ----
old_nav = """        lay.addWidget(self.icon)
        lay.addWidget(self.label)
        lay.addStretch()
        self.set_active(False)"""
new_nav = """        lay.addWidget(self.icon)
        lay.addWidget(self.label)
        self._spacer = QSpacerItem(
            0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        lay.addSpacerItem(self._spacer)
        self.set_active(False)"""
if old_nav in t:
    t = t.replace(old_nav, new_nav, 1)
    print("3. Spacer controlado en NavButton.")

# ---- 4. set_collapsed: icono centrado en su cuadro ----
new_collapsed = '''    def set_collapsed(self, collapsed):
        self.label.setVisible(not collapsed)
        lay = self.layout()
        if collapsed:
            lay.setContentsMargins(0, 0, 0, 0)
            lay.setSpacing(0)
            self._spacer.changeSize(
                0, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
            self.icon.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            self.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            lay.setContentsMargins(14, 0, 12, 0)
            lay.setSpacing(12)
            self._spacer.changeSize(
                0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
            self.icon.setFixedSize(20, 20)
            self.icon.setAlignment(Qt.AlignmentFlag.AlignLeft)
        lay.invalidate()

'''
t = re.sub(
    r"    def set_collapsed\(self, collapsed\):[\s\S]*?(?=\n    def )",
    new_collapsed,
    t,
    count=1,
)
print("4. set_collapsed con centrado real.")

# ---- 5. Ayuda/Soporte tambien se colapsan ----
old_extra = """        btn.clicked.connect(lambda _=False, f=fn: f())
        sb.addWidget(btn)"""
new_extra = old_extra + "\n        self._nav.append((btn, -1))"
if old_extra in t:
    t = t.replace(old_extra, new_extra, 1)
    print("5. Ayuda/Soporte entran al colapso (adios 'A' y 'S').")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
