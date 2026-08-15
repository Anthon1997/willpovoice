from pathlib import Path
import re, ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# ---- 1. RECOPILACION ----
i = t.find("class ActionButton")
j = t.find("\nclass TabButton")
print("--- ActionButton actual ---")
print(t[i:j])
k = t.find("def _add_neon")
print("--- _add_neon ---")
print(t[k:k + 400])
for m in ("speak_button = ActionButton", "_add_neon(self.speak_button"):
    print(f"--- {m!r} indice:", t.find(m))

# ---- 2. ActionButton foto 2: icono libre con brillo blanco ----
new_action = '''class ActionButton(QFrame):
    clicked = Signal()

    def __init__(self, glyph, text, c1, c2, parent=None):
        super().__init__(parent)
        self.setFixedHeight(46)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(18, 0, 18, 0)
        lay.setSpacing(10)
        self.icon = IconLabel(glyph, 15, "#ffffff")
        eff = QGraphicsDropShadowEffect(self.icon)
        eff.setBlurRadius(8)
        eff.setOffset(0, 0)
        eff.setColor(QColor("#ffffff"))
        self.icon.setGraphicsEffect(eff)
        self.label = QLabel(text)
        self.label.setStyleSheet(
            "color: white; font-size: 13px; font-weight: 600;"
            " background: transparent;"
        )
        lay.addStretch()
        lay.addWidget(self.icon)
        lay.addWidget(self.label)
        lay.addStretch()
        self.setStyleSheet(
            "ActionButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f" stop:0 {c1}, stop:1 {c2});"
            " border: 1px solid rgba(255,255,255,40); border-radius: 10px; }"
        )

    def mouseReleaseEvent(self, event):
        self.clicked.emit()


'''
t = re.sub(
    r"class ActionButton\(QFrame\):[\s\S]*?(?=\nclass TabButton)",
    new_action,
    t,
    count=1,
)
print("2. ActionButton foto 2 (icono libre + brillo blanco).")

# ---- 3. Neon mas suave (foto 2) ----
old_neon = re.search(
    r"def _add_neon\(self, widget, color\):[\s\S]*?setBlurRadius\((\d+)\)", t)
if old_neon:
    t = t.replace(
        f"setBlurRadius({old_neon.group(1)})",
        "setBlurRadius(16)",
        1,
    )
    print(f"3. Neon atenuado (blur {old_neon.group(1)} -> 16).")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
