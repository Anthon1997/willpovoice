from pathlib import Path
import ast

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

# 1. Bloque de foto: avatar circular recortado con anillo
old_photo = '''        photo = QLabel()
        photo.setFixedSize(36, 36)
        pix = None
        if photo_path is not None:
            pp = Path(photo_path)
            if pp.exists():
                pix = QPixmap(str(pp)).scaled(
                    36,
                    36,
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation,
                )
        if pix is None or pix.isNull():
            pix = self._initials_pixmap()
        photo.setPixmap(pix)
        photo.setScaledContents(True)
        ring = "2px solid #ffd75e;" if premium else "1px solid #232f4b;"
        photo.setStyleSheet(
            "background: transparent; border-radius: 18px; border: " + ring
        )
        layout.addWidget(photo)'''

new_photo = '''        photo = QLabel()
        photo.setFixedSize(36, 36)
        source = None
        if photo_path is not None:
            pp = Path(photo_path)
            if pp.exists():
                source = QPixmap(str(pp))
        ring = "#ffd75e" if premium else "#232f4b"
        if source is not None and not source.isNull():
            pix = self._avatar_pixmap(source, 36, ring)
        else:
            pix = self._initials_pixmap(ring)
        photo.setPixmap(pix)
        photo.setStyleSheet("background: transparent;")
        layout.addWidget(photo)'''

if old_photo in t:
    t = t.replace(old_photo, new_photo, 1)
    print("1. Foto recortada en circulo con anillo.")
else:
    print("1. AVISO: bloque de foto no encontrado.")

# 2. Metodos de avatar circular + iniciales con anillo
old_initials = '''    def _initials_pixmap(self):
        pix = QPixmap(36, 36)
        pix.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor("#1a2236"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, 36, 36)
        painter.setPen(QColor("#4a7dff"))
        painter.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        painter.drawText(
            QRect(0, 0, 36, 36),
            Qt.AlignmentFlag.AlignCenter,
            self.voice_name[:1].upper(),
        )
        painter.end()
        return pix'''

new_initials = '''    def _avatar_pixmap(self, source: QPixmap, size: int, ring: str) -> QPixmap:
        out = QPixmap(size, size)
        out.fill(Qt.GlobalColor.transparent)
        p = QPainter(out)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        clip = QPainterPath()
        clip.addEllipse(0, 0, size, size)
        p.setClipPath(clip)
        scaled = source.scaled(
            size,
            size,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )
        x = (scaled.width() - size) // 2
        y = (scaled.height() - size) // 2
        p.drawPixmap(0, 0, scaled, x, y, size, size)
        p.setClipping(False)
        p.setPen(QPen(QColor(ring), 2))
        p.drawEllipse(1, 1, size - 2, size - 2)
        p.end()
        return out

    def _initials_pixmap(self, ring: str = "#232f4b") -> QPixmap:
        pix = QPixmap(36, 36)
        pix.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor("#1a2236"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, 36, 36)
        painter.setPen(QColor("#4a7dff"))
        painter.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        painter.drawText(
            QRect(0, 0, 36, 36),
            Qt.AlignmentFlag.AlignCenter,
            self.voice_name[:1].upper(),
        )
        painter.setPen(QPen(QColor(ring), 2))
        painter.drawEllipse(1, 1, 34, 34)
        painter.end()
        return pix'''

if old_initials in t:
    t = t.replace(old_initials, new_initials, 1)
    print("2. _avatar_pixmap agregado + iniciales con anillo.")
else:
    print("2. AVISO: _initials_pixmap no encontrado.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(p.read_text(encoding="utf-8"))
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
