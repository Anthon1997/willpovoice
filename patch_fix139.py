from pathlib import Path
import re, ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# ---- 1. RECOPILACION ----
i = t.find("def _make_overlay")
j = t.find("def set_selected")
print("--- _make_overlay actual ---")
print(t[i:j])

# ---- 2. Overlay compuesto sobre la foto real ----
new_overlay = '''    def _make_overlay(self):
        size = 40
        base = self._avatar_pix.scaled(
            size, size, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation)
        pix = base.copy(0, 0, size, size)
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QColor(0, 0, 0, 100))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(0, 0, size, size)
        p.setPen(QPen(QColor("#f5b301"), 2))
        p.drawEllipse(1, 1, size - 2, size - 2)
        p.setBrush(QColor("#ffffff"))
        p.setPen(Qt.PenStyle.NoPen)
        if self._playing:
            p.drawRoundedRect(14, 13, 5, 14, 2, 2)
            p.drawRoundedRect(22, 13, 5, 14, 2, 2)
        else:
            p.drawPolygon(QPolygon(
                [QPoint(16, 12), QPoint(16, 28), QPoint(29, 20)]))
        p.end()
        return pix

'''
t = re.sub(
    r"    def _make_overlay\(self\):[\s\S]*?(?=    def set_selected)",
    new_overlay,
    t,
    count=1,
)
print("2. Overlay sobre la foto real (semitransparente de verdad).")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
