"""Splash screen organico de WillpoVoice.

Se muestra al instante (antes de los imports pesados) y se desvanece
cuando la ventana principal esta lista. Solo depende de PySide6, por lo
que puede importarse antes que torch / pocket_tts / SAPI.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import (QPixmap, QPainter, QColor, QFont, QLinearGradient,
                           QPainterPath)
from PySide6.QtWidgets import QApplication, QWidget


class WillpoSplash(QWidget):
    """Pantalla de carga con imagen de marca, estado y barra de progreso."""

    def __init__(self, image_path: str, subtitle: str = ""):
        super().__init__(
            None,
            Qt.WindowType.SplashScreen
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)

        pm = QPixmap(str(image_path))
        if pm.isNull():
            pm = QPixmap(600, 360)
            pm.fill(QColor("#0a0e1a"))
        if pm.width() > 680:
            pm = pm.scaledToWidth(680, Qt.TransformationMode.SmoothTransformation)
        self._pm = pm
        self.setFixedSize(pm.size())

        self._subtitle = subtitle
        self._status = "Iniciando WillpoVoice..."
        self._progress = 0.0
        self._sweep = 0.0

        scr = QApplication.primaryScreen()
        geo = scr.availableGeometry() if scr else self.screen().availableGeometry()
        self.move(geo.center() - self.rect().center())

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(40)
        self._anim = None

    def set_status(self, text: str, progress: float | None = None):
        """Actualiza el mensaje y (opcional) el progreso 0..1; repinta al instante."""
        self._status = str(text)
        if progress is not None:
            self._progress = max(0.0, min(1.0, float(progress)))
        self.update()
        QApplication.processEvents()

    def _tick(self):
        self._sweep = (self._sweep + 0.02) % 1.0
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        clip = QPainterPath()
        clip.addRoundedRect(0, 0, w, h, 18, 18)
        p.setClipPath(clip)
        p.drawPixmap(0, 0, self._pm)

        grad = QLinearGradient(0, h - 96, 0, h)
        grad.setColorAt(0.0, QColor(10, 14, 26, 0))
        grad.setColorAt(1.0, QColor(10, 14, 26, 225))
        p.fillRect(0, h - 96, w, 96, grad)

        p.setPen(QColor("#e6edf3"))
        p.setFont(QFont("Segoe UI", 10))
        p.drawText(22, h - 44, self._status)
        if self._subtitle:
            p.setPen(QColor("#8b93b0"))
            p.setFont(QFont("Segoe UI", 8))
            p.drawText(22, h - 62, self._subtitle)

        bar_y, bar_w = h - 24, w - 44
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(255, 255, 255, 32))
        p.drawRoundedRect(22, bar_y, bar_w, 5, 2.5, 2.5)
        p.setBrush(QColor("#7c5cff"))
        if self._progress > 0:
            p.drawRoundedRect(22, bar_y, max(6, int(bar_w * self._progress)), 5, 2.5, 2.5)
        else:
            seg = int(bar_w * 0.25)
            x = 22 + int((bar_w - seg) * self._sweep)
            p.drawRoundedRect(x, bar_y, seg, 5, 2.5, 2.5)
        p.end()

    def finish(self, window):
        """Muestra la ventana principal y desvanece el splash (350 ms)."""
        self._timer.stop()
        window.show()
        window.raise_()
        window.activateWindow()
        self._anim = QPropertyAnimation(self, b"windowOpacity")
        self._anim.setDuration(350)
        self._anim.setStartValue(1.0)
        self._anim.setEndValue(0.0)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.finished.connect(self.close)
        self._anim.start()
