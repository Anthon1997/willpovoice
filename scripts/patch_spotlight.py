from pathlib import Path

path = Path("ui") / "main_window.py"
text = path.read_text(encoding="utf-8")

text = text.replace(
    "from PySide6.QtCore import QPoint, QSize",
    "from PySide6.QtCore import QPoint, QRect, QSize",
)
text = text.replace(
    "from PySide6.QtGui import QBrush, QColor, QDesktopServices, QIcon, QMovie, QImageReader, QPainter, QPixmap, QTransform",
    "from PySide6.QtGui import QBrush, QColor, QDesktopServices, QIcon, QMovie, QImageReader, QPainter, QPainterPath, QPixmap, QRectF, QTransform",
)

overlay_class = '''class SpotlightOverlay(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.target_rect = None

    def set_target(self, widget):
        if widget is None:
            self.target_rect = None
        else:
            pos = widget.mapTo(self, QPoint(0, 0))
            self.target_rect = QRect(
                pos.x() - 6,
                pos.y() - 6,
                widget.width() + 12,
                widget.height() + 12,
            )

        self.update()

    def paintEvent(self, event):
        pix = QPixmap(self.size())
        pix.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pix)
        painter.fillRect(pix.rect(), QColor(0, 0, 0, 140))

        if self.target_rect is not None:
            painter.setCompositionMode(
                QPainter.CompositionMode.CompositionMode_Clear
            )
            path = QPainterPath()
            path.addRoundedRect(QRectF(self.target_rect), 10, 10)
            painter.fillPath(path, QColor(0, 0, 0, 255))

        painter.end()

        painter = QPainter(self)
        painter.drawPixmap(0, 0, pix)


'''

if "class SpotlightOverlay" not in text:
    text = text.replace(
        "class HelpWizard(QDialog):", overlay_class + "class HelpWizard(QDialog):", 1
    )

old1 = """    def __init__(self, parent=None, targets=None):
        super().__init__(parent)
        self.step = 0
        self.targets = targets or []"""
new1 = """    def __init__(self, parent=None, targets=None, overlay=None):
        super().__init__(parent)
        self.step = 0
        self.targets = targets or []
        self.overlay = overlay"""
text = text.replace(old1, new1)

old2 = """        self.setFixedWidth(440)

        layout = QVBoxLayout(self)"""
new2 = """        self.setFixedWidth(380)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)"""
text = text.replace(old2, new2)

text = text.replace(
    'self.title_label.setStyleSheet("font-size: 17px; font-weight: 700;")',
    'self.title_label.setStyleSheet("font-size: 15px; font-weight: 700;")',
)

old3 = """        if attr is None:
            frame = parent.frameGeometry()"""
new3 = """        if self.overlay:
            self.overlay.set_target(None if attr is None else getattr(parent, attr, None))

        if attr is None:
            frame = parent.frameGeometry()"""
text = text.replace(old3, new3)

old4 = """        point = target.mapToGlobal(QPoint(0, target.height()))
        pg = parent.frameGeometry()
        x = min(max(point.x(), pg.x()), pg.right() - self.width())
        y = point.y() + 8

        if y + self.height() > pg.bottom():
            y = point.y() - self.height() - 8

        self.move(x, y)"""
new4 = """        point = target.mapToGlobal(QPoint(0, target.height()))
        pg = parent.frameGeometry()
        center = point.x() + target.width() // 2
        x = center - self.width() // 2
        x = min(max(x, pg.x() + 4), pg.right() - self.width() - 4)
        y = point.y() + 10

        if y + self.height() > pg.bottom():
            y = target.mapToGlobal(QPoint(0, 0)).y() - self.height() - 10

        self.move(x, y)"""
text = text.replace(old4, new4)

old5 = """    def show_help(self) -> None:
        wizard = HelpWizard(
            self,
            targets=["""
new5 = """    def show_help(self) -> None:
        overlay = SpotlightOverlay(self)
        overlay.setGeometry(0, 0, self.width(), self.height())
        overlay.show()
        overlay.raise_()

        wizard = HelpWizard(
            self,
            targets=["""
text = text.replace(old5, new5)

old6 = """                "help_button",
            ],
        )
        wizard.exec()"""
new6 = """                "help_button",
            ],
            overlay=overlay,
        )
        wizard.exec()

        overlay.hide()
        overlay.deleteLater()"""
text = text.replace(old6, new6)

path.write_text(text, encoding="utf-8")
print("Modo guia con spotlight listo.")
