from pathlib import Path
import re, ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

new_stats = '''class StatsCard(QFrame):
    def __init__(self, glyph, color, title, value, parent=None):
        super().__init__(parent)
        self.setFixedHeight(88)
        self.setObjectName("statsCard")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(18, 0, 16, 0)
        lay.setSpacing(14)
        self.icon = IconLabel(glyph, 22, color)
        self.icon.setFixedSize(30, 30)
        eff = QGraphicsDropShadowEffect(self.icon)
        eff.setBlurRadius(12)
        eff.setOffset(0, 0)
        eff.setColor(QColor(color))
        self.icon.setGraphicsEffect(eff)
        texts = QVBoxLayout()
        texts.setSpacing(2)
        t1 = QLabel(title)
        t1.setStyleSheet(
            f"color: {MUTED}; font-size: 12px; background: transparent;"
        )
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(
            f"color: {TEXT}; font-size: 19px; font-weight: 700;"
            " background: transparent;"
        )
        texts.addWidget(t1)
        texts.addWidget(self.value_label)
        lay.addWidget(self.icon, 0, Qt.AlignmentFlag.AlignVCenter)
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
print("StatsCard estilo foto 2 (icono libre con neon + numeros a la par).")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
