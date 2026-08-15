from pathlib import Path
import re, ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# 1. Tarjetas sin borde por defecto (adios rayas verticales)
old_sel = """    def set_selected(self, selected):
        if selected:
            self.setStyleSheet(
                f"VoiceCard {{ background: {CARD2}; border: 1px solid {PURPLE}; border-radius: 14px; }}"
            )
        else:
            self.setStyleSheet(
                f"VoiceCard {{ background: {CARD}; border: 1px solid {BORDER};"
                f" border-radius: 14px; }} VoiceCard:hover {{ background: {CARD2}; }}"
            )"""
new_sel = """    def set_selected(self, selected):
        if selected:
            self.setStyleSheet(
                f"VoiceCard {{ background: {CARD2}; border: 1px solid {PURPLE}; border-radius: 14px; }}"
            )
        else:
            self.setStyleSheet(
                f"VoiceCard {{ background: {CARD}; border: none;"
                f" border-radius: 14px; }} VoiceCard:hover {{ background: {CARD2}; }}"
            )"""
if old_sel in t:
    t = t.replace(old_sel, new_sel, 1)
    print("1. Tarjetas limpias sin rayas.")

# 2. ActionButton estilo foto 2 (icono en cajita oscura + borde color)
new_action = '''class ActionButton(QFrame):
    clicked = Signal()

    def __init__(self, glyph, text, c1, c2, parent=None):
        super().__init__(parent)
        self.setFixedHeight(48)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 0, 18, 0)
        lay.setSpacing(10)
        box = QFrame()
        box.setFixedSize(28, 28)
        box.setStyleSheet(
            "QFrame { background: rgba(0,0,0,70); border-radius: 8px; }"
        )
        bl = QVBoxLayout(box)
        bl.setContentsMargins(0, 0, 0, 0)
        self.icon = IconLabel(glyph, 13, "#ffffff")
        self.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bl.addWidget(self.icon)
        self.label = QLabel(text)
        self.label.setStyleSheet(
            "color: white; font-size: 13px; font-weight: 600;"
            " background: transparent;"
        )
        lay.addWidget(box)
        lay.addWidget(self.label)
        self.setStyleSheet(
            "ActionButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f" stop:0 {c1}, stop:1 {c2}); border: 1px solid {c2};"
            " border-radius: 10px; }"
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
print("2. ActionButton estilo foto 2.")

# 3. Degradados mas fieles a la referencia
t = t.replace(
    'self.speak_button = ActionButton("play", "Reproducir", BLUE, "#1d4ed8")',
    'self.speak_button = ActionButton("play", "Reproducir", "#123a8c", "#2563eb")',
    1,
)
t = t.replace(
    'self.stop_button = ActionButton("stop", "Detener", MAGENTA, PURPLE)',
    'self.stop_button = ActionButton("stop", "Detener", "#6d1fa6", "#c026d3")',
    1,
)
t = t.replace(
    'self.export_button = ActionButton("download", "Exportar", TEAL, "#0d9488")',
    'self.export_button = ActionButton("download", "Exportar", "#0f766e", "#10b981")',
    1,
)
print("3. Degradados ajustados.")

# 4. Play del reproductor redondo con borde teal
old_pp = """    self.player_play = SquareButton("play", "Reproducir")
    self.player_play.setFixedSize(40, 40)"""
new_pp = old_pp + """
    self.player_play.setStyleSheet(
        f"SquareButton {{ background: {CARD}; border: 1px solid {TEAL};"
        " border-radius: 20px; }"
        f"SquareButton:hover {{ background: {CARD2}; }}"
    )"""
if old_pp in t:
    t = t.replace(old_pp, new_pp, 1)
    print("4. Play redondo con borde teal.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
