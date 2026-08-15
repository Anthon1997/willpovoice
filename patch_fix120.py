from pathlib import Path
import re, ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# 1. StatsCard: icono con neon + numero alineado a la par del icono
new_stats = '''class StatsCard(QFrame):
    def __init__(self, glyph, color, title, value, parent=None):
        super().__init__(parent)
        self.setFixedHeight(96)
        self.setObjectName("statsCard")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(18, 0, 18, 0)
        lay.setSpacing(14)
        box = QFrame()
        box.setFixedSize(44, 44)
        box.setStyleSheet(
            "QFrame { background: rgba(45,212,191,18); border-radius: 12px; }"
        )
        bl = QVBoxLayout(box)
        bl.setContentsMargins(0, 0, 0, 0)
        ic = IconLabel(glyph, 17, color)
        ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bl.addWidget(ic)
        eff = QGraphicsDropShadowEffect(box)
        eff.setBlurRadius(14)
        eff.setOffset(0, 0)
        eff.setColor(QColor(color))
        box.setGraphicsEffect(eff)
        texts = QVBoxLayout()
        texts.setSpacing(2)
        t1 = QLabel(title)
        t1.setStyleSheet(
            f"color: {MUTED}; font-size: 12px; background: transparent;"
        )
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(
            f"color: {TEXT}; font-size: 20px; font-weight: 700;"
            " background: transparent;"
        )
        texts.addWidget(t1)
        texts.addWidget(self.value_label)
        lay.addWidget(box, 0, Qt.AlignmentFlag.AlignVCenter)
        lay.addLayout(texts, 1)
        self.setStyleSheet(
            f"QFrame#statsCard {{ background: {CARD}; border: 1px solid"
            f" {BORDER}; border-radius: 14px; }}"
        )


'''
t = re.sub(
    r"class StatsCard\(QFrame\):[\s\S]*?(?=\nclass VoiceCard)",
    new_stats,
    t,
    count=1,
)
print("1. StatsCard con neon y numeros alineados.")

# 2. Editor de texto con fondo navy
old_te = """    self.text_edit.setMinimumWidth(150)"""
new_te = """    self.text_edit.setMinimumWidth(150)
    self.text_edit.setStyleSheet(
        f"QPlainTextEdit {{ background: #0d1424; color: {TEXT};"
        f" border: 1px solid {BORDER}; border-radius: 12px; padding: 10px;"
        " font-size: 14px; selection-background-color: #3b82f6; }"
    )"""
if old_te in t:
    t = t.replace(old_te, new_te, 1)
    print("2. Editor de texto navy.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
