from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")

s = t.find("    def paintEvent(self, ev):")
e = t.find("def _add_chat_bubble")
if s == -1 or e == -1:
    raise SystemExit("ERROR: paintEvent de _Bubble no encontrado")

new_paint = '''    def paintEvent(self, ev):
        from PySide6.QtGui import (QPainter, QPainterPath,
                                   QLinearGradient, QColor, QPen)
        from PySide6.QtCore import QRectF
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect().adjusted(1, 1, -1, -8))
        body = QPainterPath()
        body.addRoundedRect(r, 14, 14)
        tail = QPainterPath()
        if self.is_user:
            x = r.right() - 12
            tail.moveTo(x, r.bottom() - 4)
            tail.cubicTo(x + 2, r.bottom(), x + 4, r.bottom() + 2,
                         x + 7, self.height() - 1)
            tail.cubicTo(x - 2, r.bottom() + 1, x - 8, r.bottom() - 1,
                         x - 14, r.bottom() - 4)
            tail.closeSubpath()
        else:
            x = r.left() + 12
            tail.moveTo(x, r.bottom() - 4)
            tail.cubicTo(x - 2, r.bottom(), x - 4, r.bottom() + 2,
                         x - 7, self.height() - 1)
            tail.cubicTo(x + 2, r.bottom() + 1, x + 8, r.bottom() - 1,
                         x + 14, r.bottom() - 4)
            tail.closeSubpath()
        path = body.united(tail)
        if self.is_user:
            g = QLinearGradient(0, 0, self.width(), self.height())
            g.setColorAt(0, QColor("#8d75ff"))
            g.setColorAt(1, QColor("#6d5df0"))
            p.fillPath(path, g)
        else:
            g = QLinearGradient(0, 0, 0, self.height())
            g.setColorAt(0, QColor("#141b32"))
            g.setColorAt(1, QColor("#0e1526"))
            p.fillPath(path, g)
            p.setPen(QPen(QColor("#2a3552"), 1))
            p.drawPath(path)
        p.end()


'''

t = t[:s] + new_paint + t[e:]
mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
print("OK: cola organica unida + gradiente sutil en burbujas")
