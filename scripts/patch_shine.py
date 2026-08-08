from pathlib import Path

path = Path("ui") / "main_window.py"
text = path.read_text(encoding="utf-8")

text = text.replace(
    "from PySide6.QtGui import QBrush, QColor, QCursor, QDesktopServices, QIcon, QFont, QMovie, QImageReader, QPainter, QPainterPath, QPen, QPixmap, QTransform",
    "from PySide6.QtGui import QBrush, QColor, QCursor, QDesktopServices, QIcon, QFont, QLinearGradient, QMovie, QImageReader, QPainter, QPainterPath, QPen, QPixmap, QTransform",
)

shine_class = '''class ShineProgressBar(QProgressBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTextVisible(False)
        self._shine_x = -120.0

        timer = QTimer(self)
        timer.timeout.connect(self._advance_shine)
        timer.start(30)

    def _advance_shine(self) -> None:
        self._shine_x += 7

        if self._shine_x > self.width() + 120:
            self._shine_x = -120

        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        bg = QPainterPath()
        bg.addRoundedRect(0, 0, self.width(), self.height(), 6, 6)
        painter.fillPath(bg, QColor("#0d222b"))

        fraction = 0

        if self.maximum() > self.minimum():
            fraction = (self.value() - self.minimum()) / (
                self.maximum() - self.minimum()
            )

        pw = int(self.width() * fraction)

        if pw > 0:
            prog = QPainterPath()
            prog.addRoundedRect(0, 0, pw, self.height(), 6, 6)

            grad = QLinearGradient(0, 0, self.width(), 0)
            grad.setColorAt(0, QColor("#1780a8"))
            grad.setColorAt(1, QColor("#4de3b0"))
            painter.fillPath(prog, grad)

        painter.setClipPath(bg)

        shine = QPainterPath()
        shine.addRoundedRect(self._shine_x, 0, 110, self.height(), 6, 6)

        shine_grad = QLinearGradient(self._shine_x, 0, self._shine_x + 110, 0)
        shine_grad.setColorAt(0, QColor(255, 255, 255, 0))
        shine_grad.setColorAt(0.5, QColor(255, 255, 255, 80))
        shine_grad.setColorAt(1, QColor(255, 255, 255, 0))
        painter.fillPath(shine, shine_grad)

        painter.end()


'''

if "class ShineProgressBar" not in text:
    i = text.find("class ExportWorker(QThread):")
    if i != -1:
        text = text[:i] + shine_class + text[i:]

text = text.replace(
    "        bar = QProgressBar()",
    "        bar = ShineProgressBar()",
)

path.write_text(text, encoding="utf-8")
print("Brillo barrido listo.")
