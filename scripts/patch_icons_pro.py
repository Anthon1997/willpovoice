from pathlib import Path

path = Path("ui") / "main_window.py"
text = path.read_text(encoding="utf-8")

text = text.replace(
    "        self.open_menu.setIconSize(QSize(18, 18))\n", ""
)

text = text.replace(
    "QPainter, QPainterPath, QPixmap",
    "QPainter, QPainterPath, QPen, QPixmap",
)

new_icon = '''    def _format_icon(self, color: str, label: str) -> QIcon:
        pix = QPixmap(22, 26)
        pix.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        body = QColor(color)
        dark = body.darker(160)

        page = QPainterPath()
        page.moveTo(4, 1)
        page.lineTo(14, 1)
        page.lineTo(21, 8)
        page.lineTo(21, 22)
        page.quadTo(21, 25, 18, 25)
        page.lineTo(4, 25)
        page.quadTo(1, 25, 1, 22)
        page.lineTo(1, 4)
        page.quadTo(1, 1, 4, 1)
        page.closeSubpath()
        painter.fillPath(page, body)

        fold = QPainterPath()
        fold.moveTo(14, 1)
        fold.lineTo(21, 8)
        fold.lineTo(14, 8)
        fold.closeSubpath()
        painter.fillPath(fold, dark)

        painter.setPen(QColor("white"))
        size = 7 if len(label) <= 3 else 5
        painter.setFont(QFont("Segoe UI", size, QFont.Weight.Bold))
        painter.drawText(
            QRect(1, 8, 21, 9), Qt.AlignmentFlag.AlignCenter, label
        )

        painter.setPen(QPen(QColor("white"), 1.4))
        painter.drawLine(5, 20, 17, 20)
        painter.drawLine(5, 23, 13, 23)
        painter.end()

        return QIcon(pix)

'''

start = text.find("    def _format_icon(self")

if start != -1:
    end = text.find("    def ", start + 10)

    if end != -1:
        text = text[:start] + new_icon + text[end:]
        print("Iconos de documento listos.")
else:
    print("ERROR: _format_icon no encontrado.")

path.write_text(text, encoding="utf-8")
