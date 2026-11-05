from __future__ import annotations

import logging
import sys
from pathlib import Path
from urllib.parse import quote

from PySide6.QtCore import Qt, QThread, QTimer, QUrl, Signal, QSize, QRect, QPoint
from PySide6.QtGui import (
    QColor, QDesktopServices, QIcon, QFont, QPainter, QPainterPath, QPen,
    QPixmap, QPolygon,
)
from PySide6.QtWidgets import (
    QDialog,
    QAbstractButton,
    QComboBox, QFileDialog, QFrame, QGraphicsDropShadowEffect, QGridLayout,
    QHBoxLayout, QLabel, QLineEdit, QListWidget, QMainWindow, QMenu,
    QMessageBox, QPlainTextEdit, QProgressDialog, QPushButton,
    QScrollArea, QSizePolicy, QSlider, QSpinBox, QStackedWidget,
    QVBoxLayout, QWidget,
)

from PySide6.QtWidgets import QSpacerItem
from app.config import load_settings, save_settings
from app.version import APP_VERSION
from core import file_reader, license_manager
from core import trial_tokens
from core.audio_exporter import AudioExporter
from core.tts_engine import TTSEngine
from ui.clone_voice_page import CloneVoicePage
from ui.main_window import (ExportWorker, LicenseDialog,
    TrialActivatedDialog)

BG = "#0b0f1a"
SIDE_BG = "#0d1220"
CARD = "#141b30"
CARD2 = "#1a2138"
BORDER = "#232f4b"
TEXT = "#eef2ff"
MUTED = "#8b93b0"
TEAL = "#2dd4bf"
BLUE = "#3b82f6"
PURPLE = "#8b5cf6"
MAGENTA = "#c026d3"
RED = "#ef4444"

# ---- tema claro: traduccion de paleta en setStyleSheet ----
def _light_theme_enabled():
    try:
        return str(load_settings().get("theme", "Oscuro")) == "Claro"
    except Exception:
        return False

LIGHT_MODE = False

if LIGHT_MODE:
    BG = "#f3f5fa"
    SIDE_BG = "#e9edf5"
    CARD = "#ffffff"
    CARD2 = "#f2f4fa"
    BORDER = "#d5dcea"
    TEXT = "#17203a"
    MUTED = "#5b6478"
    _LIGHT_HEX = {
        "#ffffff": "#17203a", "#e6edf3": "#17203a", "#eef2ff": "#17203a",
        "#8b949e": "#5b6478", "#8b93b0": "#5b6478", "#9aa4b2": "#5b6478",
        "#c9d1d9": "#3c465e", "#c4b5fd": "#6d28d9",
        "#0b0f1a": "#f3f5fa", "#0d1220": "#eef1f8", "#10141f": "#ffffff",
        "#141b30": "#ffffff", "#1a2138": "#eef1f8", "#232f4b": "#d5dcea",
        "#262d3a": "#d5dcea",
        "rgba(10,14,24,214)": "rgba(255,255,255,235)",
    }
    from PySide6.QtWidgets import QWidget as _WBase
    _orig_sss = _WBase.setStyleSheet

    def _sss_light(self, qss):
        try:
            for _k, _v in _LIGHT_HEX.items():
                qss = qss.replace(_k, _v)
        except Exception:
            pass
        _orig_sss(self, qss)

    _WBase.setStyleSheet = _sss_light

PREMIUM_PHOTOS = {
    "andrew": "ms_andrew.png", "ava": "ms_ava.png", "brian": "ms_brian.png",
    "emma": "ms_emma.png", "florian": "ms_florian.png",
    "giuseppe": "ms_giuseppe.png", "hyunsu": "ms_hyunsu.png",
    "remy": "ms_remy.png", "seraphina": "ms_seraphina.png",
    "william": "ms_william.png", "vivienne": "ms_vivienne.png",
    "thalita": "ms_thalita.png", "elvira": "ms_elvira.png",
    "alonso": "ms_alonso.png", "dalia": "ms_dalia.png",
    "alfredo": "foto_narrador.png",
}


def make_icon(kind, color, size=20):
    try:
        _base = Path(getattr(sys, "_MEIPASS",
                             Path(__file__).resolve().parents[1]))
        _svg = _base / "assets" / "icons" / "svg" / f"{kind}.svg"
        if _svg.exists():
            from PySide6.QtSvg import QSvgRenderer
            from PySide6.QtCore import QByteArray
            _data = _svg.read_text(encoding="utf-8")
            _data = _data.replace("currentColor", color)
            if kind == "heart_fill":
                _data = _data.replace('fill="none"',
                                      f'fill="{color}"')
            _r = QSvgRenderer(QByteArray(_data.encode("utf-8")))
            if _r.isValid():
                pix = QPixmap(size, size)
                pix.fill(Qt.GlobalColor.transparent)
                _p = QPainter(pix)
                _r.render(_p)
                _p.end()
                return pix
    except Exception:
        pass
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(QColor(color), max(1.6, size * 0.11))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    s = size

    def pt(fx, fy):
        return QPoint(int(fx * s), int(fy * s))

    def poly(*coords):
        return QPolygon([pt(x, y) for x, y in coords])

    if kind == "menu":
        for y in (0.3, 0.5, 0.7):
            p.drawLine(pt(0.2, y), pt(0.8, y))
    elif kind == "home":
        p.drawPolyline(poly((0.5, 0.15), (0.15, 0.48), (0.15, 0.85),
                            (0.85, 0.85), (0.85, 0.48), (0.5, 0.15)))
    elif kind == "history":
        p.drawEllipse(int(s * 0.15), int(s * 0.15), int(s * 0.7), int(s * 0.7))
        p.drawLine(pt(0.5, 0.5), pt(0.5, 0.3))
        p.drawLine(pt(0.5, 0.5), pt(0.66, 0.58))
    elif kind == "mic":
        p.drawRoundedRect(int(s * 0.38), int(s * 0.12), int(s * 0.24), int(s * 0.42), 4, 4)
        p.drawArc(int(s * 0.24), int(s * 0.28), int(s * 0.52), int(s * 0.52), 180 * 16, 180 * 16)
        p.drawLine(pt(0.5, 0.8), pt(0.5, 0.9))
    elif kind in ("heart", "heart_fill"):
        path = QPainterPath()
        path.moveTo(s * 0.5, s * 0.85)
        path.cubicTo(s * 0.05, s * 0.5, s * 0.15, s * 0.1, s * 0.5, s * 0.3)
        path.cubicTo(s * 0.85, s * 0.1, s * 0.95, s * 0.5, s * 0.5, s * 0.85)
        if kind == "heart_fill":
            p.setBrush(QColor(color))
        p.drawPath(path)
    elif kind == "folder":
        p.drawPolyline(poly((0.12, 0.3), (0.12, 0.22), (0.42, 0.22), (0.5, 0.3)))
        p.drawRoundedRect(int(s * 0.12), int(s * 0.3), int(s * 0.76), int(s * 0.52), 3, 3)
    elif kind == "gear":
        import math
        p.drawEllipse(int(s * 0.32), int(s * 0.32), int(s * 0.36), int(s * 0.36))
        for i in range(8):
            a = math.radians(i * 45)
            p.drawLine(pt(0.5 + 0.32 * math.cos(a), 0.5 + 0.32 * math.sin(a)),
                       pt(0.5 + 0.45 * math.cos(a), 0.5 + 0.45 * math.sin(a)))
    elif kind == "help":
        p.drawEllipse(int(s * 0.15), int(s * 0.15), int(s * 0.7), int(s * 0.7))
        p.setFont(QFont("Segoe UI", max(8, int(s * 0.5)), QFont.Weight.Bold))
        p.drawText(QRect(0, 0, s, s), Qt.AlignmentFlag.AlignCenter, "?")
    elif kind == "headset":
        p.drawArc(int(s * 0.18), int(s * 0.15), int(s * 0.64), int(s * 0.64), 0, 180 * 16)
        p.drawRoundedRect(int(s * 0.14), int(s * 0.5), int(s * 0.14), int(s * 0.28), 3, 3)
        p.drawRoundedRect(int(s * 0.72), int(s * 0.5), int(s * 0.14), int(s * 0.28), 3, 3)
    elif kind == "play":
        p.setBrush(QColor(color))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPolygon(poly((0.32, 0.2), (0.32, 0.8), (0.8, 0.5)))
    elif kind == "stop":
        p.setBrush(QColor(color))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(int(s * 0.3), int(s * 0.3), int(s * 0.4), int(s * 0.4), 3, 3)
    elif kind == "download":
        p.drawLine(pt(0.5, 0.18), pt(0.5, 0.6))
        p.drawPolyline(poly((0.32, 0.44), (0.5, 0.62), (0.68, 0.44)))
        p.drawLine(pt(0.25, 0.8), pt(0.75, 0.8))
    elif kind == "copy":
        p.drawRoundedRect(int(s * 0.32), int(s * 0.32), int(s * 0.48), int(s * 0.52), 3, 3)
        p.drawRoundedRect(int(s * 0.2), int(s * 0.16), int(s * 0.48), int(s * 0.52), 3, 3)
    elif kind == "paste":
        p.drawRoundedRect(int(s * 0.24), int(s * 0.2), int(s * 0.52), int(s * 0.65), 3, 3)
        p.drawRect(int(s * 0.4), int(s * 0.12), int(s * 0.2), int(s * 0.14))
    elif kind == "trash":
        p.drawLine(pt(0.25, 0.28), pt(0.75, 0.28))
        p.drawLine(pt(0.42, 0.18), pt(0.58, 0.18))
        p.drawRoundedRect(int(s * 0.3), int(s * 0.28), int(s * 0.4), int(s * 0.55), 3, 3)
    elif kind == "moon":
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(color))
        p.drawEllipse(int(s * 0.18), int(s * 0.18), int(s * 0.64), int(s * 0.64))
        p.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        p.drawEllipse(int(s * 0.38), int(s * 0.1), int(s * 0.55), int(s * 0.55))
    elif kind == "globe":
        p.drawEllipse(int(s * 0.15), int(s * 0.15), int(s * 0.7), int(s * 0.7))
        p.drawLine(pt(0.15, 0.5), pt(0.85, 0.5))
        p.drawEllipse(int(s * 0.35), int(s * 0.15), int(s * 0.3), int(s * 0.7))
    elif kind == "wave":
        p.drawPolyline(poly((0.12, 0.5), (0.28, 0.5), (0.38, 0.22),
                            (0.5, 0.78), (0.62, 0.35), (0.72, 0.5), (0.88, 0.5)))
    elif kind == "filter":
        p.drawLine(pt(0.2, 0.3), pt(0.8, 0.3))
        p.drawLine(pt(0.3, 0.5), pt(0.7, 0.5))
        p.drawLine(pt(0.4, 0.7), pt(0.6, 0.7))
    elif kind == "volume":
        p.setBrush(QColor(color))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPolygon(poly((0.18, 0.4), (0.34, 0.4), (0.5, 0.24),
                           (0.5, 0.76), (0.34, 0.6), (0.18, 0.6)))
        p.setPen(pen)
        p.drawArc(int(s * 0.5), int(s * 0.3), int(s * 0.4), int(s * 0.4), -60 * 16, 120 * 16)
    elif kind == "text":
        p.drawLine(pt(0.3, 0.25), pt(0.7, 0.25))
        p.drawLine(pt(0.5, 0.25), pt(0.5, 0.78))
        p.drawLine(pt(0.38, 0.78), pt(0.62, 0.78))
    elif kind == "doc":
        p.drawRoundedRect(int(s * 0.28), int(s * 0.15), int(s * 0.44), int(s * 0.7), 3, 3)
        p.drawLine(pt(0.38, 0.35), pt(0.62, 0.35))
        p.drawLine(pt(0.38, 0.5), pt(0.62, 0.5))
        p.drawLine(pt(0.38, 0.65), pt(0.55, 0.65))
    elif kind == "search":
        p.drawEllipse(int(s * 0.2), int(s * 0.2), int(s * 0.42), int(s * 0.42))
        p.drawLine(pt(0.52, 0.52), pt(0.8, 0.8))
    elif kind == "pause":
        p.setBrush(QColor(color))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(int(s * 0.3), int(s * 0.25), int(s * 0.14), int(s * 0.5), 2, 2)
        p.drawRoundedRect(int(s * 0.56), int(s * 0.25), int(s * 0.14), int(s * 0.5), 2, 2)
    elif kind == "robot":
        # Cabeza de robot con antena
        p.setBrush(QColor(color))
        p.setPen(Qt.PenStyle.NoPen)
        # Antena
        p.drawLine(pt(0.5, 0.1), pt(0.5, 0.25))
        p.drawEllipse(int(s * 0.42), int(s * 0.05), int(s * 0.16), int(s * 0.16))
        # Cabeza
        p.drawRoundedRect(int(s * 0.25), int(s * 0.25), int(s * 0.5), int(s * 0.45), 4, 4)
        # Ojos
        p.setBrush(QColor("#ffffff"))
        p.drawEllipse(int(s * 0.32), int(s * 0.38), int(s * 0.1), int(s * 0.1))
        p.drawEllipse(int(s * 0.58), int(s * 0.38), int(s * 0.1), int(s * 0.1))
        # Boca
        p.setPen(QPen(QColor("#ffffff"), 1.5))
        p.drawLine(pt(0.4, 0.6), pt(0.6, 0.6))
    elif kind == "robot":
        # Cabeza de perfil con circuitos (IA)
        p.setPen(QPen(QColor(color), max(1.4, size * 0.10)))
        p.setBrush(Qt.BrushStyle.NoBrush)
        # Perfil de cabeza (silueta)
        head = QPainterPath()
        head.moveTo(pt(0.55, 0.15))
        head.cubicTo(pt(0.75, 0.15).x(), pt(0.75, 0.15).y(),
                     pt(0.85, 0.25).x(), pt(0.85, 0.25).y(),
                     pt(0.82, 0.40).x(), pt(0.82, 0.40).y())
        head.cubicTo(pt(0.80, 0.50).x(), pt(0.80, 0.50).y(),
                     pt(0.88, 0.55).x(), pt(0.88, 0.55).y(),
                     pt(0.82, 0.62).x(), pt(0.82, 0.62).y())
        head.cubicTo(pt(0.78, 0.66).x(), pt(0.78, 0.66).y(),
                     pt(0.78, 0.70).x(), pt(0.78, 0.70).y(),
                     pt(0.72, 0.72).x(), pt(0.72, 0.72).y())
        head.cubicTo(pt(0.65, 0.74).x(), pt(0.65, 0.74).y(),
                     pt(0.60, 0.80).x(), pt(0.60, 0.80).y(),
                     pt(0.55, 0.85).x(), pt(0.55, 0.85).y())
        head.lineTo(pt(0.30, 0.85))
        head.cubicTo(pt(0.20, 0.75).x(), pt(0.20, 0.75).y(),
                     pt(0.15, 0.55).x(), pt(0.15, 0.55).y(),
                     pt(0.20, 0.35).x(), pt(0.20, 0.35).y())
        head.cubicTo(pt(0.25, 0.20).x(), pt(0.25, 0.20).y(),
                     pt(0.40, 0.15).x(), pt(0.40, 0.15).y(),
                     pt(0.55, 0.15).x(), pt(0.55, 0.15).y())
        p.drawPath(head)
        # Circuitos internos (nodos y líneas)
        p.setBrush(QColor(color))
        nodes = [(0.40, 0.35), (0.55, 0.30), (0.70, 0.38),
                 (0.45, 0.55), (0.60, 0.50), (0.72, 0.55),
                 (0.35, 0.70), (0.50, 0.68), (0.62, 0.72)]
        r = max(1.2, size * 0.07)
        for nx, ny in nodes:
            p.drawEllipse(int(nx * s - r), int(ny * s - r), int(r*2), int(r*2))
        # Líneas de circuito entre nodos
        p.setPen(QPen(QColor(color), max(1.0, size * 0.07)))
        connections = [((0.40, 0.35), (0.55, 0.30)),
                       ((0.55, 0.30), (0.70, 0.38)),
                       ((0.40, 0.35), (0.45, 0.55)),
                       ((0.55, 0.30), (0.60, 0.50)),
                       ((0.70, 0.38), (0.72, 0.55)),
                       ((0.45, 0.55), (0.60, 0.50)),
                       ((0.60, 0.50), (0.72, 0.55)),
                       ((0.45, 0.55), (0.35, 0.70)),
                       ((0.45, 0.55), (0.50, 0.68)),
                       ((0.60, 0.50), (0.62, 0.72)),
                       ((0.35, 0.70), (0.50, 0.68)),
                       ((0.50, 0.68), (0.62, 0.72))]
        for (x1, y1), (x2, y2) in connections:
            p.drawLine(pt(x1, y1), pt(x2, y2))
    else:
        p.setBrush(QColor(color))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(int(s * 0.3), int(s * 0.3), int(s * 0.4), int(s * 0.4))
    p.end()
    return pix


class IconLabel(QLabel):
    def __init__(self, glyph, size=16, color=MUTED, parent=None):
        super().__init__(parent)
        self.setPixmap(make_icon(glyph, color, size + 4))
        self.setStyleSheet("background: transparent;")


class NavButton(QFrame):
    clicked = Signal()

    def __init__(self, glyph, text, parent=None):
        super().__init__(parent)
        self.setFixedHeight(44)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 0, 12, 0)
        lay.setSpacing(12)
        self.icon = IconLabel(glyph, 15, MUTED)
        self.icon.setFixedSize(20, 20)
        self._glyph = glyph
        self.label = QLabel(text)
        self.label.setStyleSheet(
            f"color: {MUTED}; font-size: 13px; background: transparent; border: none;"
        )
        lay.addWidget(self.icon)
        lay.addWidget(self.label)
        self._spacer = QSpacerItem(
            0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        lay.addSpacerItem(self._spacer)
        self.set_active(False)

    def mouseReleaseEvent(self, event):
        self.clicked.emit()

    def set_collapsed(self, collapsed):
        self.label.setVisible(not collapsed)
        lay = self.layout()
        if collapsed:
            lay.setContentsMargins(0, 0, 0, 0)
            lay.setSpacing(0)
            self._spacer.changeSize(
                0, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
            self.icon.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            self.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            lay.setContentsMargins(14, 0, 12, 0)
            lay.setSpacing(12)
            self._spacer.changeSize(
                0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
            self.icon.setFixedSize(20, 20)
            self.icon.setAlignment(Qt.AlignmentFlag.AlignLeft)
        lay.invalidate()


    def set_active(self, active):
        if active:
            self.setStyleSheet(
                "NavButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                " stop:0 rgba(45,212,191,26), stop:1 rgba(139,92,246,26));"
                f" border: 1px solid {BORDER}; border-radius: 10px; }}"
            )
            self.icon.setPixmap(make_icon(self._glyph, TEAL, 19))
            self.label.setStyleSheet(
                f"color: {TEXT}; font-size: 13px; font-weight: 600;"
                " background: transparent; border: none;"
            )
        else:
            self.setStyleSheet(
                "NavButton { background: transparent; border: 1px solid"
                f" transparent; border-radius: 10px; }} NavButton:hover {{ background: {CARD}; }}"
            )
            self.icon.setPixmap(make_icon(self._glyph, MUTED, 19))
            self.label.setStyleSheet(
                f"color: {MUTED}; font-size: 13px; background: transparent; border: none;"
            )



class SquareButton(QFrame):
    clicked = Signal()

    def __init__(self, glyph, tooltip="", parent=None):
        super().__init__(parent)
        self.setFixedSize(46, 46)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(tooltip)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        self.icon = IconLabel(glyph, 15, TEXT)
        self.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.icon)
        self.setStyleSheet(
            f"SquareButton {{ background: {CARD}; border: 1px solid {BORDER};"
            f" border-radius: 10px; }} SquareButton:hover {{ background: {CARD2}; }}"
        )

    def mouseReleaseEvent(self, event):
        self.clicked.emit()


class ActionButton(QFrame):
    clicked = Signal()

    def __init__(self, glyph, text, c1, c2, parent=None):
        super().__init__(parent)
        self.setFixedHeight(46)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(18, 0, 18, 0)
        lay.setSpacing(10)
        self.icon = IconLabel(glyph, 15, "#ffffff")
        eff = QGraphicsDropShadowEffect(self.icon)
        eff.setBlurRadius(8)
        eff.setOffset(0, 0)
        eff.setColor(QColor("#ffffff"))
        self.icon.setGraphicsEffect(eff)
        self.label = QLabel(text)
        self.label.setStyleSheet(
            "color: white; font-size: 13px; font-weight: 600;"
            " background: transparent;"
        )
        lay.addStretch()
        lay.addWidget(self.icon)
        lay.addWidget(self.label)
        lay.addStretch()
        self.setStyleSheet(
            "ActionButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f" stop:0 {c1}, stop:1 {c2});"
            " border: 1px solid rgba(255,255,255,40); border-radius: 10px; }"
        )

    def mouseReleaseEvent(self, event):
        self.clicked.emit()



class TabButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.set_active(False)

    def set_active(self, active):
        if active:
            self.setStyleSheet(
                f"QPushButton {{ background: transparent; color: {TEXT};"
                " font-size: 13px; font-weight: 600; border: none;"
                f" border-bottom: 2px solid {PURPLE}; padding: 6px 8px; }}"
            )
        else:
            self.setStyleSheet(
                f"QPushButton {{ background: transparent; color: {MUTED};"
                " font-size: 13px; border: none; border-bottom: 2px solid"
                f" transparent; padding: 8px 14px; }} QPushButton:hover {{ color: {TEXT}; }}"
            )


class StatsCard(QFrame):
    def __init__(self, glyph, color, title, value, parent=None):
        super().__init__(parent)
        self.setFixedHeight(88)
        self.setObjectName("statsCard")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(18, 0, 16, 0)
        lay.setSpacing(14)
        self.icon = IconLabel(glyph, 26, color)
        self.icon.setFixedSize(36, 36)
        eff = QGraphicsDropShadowEffect(self.icon)
        eff.setBlurRadius(14)
        eff.setOffset(0, 0)
        eff.setColor(QColor(color))
        self.icon.setGraphicsEffect(eff)
        texts = QVBoxLayout()
        texts.setSpacing(2)
        texts.setContentsMargins(0, 12, 0, 0)
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
        texts_widget = QWidget()
        texts_widget.setLayout(texts)
        texts_widget.setStyleSheet("background: transparent;")
        lay.addWidget(self.icon, 0, Qt.AlignmentFlag.AlignVCenter)
        lay.addWidget(texts_widget, 1, Qt.AlignmentFlag.AlignTop)
        self.setStyleSheet(
            f"QFrame#statsCard {{ background: {CARD}; border: 1px solid"
            f" {BORDER}; border-radius: 14px; }}"
        )



class PreviewPhoto(QLabel):
    play_clicked = Signal()
    hover_changed = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def enterEvent(self, event):
        self.hover_changed.emit(True)

    def leaveEvent(self, event):
        self.hover_changed.emit(False)

    def mouseReleaseEvent(self, event):
        self.play_clicked.emit()


class _HistPage(QWidget):
    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        fn = getattr(self.window(), "_layout_hist_bg", None)
        if callable(fn):
            fn()


def _layout_hist_bg(self):
    pg = getattr(self, "_hist_page", None)
    if pg is None:
        return
    w, h = pg.width(), pg.height()
    if w <= 0 or h <= 0:
        return
    if not getattr(self, "_hist_bg_pix", None):
        import sys
        base = Path(getattr(sys, "_MEIPASS",
                            Path(__file__).resolve().parents[1]))
        sp = base / "assets" / "icons" / ("chat_bg_ligth.png" if LIGHT_MODE else "chat_bg.png")
        if not sp.exists():
            self._hist_bg_pix = None
            return
        self._hist_bg_pix = QPixmap(str(sp))
    if self._hist_bg_pix:
        self._hist_bg.setGeometry(0, 0, w, h)
        self._hist_bg.setPixmap(self._hist_bg_pix)
        self._hist_bg.setScaledContents(True)


class _VocPage(QWidget):
    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        fn = getattr(self.window(), "_layout_voc_bg", None)
        if callable(fn):
            fn()


def _layout_voc_bg(self):
    pg = getattr(self, "_voc_page", None)
    if pg is None:
        return
    w, h = pg.width(), pg.height()
    if w <= 0 or h <= 0:
        return
    if not getattr(self, "_voc_bg_pix", None):
        import sys
        base = Path(getattr(sys, "_MEIPASS",
                            Path(__file__).resolve().parents[1]))
        sp = base / "assets" / "icons" / ("chat_bg_ligth.png" if LIGHT_MODE else "chat_bg.png")
        if not sp.exists():
            self._voc_bg_pix = None
            return
        self._voc_bg_pix = QPixmap(str(sp))
    if self._voc_bg_pix:
        self._voc_bg.setGeometry(0, 0, w, h)
        self._voc_bg.setPixmap(self._voc_bg_pix)
        self._voc_bg.setScaledContents(True)


class _FavPage(QWidget):
    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        fn = getattr(self.window(), "_layout_fav_bg", None)
        if callable(fn):
            fn()


def _layout_fav_bg(self):
    pg = getattr(self, "_fav_page", None)
    if pg is None:
        return
    w, h = pg.width(), pg.height()
    if w <= 0 or h <= 0:
        return
    if not getattr(self, "_fav_bg_pix", None):
        import sys
        base = Path(getattr(sys, "_MEIPASS",
                            Path(__file__).resolve().parents[1]))
        sp = base / "assets" / "icons" / ("chat_bg_ligth.png" if LIGHT_MODE else "chat_bg.png")
        if not sp.exists():
            self._fav_bg_pix = None
            return
        self._fav_bg_pix = QPixmap(str(sp))
    if self._fav_bg_pix:
        self._fav_bg.setGeometry(0, 0, w, h)
        self._fav_bg.setPixmap(self._fav_bg_pix)
        self._fav_bg.setScaledContents(True)


def _etiqueta_voz(window, name, premium):
    """Subtitulo de tarjeta: devuelve (texto, color).
    Voces con huella .safetensors (clonadas/realistas) -> rosa Favoritas.
    Premium SAPI -> dorado. No premium -> morado."""
    clon = False
    for attr in ("_cloned_set", "_cloned_names", "_cloned_voices"):
        s = getattr(window, attr, None)
        if s and name in s:
            clon = True
            break
    if not clon:
        try:
            from pathlib import Path as _P
            from core.pocket_cloner import cloner_instance
            clon = (_P(cloner_instance.voices_dir()) /
                    (name + ".safetensors")).exists()
        except Exception:
            clon = False
    if clon:
        return "WillpoVoice Realista", "#ff4fd8"
    return (("WillpoVoice Premium" if premium else "WillpoVoice"),
            ("#f5b301" if premium else "#a855f7"))


class FavCard(QFrame):
    fav_removed = Signal(str)
    preview_requested = Signal(str)

    def __init__(self, window, name, premium, parent=None):
        super().__init__(parent)
        self._name = name
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(150)
        self._set_border(False)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(1, 1, 1, 1)
        inner = QFrame()
        inner.setObjectName("fvinner")
        inner.setStyleSheet(
            "#fvinner { background: rgba(10,14,24,214); border-radius: 15px; }")
        outer.addWidget(inner)
        h = QHBoxLayout(inner)
        h.setContentsMargins(26, 0, 26, 0)
        h.setSpacing(22)
        av = QWidget()
        av.setFixedSize(112, 112)
        av.setStyleSheet("background: transparent;")
        ring = QLabel(av)
        ring.setGeometry(0, 0, 112, 112)
        ring.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            " stop:0 #3b82f6, stop:1 #a855f7); border-radius: 56px;")
        photo = QLabel(av)
        photo.setGeometry(4, 4, 104, 104)
        low = name.lower()
        fname = next((f for k, f in PREMIUM_PHOTOS.items() if k in low), None)
        if fname is None:
            first = name.replace("Microsoft ", "").split(" ")[0].strip().lower()
            fname = "face_f.png" if first.endswith("a") else "face_m.png"
        size = 104
        ckey = (fname, size)
        out = _FACE_CACHE.get(ckey)
        if out is None:
            out = QPixmap(size, size)
            out.fill(Qt.GlobalColor.transparent)
            fpath = window._resource_path(Path("assets") / "icons" / fname)
            if fpath.exists():
                src = QPixmap(str(fpath))
                if not src.isNull():
                    pnt = QPainter(out)
                    pnt.setRenderHint(QPainter.RenderHint.Antialiasing)
                    clip = QPainterPath()
                    clip.addEllipse(0, 0, size, size)
                    pnt.setClipPath(clip)
                    sc = src.scaled(size, size,
                                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                    Qt.TransformationMode.SmoothTransformation)
                    pnt.drawPixmap(0, 0, sc, (sc.width() - size) // 2,
                                   (sc.height() - size) // 2, size, size)
                    pnt.end()
            _FACE_CACHE[ckey] = out
        photo.setPixmap(out)
        photo.setStyleSheet("background: transparent;")
        badge = QLabel(av)
        badge.setGeometry(82, 0, 30, 30)
        badge.setPixmap(make_icon("sparkles", "#ffffff", 14))
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            " stop:0 #7c5cff, stop:1 #3b82f6); border-radius: 15px;")
        h.addWidget(av)
        info = QVBoxLayout()
        info.setSpacing(10)
        nm = QLabel(window._display_voice_name(name))
        nm.setStyleSheet(
            "color: #ffffff; font-size: 20px; font-weight: 700;")
        info.addWidget(nm)
        if premium:
            prow = QHBoxLayout()
            prow.setSpacing(8)
            cr = QLabel()
            cr.setPixmap(make_icon("crown", "#f5b301", 15))
            prow.addWidget(cr)
            _etx, _ecol = _etiqueta_voz(window, name, premium)
            plbl = QLabel(_etx)
            plbl.setStyleSheet(
                "color: " + _ecol + "; font-size: 13px; font-weight: 600;")
            prow.addWidget(plbl)
            prow.addStretch(1)
            info.addLayout(prow)
        chips = QHBoxLayout()
        chips.setSpacing(10)
        for tag in window._voice_subtitle(name, premium).split("\u00b7"):
            ch = QLabel(tag.strip())
            ch.setStyleSheet(
                "color: #9aa4b2; font-size: 11.5px; border: 1px solid #2a3140;"
                " border-radius: 14px; padding: 5px 14px;")
            chips.addWidget(ch)
        chips.addStretch(1)
        info.addLayout(chips)
        info.addStretch(1)
        h.addLayout(info, 1)
        right = QVBoxLayout()
        right.setSpacing(14)
        trow = QHBoxLayout()
        trow.setSpacing(14)
        if premium:
            pro = QLabel("Pro")
            pro.setStyleSheet(
                "background: #7c5cff; color: white; border-radius: 9px;"
                " font-size: 10px; font-weight: 700; padding: 4px 12px;")
            trow.addWidget(pro)
        hb = QPushButton()
        hb.setFixedSize(30, 30)
        hb.setIcon(QIcon(make_icon("heart_fill", "#ef4444", 20)))
        hb.setIconSize(QSize(20, 20))
        hb.setStyleSheet("background: transparent; border: none;")
        hb.setToolTip("Quitar de favoritos")
        hb.setCursor(Qt.CursorShape.PointingHandCursor)
        hb.clicked.connect(lambda: self.fav_removed.emit(self._name))
        trow.addWidget(hb)
        trow.addStretch(1)
        right.addLayout(trow)
        pb = QPushButton()
        pb.setFixedSize(56, 46)
        pb.setIcon(QIcon(make_icon("play", "#c9d1d9", 16)))
        pb.setIconSize(QSize(16, 16))
        pb.setStyleSheet(
            "QPushButton { background: rgba(255,255,255,6);"
            " border: 1px solid #262d3a; border-radius: 12px; }"
            " QPushButton:hover { background: rgba(255,255,255,14); }")
        pb.setCursor(Qt.CursorShape.PointingHandCursor)
        pb.clicked.connect(lambda: self.preview_requested.emit(self._name))
        right.addWidget(pb)
        right.addStretch(1)
        h.addLayout(right)

    def _set_border(self, hov):
        if hov:
            bg = "qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #3b82f6, stop:1 #a855f7)"
        else:
            bg = "rgba(148,163,255,26)"
        self.setStyleSheet(
            "FavCard { background: " + bg + "; border-radius: 16px; }")

    def enterEvent(self, ev):
        self._set_border(True)
        super().enterEvent(ev)

    def leaveEvent(self, ev):
        self._set_border(False)
        super().leaveEvent(ev)


def _fav_preview(self, name):
    for attr in ("_toggle_preview", "_on_preview_toggle", "_start_preview"):
        fn = getattr(self, attr, None)
        if callable(fn):
            try:
                fn(name)
                return
            except Exception:
                pass
    try:
        self._select_voice(name)
    except Exception:
        pass




_GEMV2 = "M6 3 L18 3 L22 9 L12 21 L2 9 Z M2 9 L22 9 M9 9 L12 21 M15 9 L12 21"
_FACE_CACHE = {}
ACCENT = "#7c5cff"
_RING_COLORS = ["#a855f7", "#f5b301", "#00d0ff", "#ff4fd8",
                "#3b82f6", "#2dd4bf", "#22d3ee", "#8b5cf6"]


class _ElideLabel(QLabel):
    def __init__(self, txt, parent=None):
        super().__init__(parent)
        self._full = txt
        self.setMinimumWidth(0)
        self.setSizePolicy(QSizePolicy.Policy.Ignored,
                           QSizePolicy.Policy.Preferred)

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        from PySide6.QtGui import QFontMetrics
        m = QFontMetrics(self.font())
        super().setText(m.elidedText(
            self._full, Qt.TextElideMode.ElideRight, self.width()))


class _LangComboButton(QPushButton):
    """Combo de idioma con popup replica del mockup."""
    currentIndexChanged = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = []
        self._idx = 0
        self._block = False
        self._lock_style = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(
            "QPushButton { background: #0d1220; color: #eef2ff;"
            " border: 1px solid #232f4b; border-radius: 10px;"
            " padding: 7px 12px; font-size: 12.5px; text-align: left; }"
            " QPushButton:hover { border: 1px solid #7c5cff; }")
        self._lock_style = True
        self.clicked.connect(self._open_popup)

    # ---- API compat QComboBox ----
    def addItems(self, texts):
        for tx in texts:
            self._items.append([tx, None])

    def count(self):
        return len(self._items)

    def itemText(self, i):
        return self._items[i][0] if 0 <= i < len(self._items) else ""

    def setItemText(self, i, tx):
        if 0 <= i < len(self._items):
            self._items[i][0] = tx
            self._paint()

    def setItemIcon(self, i, icon):
        if 0 <= i < len(self._items):
            self._items[i][1] = icon
            self._paint()

    def currentIndex(self):
        return self._idx

    def setCurrentIndex(self, i):
        if 0 <= i < len(self._items):
            self._idx = i
            self._paint()

    def currentText(self):
        return self.itemText(self._idx)

    def blockSignals(self, b):
        self._block = b
        return super().blockSignals(b)

    def setStyleSheet(self, qss):
        if self._lock_style:
            return
        super().setStyleSheet(qss)

    def _emit_changed(self):
        if not self._block:
            self.currentIndexChanged.emit(self._idx)

    def _paint(self):
        if self._items:
            tx, ic = self._items[self._idx]
            self.setText("  " + tx)
            if ic is not None:
                self.setIcon(ic)
                self.setIconSize(QSize(22, 16))

    # ---- popup ----
    def _row(self, tx, ic, check=False):
        w = QFrame()
        w.setFixedHeight(34)
        w.setCursor(Qt.CursorShape.PointingHandCursor)
        w.setStyleSheet(
            "QFrame { background: transparent; border: none;"
            " border-radius: 8px; }"
            " QFrame:hover { background: #1a2138; }")
        h = QHBoxLayout(w)
        h.setContentsMargins(10, 0, 10, 0)
        h.setSpacing(10)
        if ic is not None:
            il = QLabel()
            il.setPixmap(ic.pixmap(22, 16))
            il.setFixedSize(22, 16)
            il.setStyleSheet("background: transparent;")
            h.addWidget(il)
        lb = QLabel(tx)
        lb.setStyleSheet(
            "color: #eef2ff; font-size: 12.5px; background: transparent;")
        h.addWidget(lb)
        h.addStretch(1)
        if check:
            ck = QLabel()
            ck.setPixmap(make_icon("check", "#2dd4bf", 16))
            ck.setStyleSheet("background: transparent;")
            h.addWidget(ck)
        return w

    def _sep(self):
        s = QLabel()
        s.setFixedHeight(7)
        s.setStyleSheet(
            "background: transparent;"
            " border-top: 1px solid #232f4b; margin: 3px 6px;")
        return s

    def _open_popup(self):
        pop = QFrame(self.window(), Qt.WindowType.Popup)
        pop.setStyleSheet(
            "QFrame { background: #0d1220; border: 1px solid #232f4b;"
            " border-radius: 12px; }")
        v = QVBoxLayout(pop)
        v.setContentsMargins(6, 8, 6, 6)
        v.setSpacing(0)
        hd = QLabel("Idioma actual")
        hd.setStyleSheet(
            "color: #2dd4bf; font-size: 10.5px; padding: 2px 10px 4px;"
            " background: transparent; border: none;")
        v.addWidget(hd)
        ctx, cic = self._items[self._idx]
        rc = self._row(ctx, cic, check=True)
        rc.mouseReleaseEvent = lambda ev: pop.close()
        v.addWidget(rc)
        v.addWidget(self._sep())
        for i in range(min(3, len(self._items))):
            if i == self._idx:
                continue
            tx, ic = self._items[i]
            r = self._row(tx, ic)
            r.mouseReleaseEvent = lambda ev, ii=i: (
                pop.close(), self._choose(ii))
            v.addWidget(r)
        v.addWidget(self._sep())
        lk = QFrame()
        lk.setFixedHeight(34)
        lk.setCursor(Qt.CursorShape.PointingHandCursor)
        lk.setStyleSheet(
            "QFrame { background: transparent; border: none;"
            " border-radius: 8px; }"
            " QFrame:hover { background: #1a2138; }")
        lh = QHBoxLayout(lk)
        lh.setContentsMargins(10, 0, 10, 0)
        lh.setSpacing(8)
        lh.addStretch(1)
        gi = QLabel()
        gi.setPixmap(make_icon("globe", "#a855f7", 15))
        gi.setStyleSheet("background: transparent;")
        lh.addWidget(gi)
        lt = QLabel("Ver todos los idiomas")
        lt.setStyleSheet(
            "color: #a855f7; font-size: 12.5px; background: transparent;")
        lh.addWidget(lt)
        lh.addStretch(1)
        lk.mouseReleaseEvent = lambda ev: (pop.close(), self._open_all())
        v.addWidget(lk)
        pop.setFixedWidth(max(self.width(), 280))
        pop.move(self.mapToGlobal(QPoint(0, self.height() + 4)))
        pop.show()

    def _choose(self, i):
        self._idx = i
        self._paint()
        self._emit_changed()

    def _open_all(self):
        if self.itemText(3).startswith("Ver todos"):
            self._choose(3)
        else:
            w = self.window()
            fn = getattr(w, "_open_lang_dialog", None)
            if callable(fn):
                fn()


class _LangDialog(QDialog):
    def __init__(self, window):
        super().__init__(window)
        self._w = window
        self.setWindowTitle("Seleccionar idioma")
        self.resize(760, 620)
        self.setStyleSheet("QDialog { background: #0b0f1a; }")
        v = QVBoxLayout(self)
        v.setContentsMargins(28, 24, 28, 20)
        v.setSpacing(14)
        hdr = QHBoxLayout()
        hdr.setSpacing(12)
        ic = QLabel()
        ic.setPixmap(make_icon("globe", "#7c5cff", 30))
        hdr.addWidget(ic)
        tt = QVBoxLayout()
        tt.setSpacing(2)
        t1 = QLabel("Seleccionar idioma")
        t1.setStyleSheet("color: #ffffff; font-size: 18px; font-weight: 800;")
        t2 = QLabel("Elige el idioma que prefieras para la aplicaci\u00f3n.")
        t2.setStyleSheet("color: #8b93b0; font-size: 12px;")
        tt.addWidget(t1)
        tt.addWidget(t2)
        hdr.addLayout(tt)
        hdr.addStretch(1)
        x = QPushButton()
        x.setFixedSize(30, 30)
        x.setIcon(QIcon(make_icon("x", "#8b93b0", 14)))
        x.setCursor(Qt.CursorShape.PointingHandCursor)
        x.setStyleSheet("background: transparent; border: none;")
        x.clicked.connect(self.accept)
        hdr.addWidget(x)
        v.addLayout(hdr)
        srow = QHBoxLayout()
        srow.setSpacing(10)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Buscar idioma...")
        self.search.setFixedHeight(42)
        self.search.setStyleSheet(
            "QLineEdit { background: #10141f; border: 1px solid #232f4b;"
            " border-radius: 12px; color: #eef2ff; font-size: 13px;"
            " padding: 0 14px 0 38px; }"
            " QLineEdit:focus { border: 1px solid #7c5cff; }")
        sic = QLabel(self.search)
        sic.setPixmap(make_icon("search", "#8b93b0", 15))
        sic.setGeometry(13, 13, 16, 16)
        sic.setStyleSheet("background: transparent;")
        self.search.textChanged.connect(self._refill)
        srow.addWidget(self.search, 1)
        self.todos_cb = QComboBox()
        self.todos_cb.addItems(["Todos"])
        self.todos_cb.setFixedHeight(42)
        self.todos_cb.setFixedWidth(110)
        self.todos_cb.setStyleSheet(
            "QComboBox { background: #10141f; color: #eef2ff;"
            " border: 1px solid #232f4b; border-radius: 12px;"
            " padding: 0 12px; font-size: 12px; }"
            " QComboBox::drop-down { border: none; }")
        srow.addWidget(self.todos_cb)
        v.addLayout(srow)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet(
            "QScrollArea { background: transparent; border: none; }"
            " QScrollBar:vertical { background: #10141f; width: 8px;"
            " border-radius: 4px; }"
            " QScrollBar::handle:vertical { background: #7c5cff;"
            " border-radius: 4px; min-height: 40px; }"
            " QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical"
            " { height: 0; }")
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.grid = QGridLayout(self.container)
        self.grid.setSpacing(12)
        self.scroll.setWidget(self.container)
        v.addWidget(self.scroll, 1)
        frow = QHBoxLayout()
        fmic = QLabel()
        fmic.setPixmap(make_icon("sparkles", "#a855f7", 14))
        frow.addWidget(fmic)
        fm = QLabel("M\u00e1s idiomas pr\u00f3ximamente")
        fm.setStyleSheet("color: #a855f7; font-size: 12px;")
        frow.addWidget(fm)
        frow.addStretch(1)
        close = QPushButton("Cerrar")
        close.setCursor(Qt.CursorShape.PointingHandCursor)
        close.setStyleSheet(
            "QPushButton { background: #10141f; color: #eef2ff;"
            " border: 1px solid #232f4b; border-radius: 10px;"
            " padding: 9px 22px; font-size: 13px; font-weight: 600; }"
            " QPushButton:hover { border: 1px solid #7c5cff; }")
        close.clicked.connect(self.accept)
        frow.addWidget(close)
        v.addLayout(frow)
        self._refill()

    def _card(self, code, label, flag, sel):
        w = QFrame()
        w.setFixedHeight(50)
        w.setCursor(Qt.CursorShape.PointingHandCursor)
        border = "#7c5cff" if sel else "#232f4b"
        w.setStyleSheet(
            "QFrame { background: #10141f; border: 1.5px solid " + border +
            "; border-radius: 10px; }"
            " QFrame:hover { border: 1.5px solid #7c5cff; }")
        h = QHBoxLayout(w)
        h.setContentsMargins(12, 0, 12, 0)
        h.setSpacing(10)
        fl = QLabel()
        if flag == "world":
            fl.setPixmap(make_icon("globe", "#8b93b0", 18))
        else:
            fl.setPixmap(self._w._flag_pix(flag, 20))
        fl.setFixedSize(24, 20)
        fl.setStyleSheet("background: transparent; border: none;")
        h.addWidget(fl)
        tx = QVBoxLayout()
        tx.setSpacing(1)
        t1 = QLabel(label)
        t1.setStyleSheet(
            "color: #eef2ff; font-size: 13px; font-weight: 600;"
            " background: transparent; border: none;")
        tx.addWidget(t1)
        if sel and code != "all":
            t2 = QLabel("Idioma actual")
            t2.setStyleSheet(
                "color: #8b93b0; font-size: 10px;"
                " background: transparent; border: none;")
            tx.addWidget(t2)
        h.addLayout(tx)
        h.addStretch(1)
        if sel:
            ck = QLabel()
            ck.setPixmap(make_icon("check", "#a855f7", 18))
            ck.setStyleSheet("background: transparent; border: none;")
            h.addWidget(ck)
        w.mouseReleaseEvent = lambda ev, cc=code, ll=label: self._pick(cc, ll)
        return w

    def _refill(self):
        while self.grid.count():
            it = self.grid.takeAt(0)
            if it.widget():
                it.widget().deleteLater()
        q = self.search.text().strip().lower()
        cur = getattr(self._w, "_extra_filter", None)
        items = [("all", "Todos los idiomas", "world")]
        for code, label, flag, keys in LANG_TABLE:
            items.append((code, label, flag))
        row, col = 0, 0
        for code, label, flag in items:
            if q and q not in label.lower():
                continue
            sel = (cur == code) or (
                code == "all" and cur in (None, "premium"))
            self.grid.addWidget(self._card(code, label, flag, sel), row, col)
            col += 1
            if col == 2:
                col = 0
                row += 1

    def _pick(self, code, label):
        w = self._w
        w._extra_filter = None if code == "all" else code
        try:
            w.lang_combo.blockSignals(True)
            if code == "es":
                w.lang_combo.setCurrentIndex(1)
                w._lang_prev = 1
            elif code == "en":
                w.lang_combo.setCurrentIndex(2)
                w._lang_prev = 2
            elif code == "all":
                w.lang_combo.setItemText(3, "Ver todos los idiomas")
                w.lang_combo.setItemIcon(
                    3, QIcon(w._flag_pixmap("world")))
                w.lang_combo.setCurrentIndex(3)
                w._lang_prev = 3
            else:
                flg = next((it[2] for it in LANG_TABLE if it[0] == code),
                           "world")
                w.lang_combo.setItemText(3, label)
                w.lang_combo.setItemIcon(3, QIcon(w._flag_pix(flg)))
                w.lang_combo.setCurrentIndex(3)
                w._lang_prev = 3
        finally:
            w.lang_combo.blockSignals(False)
        if hasattr(w, "_panel_title"):
            w._panel_title.setText(
                "Todos los idiomas" if code == "all" else label)
        w._refill_combo()
        w._rebuild_cards()
        if getattr(w, "_all_built", False):
            w._rebuild_all_page()
        self._refill()


class _Switch(QAbstractButton):
    """Toggle estilo iOS 36x20."""
    def __init__(self, checked=False, accent="#2563eb", parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setChecked(checked)
        self._accent = accent
        self.setFixedSize(44, 22)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def paintEvent(self, ev):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        on = self.isChecked()
        bg = self._accent if on else "#262d3a"
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(bg))
        p.drawRoundedRect(0, 0, 44, 22, 11, 11)
        kx = 22 if on else 2
        p.setBrush(QColor("#ffffff"))
        p.drawEllipse(kx, 2, 18, 18)
        p.end()


class _AdjPage(QWidget):
    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        fn = getattr(self.window(), "_layout_adj_bg", None)
        if callable(fn):
            fn()


def _layout_adj_bg(self):
    pg = getattr(self, "_adj_page", None)
    if pg is None:
        return
    w, h = pg.width(), pg.height()
    if w <= 0 or h <= 0:
        return
    if not getattr(self, "_adj_bg_pix", None):
        import sys
        base = Path(getattr(sys, "_MEIPASS",
                            Path(__file__).resolve().parents[1]))
        sp = base / "assets" / "icons" / ("chat_bg_ligth.png" if LIGHT_MODE else "chat_bg.png")
        if not sp.exists():
            self._adj_bg_pix = None
            return
        self._adj_bg_pix = QPixmap(str(sp))
    if self._adj_bg_pix:
        from PySide6.QtGui import QTransform
        self._adj_bg.setGeometry(0, 0, w, h)
        self._adj_bg.setPixmap(
            self._adj_bg_pix.transformed(QTransform().scale(1, -1)))
        self._adj_bg.setScaledContents(True)


def _adj_row(label_text, widget, bold=False):
    row = QHBoxLayout()
    row.setSpacing(12)
    lb = QLabel(label_text)
    lb.setStyleSheet(
        "color: #c9d1d9; font-size: 13px; font-weight: " +
        ("700" if bold else "500") + ";")
    row.addWidget(lb)
    row.addStretch(1)
    row.addWidget(widget)
    return row


def _adj_combo(options, current, on_change):
    cb = QComboBox()
    cb.addItems(options)
    if current in options:
        cb.setCurrentText(current)
    cb.setStyleSheet(
        "QComboBox { background: #0d1220; color: #e6edf3;"
        " border: 1px solid #262d3a; border-radius: 8px;"
        " padding: 5px 10px; font-size: 12px; }"
        " QComboBox::drop-down { border: none; }"
        " QComboBox QAbstractItemView { background: #0d1220;"
        " color: #e6edf3; selection-background-color: #7c5cff; }")
    from PySide6.QtWidgets import QSizePolicy as _SP
    cb.setSizePolicy(_SP.Policy.Expanding, _SP.Policy.Fixed)
    cb.setMinimumWidth(90)
    cb.currentTextChanged.connect(on_change)
    return cb


def _adj_slider(minv, maxv, value, unit="", on_change=None):
    w = QWidget()
    lay = QHBoxLayout(w)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(10)
    ic_l = QLabel()
    ic_l.setPixmap(make_icon("volume", "#8b949e", 12))
    lay.addWidget(ic_l)
    sl = QSlider(Qt.Orientation.Horizontal)
    sl.setRange(minv, maxv)
    sl.setValue(value)
    sl.setStyleSheet(
        "QSlider::groove:horizontal { background: #262d3a; height: 4px;"
        " border-radius: 2px; }"
        " QSlider::handle:horizontal { background: #22d3ee; width: 16px;"
        " height: 16px; margin: -6px 0; border-radius: 8px; }"
        " QSlider::sub-page:horizontal { background: qlineargradient("
        "x1:0,y1:0,x2:1,y2:0, stop:0 #2563eb, stop:1 #22d3ee);"
        " border-radius: 2px; }")
    sl.valueChanged.connect(lambda v: on_change(v) if on_change else None)
    lay.addWidget(sl, 1)
    ic_r = QLabel()
    ic_r.setPixmap(make_icon("volume", "#c9d1d9", 16))
    lay.addWidget(ic_r)
    return w, sl


class _AdjCard(QFrame):
    def __init__(self, icon_kind, icon_color, title, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            "_AdjCard { background: rgba(13,17,26,214);"
            " border: 1px solid rgba(148,163,255,20); border-radius: 14px; }")
        self.setMinimumWidth(280)
        self.lay = QVBoxLayout(self)
        self.lay.setContentsMargins(18, 16, 18, 16)
        self.lay.setSpacing(14)
        hr = QHBoxLayout()
        hr.setSpacing(10)
        ic = QLabel()
        ic.setPixmap(make_icon(icon_kind, icon_color, 22))
        hr.addWidget(ic)
        tt = QLabel(title)
        tt.setStyleSheet("color: #ffffff; font-size: 15px; font-weight: 700;")
        hr.addWidget(tt)
        hr.addStretch(1)
        self.lay.addLayout(hr)


class _AccentCircle(QWidget):
    """Circulo de color 26px con anillo activo 36px."""
    def __init__(self, color, rainbow=False, parent=None):
        super().__init__(parent)
        self._color = color
        self._rainbow = rainbow
        self._active = False
        self.setFixedSize(38, 38)

    def set_active(self, a):
        self._active = a
        self.update()

    def paintEvent(self, ev):
        from PySide6.QtGui import QConicalGradient
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self._active:
            p.setPen(QPen(QColor("#e6edf3"), 2))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(1, 1, 36, 36)
        if self._rainbow:
            cg = QConicalGradient(19, 19, 0)
            cg.setColorAt(0.0, QColor("#ef4444"))
            cg.setColorAt(0.3, QColor("#f5b544"))
            cg.setColorAt(0.6, QColor("#22d3ee"))
            cg.setColorAt(0.9, QColor("#a855f7"))
            cg.setColorAt(1.0, QColor("#ef4444"))
            p.setPen(QPen(cg, 3))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(6, 6, 26, 26)
        else:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(self._color))
            p.drawEllipse(6, 6, 26, 26)
        p.end()


class _AccentDot(QWidget):
    dot_clicked = Signal(str)

    def __init__(self, color, name, rainbow=False, active=False, parent=None):
        super().__init__(parent)
        self._color = color
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        v = QVBoxLayout(self)
        v.setContentsMargins(2, 2, 2, 0)
        v.setSpacing(6)
        self._circ = _AccentCircle(color, rainbow)
        self._circ.set_active(active)
        self._circ.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        v.addWidget(self._circ, 0, Qt.AlignmentFlag.AlignHCenter)
        lb = QLabel(name)
        lb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lb.setStyleSheet(
            "color: #8b949e; font-size: 10px; background: transparent;")
        lb.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        v.addWidget(lb)

    def set_active(self, a):
        self._circ.set_active(a)

    def mousePressEvent(self, ev):
        self.dot_clicked.emit(self._color)
        super().mousePressEvent(ev)


class _AccentDotGroup(QWidget):
    color_changed = Signal(str)

    def __init__(self, colors, current, names=None, rainbow_last=False,
                 parent=None):
        super().__init__(parent)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)
        self._dots = []
        for i, c in enumerate(colors):
            nm = names[i] if names else c
            d = _AccentDot(
                c, nm,
                rainbow=(rainbow_last and i == len(colors) - 1),
                active=(c == current))
            d.dot_clicked.connect(self.color_changed.emit)
            d.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            lay.addWidget(d)
            self._dots.append(d)

    def set_current(self, c):
        for d in self._dots:
            d.set_active(d._color == c)


class VoiceCardV2(QFrame):
    clicked = Signal()
    fav_toggled = Signal()
    preview_toggled = Signal()

    def __init__(self, window, name, premium, selected, favorite, parent=None, compact=False):
        super().__init__(parent)
        self._name = name
        self._C = compact
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(74 if compact else 150)
        self._set_border(selected)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(1, 1, 1, 1)
        inner = QFrame()
        inner.setObjectName("v2inner")
        inner.setStyleSheet(
            "#v2inner { background: rgba(10,14,24,214); border-radius: 15px; }")
        outer.addWidget(inner)
        h = QHBoxLayout(inner)
        h.setContentsMargins(10 if self._C else 24, 0, 8 if self._C else 24, 0)
        h.setSpacing(10 if self._C else 18)
        # ---- avatar con anillo por voz + badge estrella ----
        av = QWidget()
        av.setFixedSize(40 if self._C else 104, 40 if self._C else 104)
        av.setStyleSheet("background: transparent;")
        self._av = av
        rcol = _RING_COLORS[len(name) % len(_RING_COLORS)]
        ring = QLabel(av)
        ring.setGeometry(0, 0, 40 if self._C else 104, 40 if self._C else 104)
        ring.setStyleSheet(
            "background: " + rcol + "; border-radius: " + ("20px" if self._C else "52px") + ";")
        photo = PreviewPhoto(av)
        photo.setGeometry(3, 3, 34 if self._C else 96, 34 if self._C else 96)
        photo.setScaledContents(True)
        self.photo = photo
        low = name.lower()
        fname = next((f for k, f in PREMIUM_PHOTOS.items() if k in low), None)
        if fname is None:
            first = name.replace("Microsoft ", "").split(" ")[0].strip().lower()
            fname = "face_f.png" if first.endswith("a") else "face_m.png"
        size = 34 if self._C else 96
        ckey = (fname, size)
        out = _FACE_CACHE.get(ckey)
        if out is None:
            out = QPixmap(size, size)
            out.fill(Qt.GlobalColor.transparent)
            fpath = window._resource_path(Path("assets") / "icons" / fname)
            if fpath.exists():
                src = QPixmap(str(fpath))
                if not src.isNull():
                    pnt = QPainter(out)
                    pnt.setRenderHint(QPainter.RenderHint.Antialiasing)
                    clip = QPainterPath()
                    clip.addEllipse(0, 0, size, size)
                    pnt.setClipPath(clip)
                    sc = src.scaled(size, size,
                                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                    Qt.TransformationMode.SmoothTransformation)
                    pnt.drawPixmap(0, 0, sc, (sc.width() - size) // 2,
                                   (sc.height() - size) // 2, size, size)
                    pnt.end()
            _FACE_CACHE[ckey] = out
        self._avatar_pix = out
        self._hover = False
        self._playing = False
        photo.setPixmap(out)
        photo.setStyleSheet("background: transparent;")
        photo.hover_changed.connect(self._set_hover2)
        photo.play_clicked.connect(lambda: self.preview_toggled.emit())
        if hasattr(window, "preview_changed"):
            window.preview_changed.connect(self._on_prev2)
        if selected:
            sb = QLabel(av)
            sb.setGeometry(24 if self._C else 76, 0, 16 if self._C else 28, 16 if self._C else 28)
            sb.setPixmap(make_icon("star", "#ffffff", 8 if self._C else 13))
            sb.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sb.setStyleSheet(
                "background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
                " stop:0 #3b82f6, stop:1 #2563eb); border-radius: " + ("8px" if self._C else "14px") + ";")
            self._sel_badge = sb
        else:
            self._sel_badge = None
        h.addWidget(av)
        # ---- boton play circular ----
        pb = QPushButton()
        pb.setFixedSize(28 if self._C else 52, 28 if self._C else 52)
        pb.setIcon(QIcon(make_icon("star", "#ffffff", 12 if self._C else 16)))
        pb.setIconSize(QSize(12 if self._C else 16, 12 if self._C else 16))
        pb.setStyleSheet(
            "QPushButton { background: rgba(124,92,255,18);"
            " border: 1.5px solid " + ACCENT + "; border-radius: " + ("14px" if self._C else "26px") + "; }"
            " QPushButton:hover { background: rgba(124,92,255,40); }")
        pb.setCursor(Qt.CursorShape.PointingHandCursor)
        pb.setToolTip("Usar esta voz")
        pb.clicked.connect(
            lambda: (window._select_voice(self._name),
                     window._switch_page(0)))
        if self._C:
            pb.hide()
        h.addWidget(pb)
        # ---- info ----
        info = QVBoxLayout()
        info.setSpacing(6 if self._C else 10)
        info.addStretch(1)
        nm = _ElideLabel(window._display_voice_name(name))
        nm.setStyleSheet("color: #ffffff; font-size: " + ("13px" if self._C else "17px") + "; font-weight: 700;")
        info.addWidget(nm)
        prow = QHBoxLayout()
        prow.setSpacing(8)
        cr = QLabel()
        cr.setPixmap(make_icon("crown", "#f5b301", 10 if self._C else 14))
        if self._C:
            cr.hide()
        prow.addWidget(cr)
        _etx, _ecol = _etiqueta_voz(window, name, premium)
        plbl = QLabel(_etx)
        plbl.setStyleSheet("color: " + _ecol + "; font-size: " + ("10px" if self._C else "12px") + "; font-weight: 600;")
        prow.addWidget(plbl)
        prow.addStretch(1)
        info.addLayout(prow)
        if self._C:
            info.addSpacing(4)
            cl = _ElideLabel(window._voice_subtitle(name, premium))
            cl.setStyleSheet(
                "color: #8b949e; font-size: 11px; background: transparent;")
            info.addWidget(cl)
        else:
            chips = QHBoxLayout()
            chips.setSpacing(10)
            for tag in window._voice_subtitle(name, premium).split("\u00b7"):
                ch = QLabel(tag.strip())
                ch.setStyleSheet(
                    "color: #c4b5fd; font-size: 11px;"
                    " border: 1px solid rgba(124,92,255,55); border-radius: 12px;"
                    " padding: 5px 12px; background: rgba(124,92,255,26);")
                chips.addWidget(ch)
            chips.addStretch(1)
            info.addLayout(chips)
        info.addStretch(1)
        h.addLayout(info, 1)
        # ---- derecha: Pro + heart ----
        right = QVBoxLayout()
        right.setSpacing(0 if self._C else 16)
        trow = QHBoxLayout()
        trow.setSpacing(8 if self._C else 14)
        if premium:
            pro = QLabel("Pro")
            pro.setStyleSheet(
                "background: #7c5cff; color: white; border-radius: " +
                ("5px" if self._C else "9px") + "; font-size: " +
                ("8px" if self._C else "10px") + "; font-weight: 700;"
                " padding: " + ("2px 5px" if self._C else "4px 12px") + ";")
            trow.addWidget(pro)
        hb = QPushButton()
        hb.setFixedSize(28 if self._C else 30, 28 if self._C else 30)
        hb.setIcon(QIcon(make_icon(
            "heart_fill" if favorite else "heart",
            "#ef4444" if favorite else "#8b949e", 14 if self._C else 20)))
        hb.setIconSize(QSize(14 if self._C else 20, 14 if self._C else 20))
        hb.setStyleSheet("background: transparent; border: none;")
        hb.setCursor(Qt.CursorShape.PointingHandCursor)
        hb.clicked.connect(lambda: self.fav_toggled.emit())
        trow.addWidget(hb)
        self._hb = hb
        trow.addStretch(1)
        right.addStretch(1)
        right.addLayout(trow)
        right.addStretch(1)
        h.addLayout(right)

    def _set_border(self, fav):
        if fav:
            bg = "qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #3b82f6, stop:1 " + ACCENT + ")"
        else:
            bg = "rgba(148,163,255,22)"
        self.setStyleSheet(
            "VoiceCardV2 { background: " + bg + "; border-radius: 16px; }")

    def set_state(self, selected, favorite):
        self._set_border(selected)
        if selected and getattr(self, "_sel_badge", None) is None:
            sb = QLabel(self._av)
            sb.setGeometry(24 if self._C else 76, 0, 16 if self._C else 28, 16 if self._C else 28)
            sb.setPixmap(make_icon("star", "#ffffff", 8 if self._C else 13))
            sb.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sb.setStyleSheet(
                "background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
                " stop:0 #3b82f6, stop:1 #2563eb); border-radius: " +
                ("8px" if self._C else "14px") + ";")
            sb.show()
            self._sel_badge = sb
        elif not selected and getattr(self, "_sel_badge", None) is not None:
            self._sel_badge.hide()
            self._sel_badge = None
        self._hb.setIcon(QIcon(make_icon(
            "heart_fill" if favorite else "heart",
            "#ef4444" if favorite else "#8b949e", 14 if self._C else 20)))

    def _set_hover2(self, hover):
        self._hover = hover
        self._update_photo2()

    def _on_prev2(self, name, playing):
        self._playing = (name == self._name) and playing
        self._update_photo2()

    def _update_photo2(self):
        if self._hover:
            self.photo.setPixmap(self._make_overlay2())
        else:
            self.photo.setPixmap(self._avatar_pix)

    def _make_overlay2(self):
        size = 34 if self._C else 96
        base = self._avatar_pix.scaled(
            size, size, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation)
        pix = base.copy(0, 0, size, size)
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QColor(0, 0, 0, 110))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(0, 0, size, size)
        p.setBrush(QColor("#ffffff"))
        if self._playing:
            w = max(3, size // 12)
            p.drawRoundedRect(int(size * 0.36), int(size * 0.30), w, int(size * 0.40), 2, 2)
            p.drawRoundedRect(int(size * 0.56), int(size * 0.30), w, int(size * 0.40), 2, 2)
        else:
            p.drawPolygon(QPolygon([
                QPoint(int(size * 0.40), int(size * 0.30)),
                QPoint(int(size * 0.40), int(size * 0.70)),
                QPoint(int(size * 0.72), int(size * 0.50))]))
        p.end()
        return pix

    def mousePressEvent(self, ev):
        self.clicked.emit()
        super().mousePressEvent(ev)


def _rebuild_voices_page(self):
    if not getattr(self, "_voc_built", False):
        return
    try:
        from core.pocket_cloner import cloner_instance
        _cloned = cloner_instance.list_saved_voices()
    except Exception:
        _cloned = []
    self._cloned_set = set(_cloned)
    if _cloned:
        _base = [v for v in getattr(self, "_voices", []) if v not in self._cloned_set]
        self._voices = _base + list(_cloned)
    self._clear_layout(self.all_layout)
    q = getattr(self, "_vsearch", "")
    tab = getattr(self, "_vtab", "todas")
    vall = getattr(self, "_vall", False)
    names = []
    for name in sorted(getattr(self, "_voices", []), key=self._sort_key):
        premium = self._is_premium(name)
        if tab == "premium" and not premium:
            continue
        if tab == "favoritas" and name not in self._favorites():
            continue
        if tab == "todas" and not vall and not premium:
            continue
        if q and q not in name.lower():
            continue
        names.append(name)
    self._voc_names = names
    self._voc_shown = 0
    self._voc_more_btn = None
    self._append_voc_cards()


def _append_voc_cards(self):
    lay = self.all_layout
    if lay.count():
        last = lay.itemAt(lay.count() - 1)
        if last is not None and last.spacerItem() is not None:
            lay.takeAt(lay.count() - 1)
    btn = getattr(self, "_voc_more_btn", None)
    if btn is not None:
        lay.removeWidget(btn)
        btn.deleteLater()
        self._voc_more_btn = None
    batch = self._voc_names[self._voc_shown:self._voc_shown + 8]
    for name in batch:
        premium = self._is_premium(name)
        card = VoiceCardV2(self, name, premium,
                           name == getattr(self, "_selected_voice", ""),
                           name in self._favorites())
        card.clicked.connect(lambda n=name: self._select_voice(n))
        card.fav_toggled.connect(lambda n=name: self._toggle_fav(n))
        card.preview_toggled.connect(lambda n=name: self._toggle_preview(n))
        lay.addWidget(card)
        self._voc_shown += 1
    if not self._voc_shown:
        empty = QLabel("No hay voces que mostrar con este filtro.")
        empty.setStyleSheet("color: #8b949e; font-size: 13px; padding: 40px;")
        empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(empty)
    if self._voc_shown < len(self._voc_names):
        more = QPushButton("Cargar m\u00e1s voces")
        more.setCursor(Qt.CursorShape.PointingHandCursor)
        more.setStyleSheet(
            "QPushButton { background: rgba(124,92,255,12); color: #cfe3ff;"
            " border: 1.5px solid #8b5cf6; border-radius: 12px;"
            " font-weight: 700; font-size: 12px; padding: 10px; }"
            " QPushButton:hover { background: rgba(124,92,255,28); }")
        more.clicked.connect(self._append_voc_cards)
        lay.addWidget(more)
        self._voc_more_btn = more
    lay.addStretch(1)


def _voc_set_tab(self, tab):
    self._vtab = tab
    for key in ("todas", "premium", "favoritas"):
        b = getattr(self, "_vtab_btn_" + key, None)
        if b is None:
            continue
        if key == tab:
            b.setStyleSheet(
                "QPushButton { color: #ffffff; font-weight: 700; font-size: 13px;"
                " background: #141b2e; border: none;"
                " border-bottom: 2px solid #8b5cf6; padding: 10px 18px; }")
        else:
            b.setStyleSheet(
                "QPushButton { color: #8b949e; font-weight: 600; font-size: 13px;"
                " background: transparent; border: none; padding: 10px 18px; }"
                " QPushButton:hover { color: #c9d1d9; }")
    self._rebuild_voices_page()


def _voc_toggle_all(self):
    self._vall = not getattr(self, "_vall", False)
    try:
        if self._vall:
            self.vall_btn.setText("  Solo Premium")
            self.vall_btn.setIcon(
                QIcon(_chat_svg(_GEMV2, "#8b5cf6", 14)))
            if hasattr(self, "_voc_title"):
                self._voc_title.setText("Todas las voces")
                self._voc_gem.setPixmap(
                    make_icon("globe", "#7cb7ff", 26))
                self._voc_sub.setText(
                    "Explora todas las voces disponibles en tu sistema.")
        else:
            self.vall_btn.setText("  Ver todas")
            self.vall_btn.setIcon(
                QIcon(make_icon("globe", "#7cb7ff", 14)))
            if hasattr(self, "_voc_title"):
                self._voc_title.setText(
                    'Solo <span style="color:#a855f7;">Premium</span>')
                self._voc_gem.setPixmap(
                    _chat_svg(_GEMV2, "#8b5cf6", 26))
                self._voc_sub.setText(
                    "Voces de alta calidad para proyectos profesionales.")
    except Exception:
        pass
    self._rebuild_voices_page()


class VoiceCard(QFrame):
    clicked = Signal()
    fav_toggled = Signal()
    preview_toggled = Signal()

    def __init__(self, window, name, premium, selected, favorite, parent=None):
        super().__init__(parent)
        self.window = window
        self.voice_name = name
        self._hover = False
        self._playing = False
        self.setFixedHeight(74)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 0, 8, 0)
        lay.setSpacing(10)
        self._avatar_pix = window._avatar_pixmap(
            name, "#f5b301" if premium else "#232f4b")
        self.photo = PreviewPhoto()
        self.photo.setFixedSize(40, 40)
        self.photo.setScaledContents(True)
        self.photo.setPixmap(self._avatar_pix)
        self.photo.setStyleSheet("background: transparent;")
        self.photo.hover_changed.connect(self._set_hover)
        self.photo.play_clicked.connect(self.preview_toggled.emit)
        if hasattr(window, "preview_changed"):
            window.preview_changed.connect(self._on_preview_changed)
        lay.addWidget(self.photo)
        tw = QWidget()
        tw.setStyleSheet("background: transparent;")
        tw.setMinimumWidth(90)
        tw.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        tl = QVBoxLayout(tw)
        tl.setContentsMargins(0, 0, 0, 0)
        tl.setSpacing(1)
        n = QLabel(window._display_voice_name(name))
        n.setStyleSheet(
            f"color: {TEXT}; font-size: 13px; font-weight: 600;"
            " background: transparent;"
        )
        s = QLabel(window._voice_subtitle(name, premium))
        s.setStyleSheet(
            f"color: {MUTED}; font-size: 11px; background: transparent;"
        )
        tl.addWidget(n)
        if premium:
            _etx, _ecol = _etiqueta_voz(window, name, premium)
            g = QLabel(_etx)
            g.setStyleSheet(
                "color: " + _ecol + "; font-size: 10px; font-weight: 600;"
                " background: transparent;"
            )
            tl.addWidget(g)
        tl.addWidget(s)
        lay.addWidget(tw, 1)
        if premium:
            badge = QLabel("Pro")
            badge.setStyleSheet(
                f"background: {PURPLE}; color: white; border-radius: 5px;"
                " font-size: 8px; font-weight: 700; padding: 2px 5px;"
            )
            badge.setFixedHeight(17)
            badge.setMaximumWidth(38)
            badge.setSizePolicy(
                QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            lay.addWidget(badge)
        self.heart = QPushButton()
        self.heart.setFixedSize(28, 28)
        self.heart.setIcon(QIcon(make_icon(
            "heart_fill" if favorite else "heart",
            RED if favorite else MUTED, 14)))
        self.heart.setIconSize(QSize(14, 14))
        self.heart.setStyleSheet(
            "QPushButton { background: transparent; border: none;"
            f" border-radius: 8px; }} QPushButton:hover {{ background: {CARD2}; }}"
        )
        self.heart.clicked.connect(self.fav_toggled.emit)
        lay.addWidget(self.heart)
        self.set_selected(selected)

    def _set_hover(self, hover):
        self._hover = hover
        self._update_photo()

    def _on_preview_changed(self, name, playing):
        self._playing = (name == self.voice_name) and playing
        if self._hover:
            self._update_photo()

    def _update_photo(self):
        if self._hover:
            self.photo.setPixmap(self._make_overlay())
        else:
            self.photo.setPixmap(self._avatar_pix)

    def _make_overlay(self):
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

    def set_selected(self, selected):
        if selected:
            self.setStyleSheet(
                f"VoiceCard {{ background: {CARD2}; border: 1px solid #6d5dfc;"
                " border-radius: 12px; }}"
            )
        else:
            self.setStyleSheet(
                f"VoiceCard {{ background: {CARD}; border: none;"
                f" border-radius: 12px; }} VoiceCard:hover {{ background: {CARD2}; }}"
            )

    def mouseReleaseEvent(self, event):
        self.clicked.emit()



class HistoryCardV2(QFrame):
    load_clicked = Signal()
    delete_clicked = Signal()

    def __init__(self, window, entry, parent=None):
        super().__init__(parent)
        self.setFixedHeight(100)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(
            "HistoryCardV2 { background: rgba(13,17,26,214);"
            " border: 1px solid rgba(148,163,255,20); border-radius: 14px; }"
            " HistoryCardV2:hover { background: rgba(20,26,40,230); }")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 0, 14, 0)
        lay.setSpacing(14)
        dot = QLabel()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet("background: #a855f7; border-radius: 4px;")
        lay.addWidget(dot)
        label = entry.get("label", "Texto manual")
        low = label.lower()
        if low.endswith(".pdf"):
            kind, color = "doc", RED
        elif low.endswith((".doc", ".docx", ".rtf")):
            kind, color = "doc", BLUE
        elif low.endswith((".txt", ".md", ".log", ".csv")):
            kind, color = "doc", TEAL
        elif label == "Texto manual":
            kind, color = "text", TEAL
        else:
            kind, color = "doc", MUTED
        box = QFrame()
        box.setFixedSize(64, 64)
        box.setStyleSheet(
            "QFrame { background: #10141f; border: 1px solid #262d3a;"
            " border-radius: 14px; }")
        bl = QVBoxLayout(box)
        bl.setContentsMargins(0, 0, 0, 0)
        ic = IconLabel(kind, 26, color)
        ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bl.addWidget(ic)
        lay.addWidget(box)
        tw = QWidget()
        tw.setStyleSheet("background: transparent;")
        tw.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        tl = QVBoxLayout(tw)
        tl.setContentsMargins(0, 6, 0, 6)
        tl.setSpacing(4)
        n = QLabel(label)
        n.setStyleSheet(
            "color: #ffffff; font-size: 15px; font-weight: 700;"
            " background: transparent;")
        tl.addWidget(n)
        prev = _ElideLabel((entry.get("content", "") or "").replace("\n", " "))
        prev.setStyleSheet(
            "color: #8b949e; font-size: 12.5px; background: transparent;")
        tl.addWidget(prev)
        meta = QHBoxLayout()
        meta.setSpacing(8)
        cal = QLabel()
        cal.setPixmap(make_icon("calendar", "#8b949e", 12))
        meta.addWidget(cal)
        ts = entry.get("ts") or entry.get("date") or entry.get("time") or ""
        if ts:
            ml = QLabel(str(ts))
            ml.setStyleSheet(
                "color: #8b949e; font-size: 11.5px; background: transparent;")
            meta.addWidget(ml)
        voice = entry.get("voice", "")
        is_file = low.endswith((".pdf", ".doc", ".docx", ".rtf",
                                ".txt", ".md", ".log", ".csv"))
        if voice:
            sep = QLabel("\u00b7")
            sep.setStyleSheet("color: #8b949e; font-size: 11.5px;")
            meta.addWidget(sep)
            vv = QLabel('Voz: <span style="color:#8b7bff;">' + voice + "</span>")
            vv.setStyleSheet(
                "color: #8b949e; font-size: 11.5px; background: transparent;")
            meta.addWidget(vv)
        elif is_file:
            sep = QLabel("\u00b7")
            sep.setStyleSheet("color: #8b949e; font-size: 11.5px;")
            meta.addWidget(sep)
            fl = QLabel("Archivo de texto")
            fl.setStyleSheet("color: #8b949e; font-size: 11.5px;")
            meta.addWidget(fl)
        meta.addStretch(1)
        tl.addLayout(meta)
        lay.addWidget(tw, 1)
        cp = QPushButton()
        cp.setFixedSize(44, 44)
        cp.setIcon(QIcon(make_icon("copy", "#7cb7ff", 18)))
        cp.setIconSize(QSize(18, 18))
        cp.setCursor(Qt.CursorShape.PointingHandCursor)
        cp.setToolTip("Cargar en el editor")
        cp.setStyleSheet(
            "QPushButton { background: transparent; border: 1px solid #2b4bd0;"
            " border-radius: 12px; }"
            " QPushButton:hover { background: rgba(37,99,235,25); }")
        cp.clicked.connect(lambda: self.load_clicked.emit())
        lay.addWidget(cp)
        tb = QPushButton()
        tb.setFixedSize(44, 44)
        tb.setIcon(QIcon(make_icon("trash", "#ef4444", 18)))
        tb.setIconSize(QSize(18, 18))
        tb.setCursor(Qt.CursorShape.PointingHandCursor)
        tb.setToolTip("Eliminar entrada")
        tb.setStyleSheet(
            "QPushButton { background: transparent; border: 1px solid #7f1d1d;"
            " border-radius: 12px; }"
            " QPushButton:hover { background: rgba(239,68,68,25); }")
        tb.clicked.connect(lambda: self.delete_clicked.emit())
        lay.addWidget(tb)


class HistoryCard(QFrame):
    load_clicked = Signal()
    delete_clicked = Signal()

    def __init__(self, window, entry, parent=None):
        super().__init__(parent)
        self.setFixedHeight(74)
        label = entry.get("label", "Texto manual")
        low = label.lower()
        if low.endswith(".pdf"):
            kind, color = "doc", RED
        elif low.endswith((".doc", ".docx", ".rtf")):
            kind, color = "doc", BLUE
        elif low.endswith((".txt", ".md", ".log", ".csv")):
            kind, color = "doc", TEAL
        elif label == "Texto manual":
            kind, color = "text", TEAL
        else:
            kind, color = "doc", MUTED
        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 0, 10, 0)
        lay.setSpacing(12)
        box = QFrame()
        box.setFixedSize(40, 40)
        box.setStyleSheet(
            f"QFrame {{ background: {CARD2}; border-radius: 10px; }}")
        bl = QVBoxLayout(box)
        bl.setContentsMargins(0, 0, 0, 0)
        ic = IconLabel(kind, 17, color)
        ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bl.addWidget(ic)
        lay.addWidget(box)
        tw = QWidget()
        tw.setStyleSheet("background: transparent;")
        tw.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        tl = QVBoxLayout(tw)
        tl.setContentsMargins(0, 0, 0, 0)
        tl.setSpacing(2)
        n = QLabel(label)
        n.setStyleSheet(
            f"color: {TEXT}; font-size: 13px; font-weight: 600;"
            " background: transparent;"
        )
        preview = QLabel(
            (entry.get("content", "") or "").replace("\n", " ")[:80])
        preview.setStyleSheet(
            f"color: {MUTED}; font-size: 11px; background: transparent;"
        )
        tl.addWidget(n)
        tl.addWidget(preview)
        lay.addWidget(tw, 1)
        load_btn = SquareButton("paste", "Cargar en el editor")
        load_btn.setFixedSize(34, 34)
        load_btn.clicked.connect(self.load_clicked.emit)
        del_btn = SquareButton("trash", "Eliminar entrada")
        del_btn.setFixedSize(34, 34)
        del_btn.setStyleSheet(
            f"SquareButton {{ background: {CARD}; border: 1px solid"
            f" {BORDER}; border-radius: 10px; }}"
            " SquareButton:hover { background: rgba(239,68,68,60); }"
        )
        del_btn.icon.setPixmap(make_icon("trash", RED, 19))
        del_btn.clicked.connect(self.delete_clicked.emit)
        lay.addWidget(load_btn)
        lay.addWidget(del_btn)
        self.setStyleSheet(
            f"HistoryCard {{ background: {CARD}; border: none;"
            f" border-radius: 12px; }} HistoryCard:hover {{ background: {CARD2}; }}"
        )


class _ClonedPreviewWorker(QThread):
    """Hilo para generar preview de voz clonada sin congelar la UI"""
    done = Signal(str)
    failed = Signal(str)

    def __init__(self, voice_name, text, parent=None):
        super().__init__(parent)
        self.voice_name = voice_name
        self.text = text
        self._stop_requested = False

    def request_stop(self):
        """Solicita detener el worker (compatibilidad con interfaz SAPI)"""
        self._stop_requested = True

    def run(self):
        if self._stop_requested:
            return
        try:
            from core.pocket_cloner import cloner_instance
            out = cloner_instance.generate_with_voice(self.voice_name, self.text)
            if not self._stop_requested:
                self.done.emit(out)
        except Exception as e:
            if not self._stop_requested:
                self.failed.emit(str(e))


class MainWindow(QMainWindow):
    MAX_HISTORY = 10
    preview_changed = Signal(str, bool)

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("naturalvoice_tts.ui")
        self.settings = load_settings()
        self.setWindowTitle(f"WillpoVoice v{APP_VERSION}")
        self.resize(1280, 800)
        self.setMinimumSize(980, 640)
        icon_path = self._resource_path(Path("assets") / "icons" / "icon.ico")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        self.engine = TTSEngine(logger=self.logger)
        self.exporter = AudioExporter(adapter=self.engine.adapter, logger=self.logger)
        self.export_worker = None
        self._build_ui()
        self._connect_signals()
        self._load_voices()
        self._load_history()

    @staticmethod
    def _resource_path(rel):
        base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
        return base / rel

    def _flag_pixmap(self, kind):
        w, h = 22, 16
        pix = QPixmap(w, h)
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        if kind == "es":
            p.fillRect(0, 0, w, h, QColor("#aa151b"))
            p.fillRect(0, 4, w, 8, QColor("#f1bf00"))
        elif kind == "us":
            for i in range(7):
                c = "#b22234" if i % 2 == 0 else "#ffffff"
                p.fillRect(0, i * h // 7, w, h // 7 + 1, QColor(c))
            p.fillRect(0, 0, 10, 8, QColor("#3c3b6e"))
        else:
            p.fillRect(0, 0, w, h, QColor("#1d4ed8"))
            p.setPen(QPen(QColor("#ffffff"), 1.5))
            p.drawLine(0, h // 2, w, h // 2)
            p.drawLine(w // 2, 0, w // 2, h)
            p.drawEllipse(4, 3, w - 8, h - 6)
        p.end()
        return pix

    def _avatar_pixmap(self, name, ring=None):
        low = name.lower()
        fname = None
        for key, f in PREMIUM_PHOTOS.items():
            if key in low:
                fname = f
                break
        size = 46
        if fname is None:
            first = name.replace("Microsoft ", "").split(" ")[0].strip().lower()
            female = first.endswith("a")
            fname = "face_f.png" if female else "face_m.png"
        path = self._resource_path(Path("assets") / "icons" / fname)
        if path.exists():
            src = QPixmap(str(path))
            if not src.isNull():
                out = QPixmap(size, size)
                out.fill(Qt.GlobalColor.transparent)
                p = QPainter(out)
                p.setRenderHint(QPainter.RenderHint.Antialiasing)
                clip = QPainterPath()
                clip.addEllipse(0, 0, size, size)
                p.setClipPath(clip)
                sc = src.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                Qt.TransformationMode.SmoothTransformation)
                x = (sc.width() - size) // 2
                y = (sc.height() - size) // 2
                p.drawPixmap(0, 0, sc, x, y, size, size)
                if ring:
                    p.setClipping(False)
                    p.setPen(QPen(QColor(ring), 2))
                    p.drawEllipse(1, 1, size - 2, size - 2)
                p.end()
                return out
        out = QPixmap(size, size)
        out.fill(Qt.GlobalColor.transparent)
        p = QPainter(out)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QColor(CARD2))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(0, 0, size, size)
        p.setPen(QColor(BLUE))
        p.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        p.drawText(QRect(0, 0, size, size), Qt.AlignmentFlag.AlignCenter, name[:1].upper())
        if ring:
            p.setPen(QPen(QColor(ring), 2))
            p.drawEllipse(1, 1, size - 2, size - 2)
        p.end()
        return out

    def _is_premium(self, name):
        if name in getattr(self, "_cloned_set", set()):
            return True
        low = name.lower()
        return "multilingual" in low or any(k in low for k in PREMIUM_PHOTOS)

    def _display_voice_name(self, name):
        n = name.replace("Microsoft ", "")
        if "Multilingual" in n:
            return f"{n.split('Multilingual')[0].strip()} (Multilingual)"
        return n.replace("Online (Natural)", "").replace("(Natural)", "").strip()

    def _voice_subtitle(self, name, premium):
        subs = ["Acento neutro · Profesional", "Acento suave · Natural",
                "Acento cálido · Amigable", "Acento claro · Formal"]
        return subs[len(name) % len(subs)] if premium else "Voz estándar"

    def _add_neon(self, widget, color):
        eff = QGraphicsDropShadowEffect(widget)
        eff.setBlurRadius(16)
        eff.setOffset(0, 0)
        eff.setColor(QColor(color))
        widget.setGraphicsEffect(eff)


class AdvButton(QFrame):
    """Boton de opciones avanzadas con gear y chevron."""

    clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(38)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 0, 12, 0)
        lay.setSpacing(8)
        self.icon = IconLabel("gear", 14, "#7c5cff")
        lay.addWidget(self.icon)
        self.label = QLabel("Opciones avanzadas")
        self.label.setStyleSheet(
            f"color: {TEXT}; font-size: 12px; font-weight: 600;"
            " background: transparent;")
        lay.addWidget(self.label)
        lay.addStretch()
        self.chevron = IconLabel("chevron-down", 12, MUTED)
        lay.addWidget(self.chevron)
        self.setStyleSheet(
            f"AdvButton {{ background: {CARD2}; border: 1px solid {BORDER};"
            " border-radius: 10px; }"
            f" AdvButton:hover {{ background: #232b3a; }}")

    def mouseReleaseEvent(self, event):
        self.clicked.emit()

    def set_expanded(self, expanded):
        glyph = "chevron-up" if expanded else "chevron-down"
        old = self.chevron
        lay = self.layout()
        idx = lay.indexOf(old)
        nuevo = IconLabel(glyph, 12, MUTED)
        if idx >= 0:
            lay.insertWidget(idx, nuevo)
        else:
            lay.addWidget(nuevo)
        old.deleteLater()
        self.chevron = nuevo


class AdvCard(QFrame):
    clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("advCard")
        self.setFixedHeight(44)
        self.setStyleSheet(
            f"AdvCard {{ background: {CARD}; border: 1px solid {BORDER};"
            " border-radius: 14px; }"
            " AdvCard:hover { border-color: #34406b; }")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(12)
        badge = QFrame()
        badge.setFixedSize(30, 30)
        badge.setStyleSheet("QFrame { background: rgba(139,92,246,45); border-radius: 15px; }")
        bl = QVBoxLayout(badge)
        bl.setContentsMargins(0, 0, 0, 0)
        bic = QLabel()
        bic.setPixmap(make_icon("gear", "#a78bfa", 14))
        bic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bl.addWidget(bic)
        lay.addWidget(badge)
        col = QVBoxLayout()
        col.setSpacing(2)
        self.title_lbl = QLabel("Opciones avanzadas")
        self.title_lbl.setStyleSheet(f"color: {TEXT}; font-size: 12px; font-weight: 700; background: transparent;")
        col.addWidget(self.title_lbl)
        lay.addLayout(col, 1)
        self.chev = QLabel()
        self.chev.setPixmap(make_icon("chevron-down", MUTED, 14))
        lay.addWidget(self.chev)

    def mouseReleaseEvent(self, event):
        self.clicked.emit()

    def setText(self, s):
        self.set_expanded(s.startswith(("<", "\uff1c")))

    def set_expanded(self, on):
        self.chev.setPixmap(make_icon("chevron-up" if on else "chevron-down", MUTED, 16))


class ToolButton(QFrame):
    clicked = Signal()

    def __init__(self, glyph, text, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 6, 10, 6)
        lay.setSpacing(8)
        self.icon = IconLabel(glyph, 13, MUTED)
        self.label = QLabel(text)
        self.label.setStyleSheet(
            f"color: {MUTED}; font-size: 12px; background: transparent;"
        )
        lay.addWidget(self.icon)
        lay.addWidget(self.label)
        self.setStyleSheet(
            "ToolButton { background: transparent; border: 1px solid"
            f" transparent; border-radius: 8px; }} ToolButton:hover {{ background: {CARD2}; }}"
        )
        self.setMinimumWidth(0)

    def mouseReleaseEvent(self, event):
        self.clicked.emit()




def _slider_qss():
        return """
        QSlider::groove:horizontal {
            height: 6px;
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 #2a3552, stop:0.5 #4c3a8c, stop:1 #60a5fa);
            border-radius: 3px;
        }
        QSlider::handle:horizontal {
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 #c4b5fd, stop:1 #7c5cff);
            border: 2px solid #ffffff;
            width: 16px;
            height: 16px;
            margin: -6px 0;
            border-radius: 10px;
        }
        QSlider::handle:horizontal:hover {
            background: #a78bfa;
        }
        QSlider::sub-page:horizontal {
            background: transparent;
        }
        """

def _build_ui(self):
    central = QWidget()
    central.setObjectName("centralMain")
    central.setStyleSheet(
        "QWidget#centralMain { background: #0d1424; }"
    )
    self.setCentralWidget(central)
    self.setStyleSheet("QMainWindow { background: #0b0f1a; } QWidget#centralMain { background: #0b0f1a; } QStackedWidget { background: #0b0f1a; }")
    root = QHBoxLayout(central)
    root.setContentsMargins(0, 0, 0, 0)
    root.setSpacing(0)

    # ---------- SIDEBAR ----------
    self.sidebar = QFrame()
    self.sidebar.setFixedWidth(232)
    self.sidebar.setObjectName("sideBar")
    self.sidebar.setStyleSheet(
            "QFrame#sidebarMain { background: #0b0f1a;"
            " border-right: 1px solid #232f4b; }")
    sb = QVBoxLayout(self.sidebar)
    sb.setContentsMargins(14, 14, 14, 14)
    sb.setSpacing(4)
    self.hamburger = SquareButton("menu", "Menu")
    self.hamburger.clicked.connect(self._toggle_sidebar)
    sb.addWidget(self.hamburger, 0, Qt.AlignmentFlag.AlignLeft)
    sb.addSpacing(8)
    logo = QLabel()
    lp = self._resource_path(Path("assets") / "icons" / "logo.png")
    if not lp.exists():
        lp = self._resource_path(Path("assets") / "icons" / "icon.ico")
    if lp.exists():
        logo.setPixmap(QPixmap(str(lp)).scaledToHeight(
            40, Qt.TransformationMode.SmoothTransformation))
    logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
    logo.setStyleSheet("background: transparent;")
    self._logo_name = QLabel("WillpoVoice")
    self._logo_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
    self._logo_name.setStyleSheet(
        f"color: {TEXT}; font-size: 15px; font-weight: 700; background: transparent;"
    )
    self._logo_ver = QLabel(f"v{APP_VERSION}")
    self._logo_ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
    self._logo_ver.setStyleSheet(
        f"color: {MUTED}; font-size: 10px; background: transparent;"
    )
    sb.addWidget(logo)
    sb.addWidget(self._logo_name)
    sb.addWidget(self._logo_ver)
    sb.addSpacing(14)
    self._nav = []
    for glyph, text, page in (
        ("home", "Inicio", 0), ("history", "Historial", 1),
        ("mic", "Voces", 2), ("heart", "Favoritos", 3),
        ("folder", "Proyectos", 4), ("sparkles", "Chat IA", 5),
        ("gear", "Ajustes", 6),
    ):
        btn = NavButton(glyph, text)
        btn.clicked.connect(lambda _=False, pg=page: self._switch_page(pg))
        sb.addWidget(btn)
        self._nav.append((btn, page))

    # Boton de Clonar Voz con icono de robot
    clone_btn = NavButton("robot", "Clonar voz")
    clone_btn.clicked.connect(lambda _=False, pg=7: self._switch_page(pg))
    sb.addWidget(clone_btn)
    self._nav.append((clone_btn, 7))

    sep = QFrame()
    sep.setFixedHeight(1)
    sep.setStyleSheet(f"background: {BORDER};")
    sb.addWidget(sep)
    sb.addSpacing(4)
    for glyph, text, fn in (("help", "Ayuda", self.show_help),
                            ("headset", "Soporte", self.open_support)):
        btn = NavButton(glyph, text)
        btn.clicked.connect(lambda _=False, f=fn: f())
        sb.addWidget(btn)
        self._nav.append((btn, -1))
        self._token_chip_icon = QLabel()
        self._token_chip_icon.setPixmap(make_icon("coins", "#f5b544", 14))
        self._token_chip_text = QLabel("")
        self._token_chip_text.setStyleSheet(
            "color: #f5b544; font-weight: 700;"
            " font-size: 12px; background: transparent;")
        self._token_chip_wrap = QFrame()
        chw = QHBoxLayout(self._token_chip_wrap)
        chw.setContentsMargins(10, 6, 10, 6)
        chw.setSpacing(8)
        self._token_chip_icon.setFixedSize(16, 16)
        chw.addWidget(self._token_chip_icon)
        chw.addWidget(self._token_chip_text)
        chw.addStretch(1)
        self._token_chip_wrap.setStyleSheet(
            "QFrame { background: transparent; border: none; }")
        self._token_chip_wrap.setVisible(False)
        sb.addWidget(self._token_chip_wrap)
    sb.addStretch()
    self._prem_card = QFrame()
    self._prem_card.setStyleSheet(
        "QFrame { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
        " stop:0 #241a3d, stop:1 #3b2a63); border-radius: 14px; }"
    )
    pl = QVBoxLayout(self._prem_card)
    pl.setContentsMargins(14, 14, 14, 14)
    try:
        _d0 = license_manager.license_details()
        _lic0 = _d0.get("state") == "licensed"
        _t0 = _d0.get("tier", "")
        _n0 = _t0 if _t0 in ("Platinum", "Gold", "Estándar") else "Estándar"
    except Exception:
        _lic0, _n0 = False, "Estándar"
    pt = QLabel(("👑  WillpoVoice " + _n0) if _lic0 else "WillpoVoice")
    self._prem_title = pt
    pt.setStyleSheet(f"color: {TEXT}; font-size: 12px; font-weight: 700; background: transparent;")
    pd = QLabel(("Plan " + _n0 + " activo permanentemente.") if _lic0
                else "Desbloquea todas las voces y funciones premium.")
    self._prem_desc = pd
    pd.setWordWrap(True)
    pd.setStyleSheet(f"color: {MUTED}; font-size: 10px; background: transparent;")
    pb = QPushButton("✨ Ver planes")
    pb.setCursor(Qt.CursorShape.PointingHandCursor)
    pb.setStyleSheet(
        "QPushButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
        f" stop:0 {BLUE}, stop:1 {PURPLE}); color: white; border: none;"
        " border-radius: 8px; padding: 7px 12px; font-weight: 600; }"
    )
    pb.clicked.connect(self._open_plans)
    pl.addWidget(pt)
    pl.addWidget(pd)
    pl.addWidget(pb, 0, Qt.AlignmentFlag.AlignLeft)
    sb.addWidget(self._prem_card)
    root.addWidget(self.sidebar)

    # ---------- PAGINAS ----------
    self.pages = QStackedWidget()
    root.addWidget(self.pages, 1)

    page0 = QWidget()
    p0 = QVBoxLayout(page0)
    p0.setContentsMargins(16, 14, 16, 14)
    p0.setSpacing(14)

    header = QFrame()
    header.setFixedHeight(180)
    header.setMinimumWidth(0)
    header.setObjectName("headerCard")
    header.setStyleSheet(f"QFrame#headerCard {{ background: {CARD}; border-radius: 16px; }}")
    hg = QGridLayout(header)
    hg.setContentsMargins(0, 0, 0, 0)
    cover = QLabel()
    cp = self._resource_path(Path("assets") / "icons" / "portada.png")
    if not cp.exists():
        fd = self._resource_path(Path("assets") / "icons" / "portada_frames")
        if fd.exists():
            files = sorted(fd.glob("*.jpg")) or sorted(fd.glob("*.png"))
            if files:
                cp = files[len(files) // 2]
    if LIGHT_MODE:
        _lp = self._resource_path(Path("assets") / "icons" / "banner_light.png")
        if _lp.exists():
            cp = _lp
    if cp.exists():
        cover.setPixmap(QPixmap(str(cp)))
    cover.setScaledContents(True)
    cover.setMinimumSize(1, 1)
    cover.setSizePolicy(
        QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
    cover.setStyleSheet("background: transparent; border-radius: 16px;")
    hg.addWidget(cover, 0, 0)
    titles = QWidget()
    titles.setStyleSheet("background: transparent;")
    tl2 = QVBoxLayout(titles)
    tl2.setContentsMargins(24, 16, 0, 16)
    t1 = QLabel("WillpoVoice")
    t1.setStyleSheet("color: " + ("#17203a" if LIGHT_MODE else "white") +
                       "; font-size: 26px; font-weight: 700; background: transparent;")
    t2 = QLabel("Convierte texto en voz con voces naturales")
    t2.setStyleSheet("color: #cdd5ea; font-size: 12px; background: transparent;")
    tl2.addWidget(t1)
    tl2.addWidget(t2)
    tl2.addStretch()
    hg.addWidget(titles, 0, 0)
    p0.addWidget(header)

    stats = QHBoxLayout()
    stats.setSpacing(14)
    self.stat_voices = StatsCard("mic", TEAL, "Voces disponibles", "0")
    self.stat_langs = StatsCard("globe", BLUE, "Idiomas", "29")
    self.stat_conv = StatsCard("wave", TEAL, "Conversiones hoy",
                               str(self.settings.get("conv_today", 0)))
    for s in (self.stat_voices, self.stat_langs, self.stat_conv):
        s.setMinimumWidth(0)
        s.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
        stats.addWidget(s)
    p0.addLayout(stats)

    card = QFrame()
    card.setObjectName("convCard")
    card.setMinimumWidth(0)
    card.setStyleSheet(f"QFrame#convCard {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 16px; }}")
    cl = QVBoxLayout(card)
    cl.setContentsMargins(18, 14, 18, 16)
    cl.setSpacing(10)

    # ---------- fila superior: tabs + limpiar/pegar ----------
    top = QHBoxLayout()
    top.setSpacing(10)
    self.tab_text = TabButton("Texto manual")
    self.tab_file = TabButton("Importar archivo")
    self.tab_text.set_active(True)
    self.tab_text.setIcon(QIcon(make_icon("text", "#a78bfa", 14)))
    self.tab_text.setIconSize(QSize(14, 14))
    self.tab_file.setIcon(QIcon(make_icon("doc", MUTED, 14)))
    self.tab_file.setIconSize(QSize(14, 14))
    self.tab_file.clicked.connect(self._open_document_dialog)
    _uw = QFrame()
    _uwl = QVBoxLayout(_uw)
    _uwl.setContentsMargins(0, 0, 0, 0)
    _uwl.setSpacing(4)
    _uwl.addWidget(self.tab_text)
    _tab_under = QFrame()
    _tab_under.setFixedHeight(3)
    _tab_under.setVisible(False)
    _uwl.addWidget(_tab_under)
    top.addWidget(_uw)
    _uw2 = QFrame()
    _uw2l = QVBoxLayout(_uw2)
    _uw2l.setContentsMargins(0, 0, 0, 0)
    _uw2l.setSpacing(4)
    _uw2l.addWidget(self.tab_file)
    _spu = QFrame()
    _spu.setFixedHeight(3)
    _spu.setStyleSheet("background: transparent;")
    _uw2l.addWidget(_spu)
    top.addWidget(_uw2)
    top.addStretch()
    self.btn_clear = ToolButton("trash", "Limpiar")
    self.btn_paste = ToolButton("paste", "Pegar")
    self.btn_clear.icon.setPixmap(make_icon("trash", "#e879f9", 13))
    self.btn_paste.icon.setPixmap(make_icon("paste", "#60a5fa", 13))
    for _tb in (self.btn_clear, self.btn_paste):
        _tb.label.setStyleSheet(f"color: {TEXT}; font-size: 12px; background: transparent;")
        _tb.setStyleSheet(f"ToolButton {{ background: {CARD2}; border: 1px solid {BORDER}; border-radius: 10px; }} ToolButton:hover {{ border-color: #34406b; }}")
    top.addWidget(self.btn_clear)
    top.addWidget(self.btn_paste)
    cl.addLayout(top)

    # ---------- caja de texto con borde neon degradado ----------
    self._text_card = QFrame()
    self._text_card.setObjectName("textCard")
    self._text_card.setStyleSheet("QFrame#textCard { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #7c5cff, stop:0.5 #4c6ef5, stop:1 #38bdf8); border-radius: 14px; }")
    _tcl = QVBoxLayout(self._text_card)
    _tcl.setContentsMargins(1, 1, 1, 1)
    _tin = QFrame()
    _tin.setObjectName("textInner")
    _tin.setStyleSheet("QFrame#textInner { background: #0d1424; border-radius: 13px; }")
    _tiv = QVBoxLayout(_tin)
    _tiv.setContentsMargins(12, 8, 14, 4)
    _tiv.setSpacing(2)
    self.text_edit = QPlainTextEdit()
    self.text_edit.setPlaceholderText("Escribe aquí el texto que quieres convertir a voz...")
    self.text_edit.setFixedHeight(110)
    self.text_edit.setMinimumWidth(0)
    self.text_edit.setStyleSheet(f"QPlainTextEdit {{ background: transparent; color: {TEXT}; border: none; padding: 2px 0; font-size: 13px; selection-background-color: #3b82f6; }}")
    _tiv.addWidget(self.text_edit)
    _crow = QHBoxLayout()
    _crow.addStretch()
    self.counter_label = QLabel("0 / 5000")
    self.counter_label.setStyleSheet(f"color: {MUTED}; font-size: 10px; background: transparent;")
    _crow.addWidget(self.counter_label)
    _tiv.addLayout(_crow)
    _tcl.addWidget(_tin)
    cl.addWidget(self._text_card)

    # ---------- tarjetas Idioma / Voz seleccionada ----------
    sel = QHBoxLayout()
    sel.setSpacing(14)
    sel.setContentsMargins(0, 2, 0, 0)
    combo_qss = (
        f"QComboBox {{ background: #0a0d1f; color: {TEXT}; border: 1px solid"
        " #272c4c; border-radius: 9px; padding: 6px 12px;"
        " font-size: 12.5px; }"
        " QComboBox:hover { border: 1px solid #34406b; }"
        " QComboBox::drop-down { border: none; width: 28px; }"
        f" QComboBox QAbstractItemView {{ background: #10162a; color: {TEXT};"
        f" border: 1px solid {BORDER}; selection-background-color: {CARD2};"
        " padding: 6px; }"
    )
    _lc = QFrame()
    _lc.setObjectName("langCard")
    _lc.setFixedHeight(76)
    _lc.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    _lc.setStyleSheet("QFrame#langCard { background: #10122b; border: 1px solid rgba(139,92,246,85); border-radius: 12px; }")
    _lcv = QVBoxLayout(_lc)
    _lcv.setContentsMargins(12, 8, 12, 8)
    _lcv.setSpacing(6)
    _lh = QHBoxLayout()
    _lh.setSpacing(7)
    _lic2 = QLabel()
    _lic2.setPixmap(make_icon("globe", "#a78bfa", 14))
    _lh.addWidget(_lic2)
    l1 = QLabel("Idioma")
    l1.setStyleSheet(f"color: {TEXT}; font-size: 11.5px; font-weight: 600; background: transparent;")
    _lh.addWidget(l1)
    _lh.addStretch()
    _lcv.addLayout(_lh)
    self.lang_combo = _LangComboButton()
    self.lang_combo.addItems(["Multilingüe Premium", "Español (España)", "Inglés (EEUU)", "Ver todos los idiomas"])
    self.lang_combo.setItemIcon(0, QIcon(make_icon("crown", "#f5b544", 16)))
    self.lang_combo.setItemIcon(1, QIcon(self._flag_pixmap("es")))
    self.lang_combo.setItemIcon(2, QIcon(self._flag_pixmap("us")))
    self.lang_combo.setItemIcon(3, QIcon(make_icon("globe", "#a855f7", 16)))
    self.lang_combo.currentIndexChanged.connect(
        lambda _i: self._on_lang_changed())
    self.lang_combo.setCurrentIndex(0)
    self.lang_combo.setStyleSheet(combo_qss)
    self.lang_combo.setFixedHeight(36)
    self.lang_combo.setSizePolicy(
        QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    self.lang_combo.setMinimumWidth(0)
    _lcv.addWidget(self.lang_combo)
    sel.addWidget(_lc, 1)
    _vc = QFrame()
    _vc.setObjectName("voiceCard")
    _vc.setFixedHeight(76)
    _vc.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    _vc.setStyleSheet("QFrame#voiceCard { background: #10122b; border: 1px solid rgba(139,92,246,85); border-radius: 12px; }")
    _vcv = QVBoxLayout(_vc)
    _vcv.setContentsMargins(12, 8, 12, 8)
    _vcv.setSpacing(6)
    _vh2 = QHBoxLayout()
    _vh2.setSpacing(7)
    _vic3 = QLabel()
    _vic3.setPixmap(make_icon("wave", "#60a5fa", 14))
    _vh2.addWidget(_vic3)
    l2 = QLabel("Voz seleccionada")
    l2.setStyleSheet(f"color: {TEXT}; font-size: 11.5px; font-weight: 600; background: transparent;")
    _vh2.addWidget(l2)
    _vh2.addStretch()
    _vcv.addLayout(_vh2)
    self.voice_combo = QComboBox()
    self.voice_combo.setStyleSheet(
        combo_qss + " QComboBox { padding: 6px 80px 6px 12px; }"
    )
    self.pro_badge = QLabel("Pro", self.voice_combo)
    self.pro_badge.setStyleSheet(
        f"background: {PURPLE}; color: white; border-radius: 6px;"
        " font-size: 9px; font-weight: 700; padding: 3px 6px;"
    )
    self.pro_badge.setAttribute(
        Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    self.voice_combo.setFixedHeight(36)
    self.voice_combo.setSizePolicy(
        QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    self.voice_combo.setMinimumWidth(0)
    self.voice_combo.installEventFilter(self)
    for _cb in (self.lang_combo, self.voice_combo):
        _cb.setFixedHeight(36)
        _cb.setIconSize(QSize(16, 13))
        _cb.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    _vcv.addWidget(self.voice_combo)
    sel.addWidget(_vc, 1)
    self._lang_card = _lc
    self._lang_card_layout = _lcv
    self._voice_card = _vc
    self._voice_card_layout = _vcv
    self._lang_combo_ref = self.lang_combo
    self._voice_combo_ref = self.voice_combo
    cl.addLayout(sel)

    # ---------- Opciones avanzadas (tarjeta colapsable) ----------
    self.adv_button = AdvCard()
    cl.addWidget(self.adv_button)
    self.adv_widget = QWidget()
    self.adv_widget.setStyleSheet("background: transparent;")
    al = QHBoxLayout(self.adv_widget)
    al.setContentsMargins(2, 6, 2, 4)
    al.setSpacing(28)
    _mock_slider = """
    QSlider { background: transparent; }
    QSlider::groove:horizontal { height: 6px; border-radius: 3px;
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #7c5cff, stop:1 #38bdf8); }
    QSlider::sub-page:horizontal { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #7c5cff, stop:1 #38bdf8); border-radius: 3px; }
    QSlider::add-page:horizontal { background: #232f4b; border-radius: 3px; }
    QSlider::handle:horizontal { width: 14px; height: 14px; margin: -5px 0;
        border-radius: 7px; background: #ffffff; border: 3px solid rgba(124,92,255,160); }
    """
    _vcol = QVBoxLayout()
    _vcol.setSpacing(6)
    _vhead = QHBoxLayout()
    _vhead.setSpacing(8)
    _vico = QLabel()
    _vico.setPixmap(make_icon("bolt", "#a78bfa", 15))
    _vhead.addWidget(_vico)
    _vtitle = QLabel("Velocidad")
    _vtitle.setStyleSheet(f"color: {TEXT}; font-size: 13px; font-weight: 600; background: transparent;")
    _vhead.addWidget(_vtitle)
    _vhead.addStretch()
    _vcol.addLayout(_vhead)
    self.rate_slider = QSlider(Qt.Orientation.Horizontal)
    self.rate_slider.setRange(-10, 10)
    self.rate_slider.setStyleSheet(_mock_slider)
    _vcol.addWidget(self.rate_slider)
    _vsub = QHBoxLayout()
    _va = QLabel("Más lenta")
    _va.setStyleSheet(f"color: {MUTED}; font-size: 10.5px; background: transparent;")
    _vb = QLabel("Más rápida")
    _vb.setStyleSheet(f"color: {MUTED}; font-size: 10.5px; background: transparent;")
    _vsub.addWidget(_va)
    _vsub.addStretch()
    _vsub.addWidget(_vb)
    _vcol.addLayout(_vsub)
    al.addLayout(_vcol, 1)
    _ocol = QVBoxLayout()
    _ocol.setSpacing(6)
    _ohead = QHBoxLayout()
    _ohead.setSpacing(8)
    _oico = QLabel()
    _oico.setPixmap(make_icon("volume", "#a78bfa", 15))
    _ohead.addWidget(_oico)
    _otitle = QLabel("Volumen")
    _otitle.setStyleSheet(f"color: {TEXT}; font-size: 13px; font-weight: 600; background: transparent;")
    _ohead.addWidget(_otitle)
    _ohead.addStretch()
    _ocol.addLayout(_ohead)
    self.volume_slider = QSlider(Qt.Orientation.Horizontal)
    self.volume_slider.setRange(0, 100)
    self.volume_slider.setValue(100)
    self.volume_slider.setStyleSheet(_mock_slider)
    _ocol.addWidget(self.volume_slider)
    _osub = QHBoxLayout()
    _oa = QLabel("Bajo")
    _oa.setStyleSheet(f"color: {MUTED}; font-size: 10.5px; background: transparent;")
    _ob = QLabel("Alto")
    _ob.setStyleSheet(f"color: {MUTED}; font-size: 10.5px; background: transparent;")
    _osub.addWidget(_oa)
    _osub.addStretch()
    _osub.addWidget(_ob)
    _ocol.addLayout(_osub)
    al.addLayout(_ocol, 1)
    self.adv_widget.setVisible(False)
    cl.addWidget(self.adv_widget)
    p0.addWidget(card)
    acts = QHBoxLayout()
    acts.setSpacing(12)
    self.speak_button = ActionButton("play", "Reproducir", "#123a8c", "#2563eb")
    self.stop_button = ActionButton("stop", "Detener", "#6d1fa6", "#c026d3")
    self.export_button = ActionButton("download", "Exportar", "#0f766e", "#10b981")
    self.copy_button = SquareButton("copy", "Copiar texto")
    self.open_button = SquareButton("folder", "Abrir archivo")
    self.theme_button = SquareButton("moon", "Tema")
    acts.addWidget(self.speak_button, 1)
    acts.addWidget(self.stop_button, 1)
    acts.addWidget(self.export_button, 1)
    acts.addSpacing(12)
    acts.addWidget(self.copy_button)
    acts.addWidget(self.open_button)
    acts.addWidget(self.theme_button)

    for _ab in (self.speak_button, self.stop_button, self.export_button):
        _ab.setMinimumWidth(0)
    p0.addLayout(acts)
    self._add_neon(self.speak_button, BLUE)
    self._add_neon(self.stop_button, MAGENTA)
    self._add_neon(self.export_button, TEAL)

    player = QFrame()
    player.setFixedHeight(64)
    player.setMinimumWidth(0)
    player.setObjectName("playerBar")
    player.setStyleSheet(f"QFrame#playerBar {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 14px; }}")
    yl = QHBoxLayout(player)
    yl.setContentsMargins(12, 0, 14, 0)
    yl.setSpacing(10)
    self.player_play = SquareButton("play", "Reproducir")
    self.player_play.setFixedSize(40, 40)
    self.player_play.setStyleSheet(
        f"SquareButton {{ background: {CARD}; border: 1px solid {TEAL};"
        " border-radius: 20px; }"
        f"SquareButton:hover {{ background: {CARD2}; }}"
    )
    self.time_cur = QLabel("0:00")
    self.time_cur.setStyleSheet(f"color: {MUTED};")
    self.progress_slider = QSlider(Qt.Orientation.Horizontal)
    self.progress_slider.setRange(0, 100)
    if LIGHT_MODE:
        self.progress_slider.setStyleSheet(
            "QSlider { background: transparent; }"
            " QSlider::groove:horizontal { height: 6px; border-radius: 3px;"
            " background: #d5dcea; }"
            " QSlider::sub-page:horizontal { background: #3b82f6;"
            " border-radius: 3px; }"
            " QSlider::add-page:horizontal { background: #d5dcea;"
            " border-radius: 3px; }"
            " QSlider::handle:horizontal { width: 14px; height: 14px;"
            " margin: -5px 0; border-radius: 7px; background: #ffffff;"
            " border: 3px solid #3b82f6; }")
    self.time_tot = QLabel("0:00")
    self.time_tot.setStyleSheet(f"color: {MUTED};")
    vol_icon = IconLabel("volume", 14, MUTED)
    self.vol_slider = QSlider(Qt.Orientation.Horizontal)
    self.vol_slider.setRange(0, 100)
    self.vol_slider.setValue(100)
    self.vol_slider.setFixedWidth(110)
    yl.addWidget(self.player_play)
    yl.addWidget(self.time_cur)
    yl.addWidget(self.progress_slider, 1)
    yl.addWidget(self.time_tot)
    yl.addWidget(vol_icon)
    yl.addWidget(self.vol_slider)
    p0.addWidget(player)
    if LIGHT_MODE:
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
        from PySide6.QtGui import QColor as _QCsh
        _sh = QGraphicsDropShadowEffect(player)
        _sh.setBlurRadius(30)
        _sh.setOffset(0, 6)
        _sh.setColor(_QCsh(23, 32, 58, 45))
        player.setGraphicsEffect(_sh)
    self.pages.addWidget(page0)

    page1 = _HistPage()
    page1.setStyleSheet("background: transparent;")
    self._hist_page = page1
    self._hist_bg = QLabel(page1)
    self._hist_bg.setStyleSheet("background: transparent;")
    self._hist_bg.lower()
    h1 = QVBoxLayout(page1)
    h1.setContentsMargins(40, 36, 40, 28)
    h1.setSpacing(6)
    hh = QHBoxLayout()
    hh.setSpacing(14)
    hic = QLabel()
    hic.setPixmap(make_icon("history", "#a855f7", 34))
    hh.addWidget(hic)
    ht = QLabel("Historial")
    ht.setStyleSheet(f"color: {TEXT}; font-size: 26px; font-weight: 800;")
    hh.addWidget(ht)
    hh.addStretch(1)
    self.btn_hist_search = QPushButton(" Buscar")
    self.btn_hist_search.setIcon(QIcon(make_icon("search", "#c9d1d9", 14)))
    self.btn_hist_search.setCursor(Qt.CursorShape.PointingHandCursor)
    self.btn_hist_search.setStyleSheet(
        "QPushButton { color: #c9d1d9; font-weight: 600; font-size: 12px;"
        " background: #0d1220; border: 1px solid #262d3a; border-radius: 12px;"
        " padding: 9px 16px; } QPushButton:hover { border: 1px solid #7c5cff; }")
    hh.addWidget(self.btn_hist_search)
    self.btn_hist_filter = QPushButton(" Filtrar")
    self.btn_hist_filter.setIcon(QIcon(make_icon("filter", "#c9d1d9", 14)))
    self.btn_hist_filter.setCursor(Qt.CursorShape.PointingHandCursor)
    self.btn_hist_filter.setStyleSheet(
        "QPushButton { color: #c9d1d9; font-weight: 600; font-size: 12px;"
        " background: #0d1220; border: 1px solid #262d3a; border-radius: 12px;"
        " padding: 9px 16px; } QPushButton:hover { border: 1px solid #7c5cff; }")
    hh.addWidget(self.btn_hist_filter)
    h1.addLayout(hh)
    hsub = QLabel("Aqu\u00ed puedes ver todos tus textos y conversiones recientes.")
    hsub.setStyleSheet(f"color: {MUTED}; font-size: 13px;")
    h1.addWidget(hsub)
    h1.addSpacing(10)
    self.hsearch_row = QWidget()
    hsr = QHBoxLayout(self.hsearch_row)
    hsr.setContentsMargins(0, 0, 0, 0)
    self.hsearch_edit = QLineEdit()
    self.hsearch_edit.setPlaceholderText("Buscar en el historial...")
    self.hsearch_edit.setFixedHeight(42)
    self.hsearch_edit.setStyleSheet(
        "QLineEdit { background: #0d1220; border: 1px solid #262d3a;"
        " border-radius: 12px; color: #e6edf3; font-size: 13px;"
        " padding: 0 14px; }"
        " QLineEdit:focus { border: 1px solid #7c5cff; }")
    self.hsearch_edit.textChanged.connect(
        lambda s: (setattr(self, "_hsearch", s), self._load_history()))
    hsr.addWidget(self.hsearch_edit)
    self.hsearch_row.setVisible(False)
    h1.addWidget(self.hsearch_row)
    self.btn_hist_search.clicked.connect(
        lambda: (self.hsearch_row.setVisible(
            not self.hsearch_row.isVisible()),
            self.hsearch_edit.setFocus()
            if self.hsearch_row.isVisible() else None))

    def _open_hfilter():
        from PySide6.QtWidgets import QMenu
        from PySide6.QtCore import QPoint
        m = QMenu()
        m.setStyleSheet(
            "QMenu { background: #0d1220; border: 1px solid #262d3a;"
            " border-radius: 8px; padding: 6px; }"
            " QMenu::item { color: #c9d1d9; padding: 6px 18px; }"
            " QMenu::item:selected { background: rgba(124,92,255,40); }")
        for key, txt in (("todos", "Todos"), ("textos", "Textos manuales"),
                         ("archivos", "Archivos")):
            a = m.addAction(txt)
            a.triggered.connect(
                lambda _c, k=key: (setattr(self, "_hfilter", k),
                                   self._load_history()))
        m.exec(self.btn_hist_filter.mapToGlobal(
            QPoint(0, self.btn_hist_filter.height() + 4)))

    self.btn_hist_filter.clicked.connect(_open_hfilter)
    self.hist_scroll = QScrollArea()
    self.hist_scroll.setWidgetResizable(True)
    self.hist_scroll.setFrameShape(QFrame.Shape.NoFrame)
    self.hist_scroll.setHorizontalScrollBarPolicy(
        Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    self.hist_scroll.setStyleSheet(
        "QScrollArea { background: transparent; border: none; }")
    self.hist_container = QWidget()
    self.hist_container.setStyleSheet("background: transparent;")
    self.history_layout = QVBoxLayout(self.hist_container)
    self.history_layout.setContentsMargins(2, 2, 2, 2)
    self.history_layout.setSpacing(16)
    self.hist_scroll.setWidget(self.hist_container)
    self.btn_clear_hist = QPushButton(" Limpiar historial")
    self.btn_clear_hist.setIcon(QIcon(make_icon("trash", RED, 14)))
    self.btn_clear_hist.setCursor(Qt.CursorShape.PointingHandCursor)
    self.btn_clear_hist.setStyleSheet(
        "QPushButton { background: transparent; color: " + RED + ";"
        " border: 1px solid rgba(239,68,68,90); border-radius: 12px;"
        " font-weight: 600; font-size: 12px; padding: 9px 16px; }"
        " QPushButton:hover { background: rgba(239,68,68,25); }")
    h1.addWidget(self.hist_scroll, 1)
    h1.addWidget(self.btn_clear_hist, 0, Qt.AlignmentFlag.AlignLeft)
    self.pages.addWidget(page1)

    page2 = _VocPage()
    page2.setStyleSheet("background: transparent;")
    self._voc_page = page2
    self._voc_bg = QLabel(page2)
    self._voc_bg.setStyleSheet("background: transparent;")
    self._voc_bg.lower()
    v2 = QVBoxLayout(page2)
    v2.setContentsMargins(40, 36, 40, 28)
    v2.setSpacing(6)
    vh = QHBoxLayout()
    vh.setSpacing(12)
    vtt = QLabel('Solo <span style="color:#a855f7;">Premium</span>')
    vtt.setStyleSheet(f"color: {TEXT}; font-size: 26px; font-weight: 800;")
    vh.addWidget(vtt)
    self._voc_title = vtt
    vgem = QLabel()
    vgem.setPixmap(_chat_svg(_GEMV2, "#8b5cf6", 26))
    vh.addWidget(vgem)
    self._voc_gem = vgem
    vh.addStretch(1)
    self.vall_btn = QPushButton("  Ver todas")
    self.vall_btn.setIcon(QIcon(make_icon("globe", "#7cb7ff", 14)))
    self.vall_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    self.vall_btn.setStyleSheet(
        "QPushButton { color: #cfe3ff; font-weight: 700; font-size: 12px;"
        " background: rgba(124,92,255,10); border: 1.5px solid #8b5cf6;"
        " border-radius: 12px; padding: 9px 16px; }"
        " QPushButton:hover { background: rgba(124,92,255,25); }")
    self.vall_btn.clicked.connect(lambda: self._voc_toggle_all())
    vh.addWidget(self.vall_btn)
    v2.addLayout(vh)
    vsub = QLabel("Voces de alta calidad para proyectos profesionales.")
    vsub.setStyleSheet(f"color: {MUTED}; font-size: 13px;")
    v2.addWidget(vsub)
    self._voc_sub = vsub
    v2.addSpacing(14)
    vsr = QHBoxLayout()
    vsr.setSpacing(12)
    self.vsearch_edit = QLineEdit()
    self.vsearch_edit.setPlaceholderText("Buscar voces...")
    self.vsearch_edit.setFixedHeight(46)
    self.vsearch_edit.setStyleSheet(
        "QLineEdit { background: #0d1220; border: 1px solid #262d3a;"
        " border-radius: 12px; color: #e6edf3; font-size: 13px;"
        " padding: 0 16px; }"
        " QLineEdit:focus { border: 1px solid #7c5cff; }")
    self.vsearch_edit.textChanged.connect(
        lambda s: (setattr(self, "_vsearch", s.strip().lower()),
                   self._rebuild_voices_page()))
    vsr.addWidget(self.vsearch_edit, 1)
    vfil = QPushButton()
    vfil.setFixedSize(46, 46)
    vfil.setIcon(QIcon(make_icon("gear", "#c9d1d9", 16)))
    vfil.setStyleSheet(
        "QPushButton { background: transparent; border: 1.5px solid #7c5cff;"
        " border-radius: 12px; }"
        " QPushButton:hover { background: rgba(124,92,255,20); }")
    vsr.addWidget(vfil)
    v2.addLayout(vsr)
    v2.addSpacing(10)
    vtabs = QHBoxLayout()
    vtabs.setSpacing(8)
    for key, label, ik in (("todas", "Todas", None),
                           ("premium", "Premium", "crown"),
                           ("favoritas", "Favoritas", "heart")):
        b = QPushButton(label)
        if ik:
            b.setIcon(QIcon(make_icon(ik, "#f5b544" if ik == "crown" else "#ff4fd8", 14)))
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        setattr(self, "_vtab_btn_" + key, b)
        b.clicked.connect(lambda _c, k=key: self._voc_set_tab(k))
        vtabs.addWidget(b)
    vtabs.addStretch(1)
    v2.addLayout(vtabs)
    self._voc_set_tab("todas")
    vsep = QFrame()
    vsep.setFixedHeight(1)
    vsep.setStyleSheet("background: #262d3a;")
    v2.addWidget(vsep)
    v2.addSpacing(14)
    self.all_scroll = QScrollArea()
    self.all_scroll.setWidgetResizable(True)
    self.all_scroll.setFrameShape(QFrame.Shape.NoFrame)
    self.all_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    self.all_scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
    self.all_container = QWidget()
    self.all_container.setStyleSheet("background: transparent;")
    self.all_layout = QVBoxLayout(self.all_container)
    self.all_layout.setContentsMargins(2, 2, 2, 2)
    self.all_layout.setSpacing(18)
    self.all_scroll.setWidget(self.all_container)
    v2.addWidget(self.all_scroll, 1)
    self.pages.addWidget(page2)

    page3 = _FavPage()
    page3.setStyleSheet("background: transparent;")
    self._fav_page = page3
    self._fav_bg = QLabel(page3)
    self._fav_bg.setStyleSheet("background: transparent;")
    self._fav_bg.lower()
    f3 = QVBoxLayout(page3)
    f3.setContentsMargins(40, 36, 40, 28)
    f3.setSpacing(6)
    fh = QHBoxLayout()
    fh.setSpacing(16)
    fic = QLabel()
    fic.setPixmap(make_icon("heart", "#a855f7", 34))
    fh.addWidget(fic)
    ft = QLabel("Favoritos")
    ft.setStyleSheet(f"color: {TEXT}; font-size: 26px; font-weight: 800;")
    fh.addWidget(ft)
    fh.addStretch(1)
    f3.addLayout(fh)
    fsub = QLabel("Tus voces favoritos, siempre a mano.")
    fsub.setStyleSheet(f"color: {MUTED}; font-size: 13px;")
    f3.addWidget(fsub)
    f3.addSpacing(18)
    self.fav_scroll = QScrollArea()
    self.fav_scroll.setWidgetResizable(True)
    self.fav_scroll.setFrameShape(QFrame.Shape.NoFrame)
    self.fav_scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
    self.fav_container = QWidget()
    self.fav_container.setStyleSheet("background: transparent;")
    self.fav_layout = QVBoxLayout(self.fav_container)
    self.fav_layout.setContentsMargins(2, 2, 2, 2)
    self.fav_layout.setSpacing(20)
    self.fav_scroll.setWidget(self.fav_container)
    f3.addWidget(self.fav_scroll, 1)
    self.pages.addWidget(page3)

    page4 = QWidget()
    page4.setStyleSheet("background: transparent;")
    self._proj_page = page4
    page4.installEventFilter(self)
    pr4 = QVBoxLayout(page4)
    pr4.setContentsMargins(40, 36, 40, 28)
    pr4.setSpacing(14)

    self._proj_bg = QLabel(page4)
    self._proj_bg.setStyleSheet("background: transparent;")
    self._proj_bg.lower()

    ph = QHBoxLayout()
    ph.setSpacing(12)
    pi = QLabel()
    pi.setPixmap(make_icon("folder", "#bc8cff", 30))
    ph.addWidget(pi)
    pc = QVBoxLayout()
    pc.setSpacing(2)
    pt = QLabel("Proyectos")
    pt.setStyleSheet(f"color: {TEXT}; font-size: 20px; font-weight: 800;")
    ps = QLabel("Gestiona y organiza tus proyectos de voz.")
    ps.setStyleSheet(f"color: {MUTED}; font-size: 13px;")
    pc.addWidget(pt)
    pc.addWidget(ps)
    ph.addLayout(pc)
    ph.addStretch(1)
    self._proj_search = QLineEdit()
    self._proj_search.setPlaceholderText("Buscar proyectos...")
    self._proj_search.setFixedHeight(40)
    self._proj_search.setFixedWidth(280)
    self._proj_search.setStyleSheet(
        "QLineEdit { background: rgba(13,17,26,160);"
        " border: 1px solid #262d3a; border-radius: 10px;"
        " color: #e6edf3; font-size: 12.5px; padding: 0 14px 0 38px; }"
        " QLineEdit:focus { border: 1px solid #7c5cff; }")
    _lupa = QLabel(self._proj_search)
    _lupa.setPixmap(make_icon("search", "#8b93b0", 14))
    _lupa.setGeometry(12, 12, 16, 16)
    _lupa.setStyleSheet("background: transparent;")
    self._proj_search.textChanged.connect(
        lambda s: (setattr(self, "_psearch", s.strip().lower()),
                   self._rebuild_projects()))
    ph.addWidget(self._proj_search)
    btn_fil = QPushButton("  Filtrar")
    btn_fil.setIcon(QIcon(make_icon("filter", "#c9d1d9", 14)))
    btn_fil.setFixedHeight(40)
    btn_fil.setCursor(Qt.CursorShape.PointingHandCursor)
    btn_fil.setStyleSheet(
        "QPushButton { background: rgba(13,17,26,160); color: #c9d1d9;"
        " border: 1px solid #232f4b; border-radius: 10px;"
        " padding: 0 16px; font-size: 12.5px; font-weight: 600; }"
        " QPushButton:hover { border: 1px solid #7c5cff; }")
    btn_fil.clicked.connect(lambda: self._proj_open_filter(btn_fil))
    ph.addWidget(btn_fil)
    btn_new = QPushButton("  Nuevo proyecto")
    btn_new.setIcon(QIcon(make_icon("plus", "#ffffff", 14)))
    btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
    btn_new.setStyleSheet(
        "QPushButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
        " stop:0 #6d5df0, stop:1 #8b5cf6); color: white;"
        " border: none; border-radius: 10px; padding: 9px 16px;"
        " font-size: 12.5px; font-weight: 700; }"
        " QPushButton:hover { background: #9d70ff; }")
    btn_new.clicked.connect(lambda: self._switch_page(0))
    ph.addWidget(btn_new)
    pr4.addLayout(ph)

    stats_row = QHBoxLayout()
    stats_row.setSpacing(14)
    self._proj_stats = []
    from PySide6.QtWidgets import QProgressBar as _PBar
    for icon, label, sub, color in [
        ("folder", "Proyectos", "Total creados", "#a855f7"),
        ("wave", "Audio generado", "Tiempo total", "#2dd4bf"),
        ("mic", "Voces utilizadas", "En tus proyectos", "#f59e0b"),
        ("doc", "Espacio utilizado", "De 10 GB disponibles", "#3b82f6")]:
        card = QFrame()
        card.setObjectName("pstat")
        _r0 = int(color[1:3], 16)
        _g0 = int(color[3:5], 16)
        _b0 = int(color[5:7], 16)
        _tint = "rgba(%d,%d,%d,26)" % (_r0, _g0, _b0)
        _bord = "rgba(%d,%d,%d,51)" % (_r0, _g0, _b0)
        card.setStyleSheet(
            "#pstat { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            " stop:0 " + _tint + ", stop:1 rgba(13,17,26,140));"
            " border-radius: 14px; border: 1px solid " + _bord + "; }")
        ch = QHBoxLayout(card)
        ch.setContentsMargins(16, 14, 16, 14)
        ch.setSpacing(14)
        tile = QLabel()
        tile.setFixedSize(46, 46)
        tile.setPixmap(make_icon(icon, color, 20))
        tile.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tile.setStyleSheet(
            "background: rgba(255,255,255,6); border-radius: 12px;")
        ch.addWidget(tile)
        cv = QVBoxLayout()
        cv.setSpacing(2)
        vl = QLabel("0")
        vl.setStyleSheet(
            "color: #ffffff; font-size: 17px; font-weight: 800;")
        ll = QLabel(label)
        ll.setStyleSheet(
            "color: " + color + "; font-size: 11.5px; font-weight: 600;")
        sl = QLabel(sub)
        sl.setStyleSheet("color: #8b93b0; font-size: 10.5px;")
        if icon == "doc":
            try:
                import shutil
                _du = shutil.disk_usage(str(Path.home()))
                sl.setText("De %d GB disponibles"
                           % round(_du.total / (1024 ** 3)))
            except Exception:
                pass
        cv.addWidget(vl)
        cv.addWidget(ll)
        cv.addWidget(sl)
        if icon == "doc":
            pb = _PBar()
            pb.setRange(0, 100)
            pb.setValue(0)
            pb.setFixedHeight(5)
            pb.setTextVisible(False)
            pb.setStyleSheet(
                "QProgressBar { background: #232f4b; border-radius: 2px; }"
                " QProgressBar::chunk { background: #3b82f6;"
                " border-radius: 2px; }")
            cv.addSpacing(6)
            cv.addWidget(pb)
            self._proj_bar = pb
        ch.addLayout(cv, 1)
        stats_row.addWidget(card)
        self._proj_stats.append(vl)
    pr4.addLayout(stats_row)

    tr = QHBoxLayout()
    tr.setSpacing(22)
    self._proj_tab_group = []
    for nm, key in [("Todos", "todos"), ("Recientes", "recientes"),
                    ("Favoritos", "favoritos"), ("Archivados", "archivados")]:
        b = QPushButton(nm + " (0)")
        b.setCheckable(True)
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        b.setStyleSheet(
            "QPushButton { background: transparent; color: #8b93b0;"
            " border: none; border-bottom: 2px solid transparent;"
            " padding: 8px 2px; font-size: 13px; font-weight: 600; }"
            " QPushButton:checked { color: #c4b5fd;"
            " border-bottom: 2px solid #7c5cff; }"
            " QPushButton:hover { color: #c9d1d9; }")
        b.clicked.connect(
            lambda _=False, kk=key: self._set_proj_tab(kk))
        tr.addWidget(b)
        self._proj_tab_group.append((b, key))
    tr.addStretch(1)
    olbl = QLabel("Ordenar por:")
    olbl.setStyleSheet("color: #8b93b0; font-size: 12px;")
    tr.addWidget(olbl)
    self._proj_sort = QComboBox()
    self._proj_sort.addItems(["Más recientes", "Más antiguos",
                              "Nombre", "Duración"])
    self._proj_sort.setFixedHeight(36)
    self._proj_sort.setFixedWidth(150)
    self._proj_sort.setStyleSheet(
        "QComboBox { background: #0d1220; color: #e6edf3;"
        " border: 1px solid #232f4b; border-radius: 10px;"
        " padding: 0 10px; font-size: 12px; }")
    self._proj_sort.currentIndexChanged.connect(
        lambda: self._rebuild_projects())
    tr.addWidget(self._proj_sort)
    pr4.addLayout(tr)

    self._proj_scroll = QScrollArea()
    self._proj_scroll.setWidgetResizable(True)
    self._proj_scroll.setFrameShape(QFrame.Shape.NoFrame)
    self._proj_scroll.setStyleSheet(
        "QScrollArea { background: transparent; border: none; }"
        " QScrollBar:vertical { background: #10141f; width: 8px;"
        " border-radius: 4px; }"
        " QScrollBar::handle:vertical { background: #7c5cff;"
        " border-radius: 4px; min-height: 40px; }"
        " QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical"
        " { height: 0; }")
    self._proj_container = QWidget()
    self._proj_container.setStyleSheet("background: transparent;")
    self._proj_layout = QVBoxLayout(self._proj_container)
    self._proj_layout.setContentsMargins(2, 2, 2, 2)
    self._proj_layout.setSpacing(8)
    self._proj_scroll.setWidget(self._proj_container)
    pr4.addWidget(self._proj_scroll, 1)

    pg = QHBoxLayout()
    self._proj_info = QLabel("Mostrando 0 a 0 de 0 proyectos")
    self._proj_info.setStyleSheet("color: #8b93b0; font-size: 12px;")
    pg.addWidget(self._proj_info, 1)
    self._proj_prev = QPushButton("\u2039")
    self._proj_next = QPushButton("\u203a")
    for b in (self._proj_prev, self._proj_next):
        b.setFixedSize(36, 36)
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        b.setStyleSheet(
            "QPushButton { background: rgba(13,17,26,160); color: #8b93b0;"
            " border: 1px solid #232f4b; border-radius: 10px;"
            " font-size: 16px; font-weight: 700; }"
            " QPushButton:hover { border: 1px solid #7c5cff; }"
            " QPushButton:disabled { color: #333; }")
    self._proj_prev.clicked.connect(lambda: self._proj_page_go(-1))
    self._proj_next.clicked.connect(lambda: self._proj_page_go(1))
    self._proj_nums = QHBoxLayout()
    self._proj_nums.setSpacing(6)
    pg.addWidget(self._proj_prev)
    pg.addLayout(self._proj_nums)
    pg.addWidget(self._proj_next)
    pr4.addLayout(pg)

    self._proj_page_num = 0
    self._proj_items = []
    self.pages.addWidget(page4)

    # ---------- PAGINA 5: CHAT IA ----------
    page5 = QWidget()
    page5.setStyleSheet("background: transparent;")
    self._chat_page = page5
    page5.installEventFilter(self)
    p5 = QVBoxLayout(page5)
    p5.setContentsMargins(24, 20, 24, 20)
    p5.setSpacing(14)

    self._chat_bg = QLabel(page5)
    self._chat_bg.setStyleSheet("background: transparent;")
    self._chat_bg.lower()

    h5 = QHBoxLayout()
    h5.setSpacing(12)
    ico5 = QLabel()
    ico5.setPixmap(make_icon("sparkles", "#bc8cff", 30))
    h5.addWidget(ico5)
    tcol = QVBoxLayout()
    tcol.setSpacing(2)
    t5 = QLabel("Chat IA")
    t5.setStyleSheet(f"color: {TEXT}; font-size: 20px; font-weight: 800;")
    tcol.addWidget(t5)
    s5 = QLabel("Asistente inteligente de WillpoVoice")
    s5.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
    tcol.addWidget(s5)
    h5.addLayout(tcol)
    h5.addStretch(1)
    btn_config = QPushButton("  Configurar API Key")
    btn_config.setIcon(QIcon(make_icon("key", "#7cb7ff", 14)))
    btn_config.setCursor(Qt.CursorShape.PointingHandCursor)
    btn_config.setStyleSheet(
        "QPushButton { background: transparent; color: #cfe3ff;"
        " border: 1px solid #2f4c79; border-radius: 16px;"
        " padding: 7px 14px; font-size: 11.5px; font-weight: 600; }"
        " QPushButton:hover { background: rgba(88,166,255,25); }")
    btn_config.clicked.connect(self._configure_groq_key)
    h5.addWidget(btn_config)
    btn_help = QPushButton("  ?")
    btn_help.setIcon(QIcon(make_icon("help", "#7cb7ff", 14)))
    btn_help.setCursor(Qt.CursorShape.PointingHandCursor)
    btn_help.setStyleSheet(
        "QPushButton { background: transparent; color: #cfe3ff;"
        " border: 1px solid #2f4c79; border-radius: 16px;"
        " padding: 7px 14px; font-size: 11.5px; font-weight: 600; }"
        " QPushButton:hover { background: rgba(88,166,255,25); }")
    btn_help.clicked.connect(self._show_chat_tutorial)
    h5.addWidget(btn_help)
    p5.addLayout(h5)

    self._chat_banner = QFrame()
    self._chat_banner.setObjectName("groqCard")
    self._chat_banner.setStyleSheet(
        "#groqCard { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
        " stop:0 rgba(18,24,56,235), stop:1 rgba(30,16,60,235));"
        " border: 1px solid #3b4bd8; border-radius: 18px; }")
    bv = QVBoxLayout(self._chat_banner)
    bv.setContentsMargins(28, 26, 28, 26)
    bv.setSpacing(18)

    hdr = QHBoxLayout()
    hdr.setSpacing(18)
    orb = QLabel()
    orb.setFixedSize(72, 72)
    orb.setPixmap(make_icon("key", "#c4b5fd", 34))
    orb.setAlignment(Qt.AlignmentFlag.AlignCenter)
    orb.setStyleSheet(
        "background: rgba(124,92,255,40); border: 2px solid #7c5cff;"
        " border-radius: 36px;")
    hdr.addWidget(orb)
    tcol = QVBoxLayout()
    tcol.setSpacing(4)
    t1 = QLabel("Configura tu API Key")
    t1.setStyleSheet(
        "color: #ffffff; font-size: 22px; font-weight: 800; font-style: italic;")
    tcol.addWidget(t1)
    t2 = QLabel("Conecta tu API Key para desbloquear todo el poder "
                "del Chat IA de WillpoVoice.")
    t2.setStyleSheet("color: #a8b3cf; font-size: 12px;")
    tcol.addWidget(t2)
    hdr.addLayout(tcol)
    btn_del = QPushButton("  Eliminar API Key")
    btn_del.setIcon(QIcon(make_icon("trash", "#ff7b72", 13)))
    btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
    btn_del.setStyleSheet(
        "QPushButton { background: transparent; color: #ff7b72;"
        " border: 1px solid rgba(255,123,114,80); border-radius: 14px;"
        " padding: 6px 12px; font-size: 10.5px; font-weight: 600; }"
        " QPushButton:hover { background: rgba(255,123,114,25); }")
    btn_del.clicked.connect(self._delete_groq_key)
    hdr.addWidget(btn_del)
    hdr.addStretch(1)
    bv.addLayout(hdr)

    cards = QHBoxLayout()
    cards.setSpacing(16)
    for glyph, ctitle, cdesc in [
        ("shield", "Seguridad de tus datos",
         "Las conversaciones que tienes son privadas."),
        ("bolt", "Acceso Completo",
         "Disfruta de respuestas mas rapidas y precisas con Groq."),
    ]:
        fr = QFrame()
        fr.setObjectName("gcMini")
        fr.setStyleSheet(
            "#gcMini { background: rgba(13,18,40,160);"
            " border: 1px solid #2a3364; border-radius: 12px; }")
        fv = QHBoxLayout(fr)
        fv.setContentsMargins(16, 14, 16, 14)
        fv.setSpacing(12)
        ic = QLabel()
        ic.setFixedSize(44, 44)
        ic.setPixmap(make_icon(glyph, "#ffffff", 20))
        ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ic.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            " stop:0 #6d5df0, stop:1 #4527a0); border-radius: 22px;")
        fv.addWidget(ic)
        tx = QVBoxLayout()
        tx.setSpacing(3)
        a = QLabel(ctitle)
        a.setStyleSheet("color: #ffffff; font-size: 13px; font-weight: 700;")
        tx.addWidget(a)
        b = QLabel(cdesc)
        b.setStyleSheet("color: #93a0c2; font-size: 11px;")
        b.setWordWrap(True)
        tx.addWidget(b)
        fv.addLayout(tx)
        cards.addWidget(fr)
    bv.addLayout(cards)

    lbl = QLabel("Ingresa tu API Key")
    lbl.setStyleSheet("color: #e6edf3; font-size: 12px; font-weight: 700;")
    bv.addWidget(lbl)

    key_row = QFrame()
    key_row.setObjectName("gcInput")
    key_row.setStyleSheet(
        "#gcInput { background: rgba(10,14,32,200);"
        " border: 1px solid #2a3364; border-radius: 10px; }")
    kv = QHBoxLayout(key_row)
    kv.setContentsMargins(12, 4, 8, 4)
    kv.setSpacing(8)
    kic = QLabel()
    kic.setPixmap(make_icon("key", "#8b949e", 16))
    kv.addWidget(kic)
    self._groq_key_input = QLineEdit()
    self._groq_key_input.setFixedHeight(38)
    self._groq_key_input.setPlaceholderText(
        "gsk_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    self._groq_key_input.setEchoMode(QLineEdit.EchoMode.Password)
    self._groq_key_input.setStyleSheet(
        "QLineEdit { background: transparent; border: none;"
        " color: #e6edf3; font-size: 12.5px; }")
    self._groq_key_input.returnPressed.connect(self._save_groq_key)
    kv.addWidget(self._groq_key_input, 1)
    self._key_eye = QPushButton()
    self._key_eye.setFixedSize(32, 32)
    self._key_eye.setCursor(Qt.CursorShape.PointingHandCursor)
    self._key_eye.setStyleSheet(
        "QPushButton { background: transparent; border: none; }")
    self._key_eye.setIcon(QIcon(_chat_svg(_EYE_OFF, "#8b949e", 16)))
    self._key_eye.clicked.connect(self._toggle_key_vis)
    kv.addWidget(self._key_eye)
    bv.addWidget(key_row)

    hint = QLabel("Presiona Enter para conectar  ·  "
                  "Obtén tu clave gratis en console.groq.com "
                  "")
    hint.setStyleSheet("color: #93a0c2; font-size: 11px;")
    bv.addWidget(hint)

    bot = QHBoxLayout()
    bot.setSpacing(12)
    btn_get = QPushButton("  Obtener API Key gratis")
    btn_get.setIcon(QIcon(make_icon("key", "#ffffff", 16)))
    btn_get.setFixedHeight(44)
    btn_get.setCursor(Qt.CursorShape.PointingHandCursor)
    btn_get.setStyleSheet(
        "QPushButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
        " stop:0 #6d5df0, stop:1 #2f6bff); color: white; border: none;"
        " border-radius: 10px; padding: 0 22px; font-weight: 700;"
        " font-size: 12.5px; }"
        " QPushButton:hover { background: #7d6ffb; }")
    btn_get.clicked.connect(
        lambda: QDesktopServices.openUrl(QUrl("https://console.groq.com/keys")))
    bot.addWidget(btn_get)
    lock = QLabel()
    lock.setPixmap(make_icon("lock", "#8d75ff", 14))
    bot.addWidget(lock)
    priv = QLabel("Tú tienes el control absoluto: "
                  "")
    priv.setStyleSheet("color: #93a0c2; font-size: 11px;")
    bot.addWidget(priv)
    bot.addStretch(1)
    bv.addLayout(bot)

    p5.addWidget(self._chat_banner)
    from PySide6.QtCore import QSettings as _QSb
    if _QSb("WillpoVoice", "WillpoVoice").value("groq_api_key", ""):
        self._chat_banner.setVisible(False)

    self._chat_scroll = QScrollArea()
    self._chat_scroll.setWidgetResizable(True)
    self._chat_scroll.setStyleSheet(
        "QScrollArea { border: none; background: transparent; }")
    chat_widget = QWidget()
    chat_widget.setStyleSheet("background: transparent;")
    self._chat_layout = QVBoxLayout(chat_widget)
    self._chat_layout.setContentsMargins(0, 0, 0, 0)
    self._chat_layout.setSpacing(14)
    self._chat_layout.addStretch(1)
    self._chat_scroll.setWidget(chat_widget)
    self._chat_scroll.viewport().setStyleSheet("background: transparent;")
    p5.addWidget(self._chat_scroll, 1)

    bar = QFrame()
    bar.setObjectName("chatBar")
    bar.setStyleSheet(
        "#chatBar { background: #0d1220; border: 1px solid #263050;"
        " border-radius: 24px; }")
    bh = QHBoxLayout(bar)
    bh.setContentsMargins(8, 6, 8, 6)
    bh.setSpacing(8)
    orb = QLabel()
    orb.setFixedSize(40, 40)
    orb.setPixmap(make_icon("sparkles", "#bc8cff", 20))
    orb.setAlignment(Qt.AlignmentFlag.AlignCenter)
    orb.setStyleSheet(
        "border: 1.5px solid #6b3fa8; border-radius: 20px; background: transparent;")
    bh.addWidget(orb)
    self._chat_input = QLineEdit()
    self._chat_input.setFixedHeight(38)
    self._chat_input.setPlaceholderText("Escribe tu pregunta...")
    self._chat_input.setStyleSheet(
        "QLineEdit { background: transparent; border: none; color: #e6edf3;"
        " font-size: 13px; padding: 0 6px; }")
    self._chat_input.returnPressed.connect(self._send_chat_message)
    bh.addWidget(self._chat_input, 1)
    btn_send = QPushButton()
    btn_send.setFixedSize(40, 40)
    btn_send.setCursor(Qt.CursorShape.PointingHandCursor)
    btn_send.setIcon(QIcon(_chat_svg(
        "M2.01 21 23 12 2.01 3 2 10l15 2-15 2z", "#ffffff", 18)))
    btn_send.setStyleSheet(
        "QPushButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
        " stop:0 #8d75ff, stop:1 #6d5df0); border: none; border-radius: 12px; }"
        " QPushButton:hover { background: #9d87ff; }")
    btn_send.clicked.connect(self._send_chat_message)
    bh.addWidget(btn_send)
    p5.addWidget(bar)
    self._chat_send_btn = btn_send
    from PySide6.QtCore import QSettings as _QS
    _has_key = bool(_QS("WillpoVoice", "WillpoVoice").value("groq_api_key", ""))
    self._set_chat_locked(not _has_key)
    self._add_chat_bubble(
        "\u00a1Hola! \u00bfEn qu\u00e9 puedo ayudarte hoy?", is_user=False)
    self._show_chat_chips()

        # Marco semi-transparente alrededor de todo el Chat IA
    try:
        _old_l = page5.layout()
        _old_l.setContentsMargins(10, 10, 10, 10)
        _frame = QFrame(page5)
        _frame.setObjectName("chatFrame")
        _frame.setStyleSheet(
            "#chatFrame { border: 1.5px solid rgba(139,117,255,80);"
            " border-radius: 18px; background: rgba(12,16,28,120); }")
        _fl = QVBoxLayout(_frame)
        _fl.setContentsMargins(14, 14, 14, 14)
        _fl.setSpacing(10)
        while _old_l.count():
            _it = _old_l.takeAt(0)
            _w = _it.widget()
            if _w is not None:
                _fl.addWidget(_w)
            elif _it.layout() is not None:
                _fl.addLayout(_it.layout())
            else:
                _fl.addItem(_it)
        _old_l.addWidget(_frame)
        _sep = QFrame(_frame)
        _sep.setFixedHeight(1)
        _sep.setStyleSheet(
            "background: rgba(139,117,255,45); border: none;")
        _fl.insertWidget(1, _sep)
    except Exception as _exc:
        print("chatFrame:", _exc)
    self.pages.addWidget(page5)

    page6 = _AdjPage()
    page6.setStyleSheet("background: transparent;")
    self._adj_page = page6
    self._adj_bg = QLabel(page6)
    self._adj_bg.setStyleSheet("background: transparent;")
    self._adj_bg.lower()
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    scroll.setHorizontalScrollBarPolicy(
        Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    scroll.setStyleSheet(
        "QScrollArea { background: transparent; border: none; }")
    container = QWidget()
    container.setStyleSheet("background: transparent;")
    a5 = QVBoxLayout(container)
    a5.setContentsMargins(40, 36, 40, 28)
    a5.setSpacing(6)

    hh = QHBoxLayout()
    hh.setSpacing(14)
    hic = QLabel()
    hic.setPixmap(make_icon("gear", "#3b82f6", 40))
    hh.addWidget(hic)
    at5 = QLabel("Ajustes")
    at5.setStyleSheet("color: #ffffff; font-size: 26px; font-weight: 800;")
    hh.addWidget(at5)
    hh.addStretch(1)
    restore_btn = QPushButton(" Restaurar valores")
    restore_btn.setIcon(QIcon(make_icon("history", "#e6edf3", 14)))
    restore_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    restore_btn.setStyleSheet(
        "QPushButton { color: #e6edf3; font-weight: 600; font-size: 12px;"
        " background: rgba(13,18,32,180); border: 1px solid #3a4152;"
        " border-radius: 12px; padding: 9px 16px; }"
        " QPushButton:hover { border: 1px solid #7c5cff; }")

    def _restore_defaults():
        self.settings["char_limit"] = 5000
        self.settings["volume"] = 100
        self.settings["rate"] = 0
        self.settings["export_format"] = "mp3"
        self.settings["theme"] = "Oscuro"
        self.settings["animations"] = True
        self.settings["auto_play"] = True
        self.settings["auto_history"] = True
        self.settings["accent"] = "#7c5cff"
        self._rebuild_settings()
        self.statusBar().showMessage("Valores restaurados.")

    restore_btn.clicked.connect(_restore_defaults)
    hh.addWidget(restore_btn)
    a5.addLayout(hh)
    hsub = QLabel("Personaliza WillpoVoice seg\u00fan tus preferencias.")
    hsub.setStyleSheet("color: #8b949e; font-size: 13px;")
    a5.addWidget(hsub)
    a5.addSpacing(18)

    grid = QGridLayout()
    grid.setSpacing(18)
    grid.setColumnStretch(0, 1)
    grid.setColumnStretch(1, 1)
    grid.setColumnStretch(2, 1)

    # --- CARD 1: General ---
    c1 = _AdjCard("globe", "#3b82f6", "General")
    lang_cb = _adj_combo(
        ["Espa\u00f1ol", "English"],
        self.settings.get("lang_pref", "Espa\u00f1ol"),
        lambda v: self._on_lang_pref(v))
    c1.lay.addLayout(_adj_row("Idioma de la aplicaci\u00f3n", lang_cb))
    tema_lbl = QLabel("Tema")
    tema_lbl.setStyleSheet("color: #c9d1d9; font-size: 13px;")
    c1.lay.addWidget(tema_lbl)
    tema_row = QHBoxLayout()
    tema_row.setSpacing(8)
    self._tema_btns = {}

    def _set_tema(sel):
        self.settings["theme"] = sel
        try:
            want_light = False
            if sel == "Claro":
                want_light = True
                self.settings["dark_mode"] = False
            elif sel == "Sistema":
                from PySide6.QtGui import QGuiApplication
                want_light = QGuiApplication.styleHints().colorScheme().name == "Light"
                self.settings["dark_mode"] = not want_light
            else:
                self.settings["dark_mode"] = True
            if want_light != bool(globals().get("LIGHT_MODE", False)):
                from PySide6.QtWidgets import QMessageBox
                r = QMessageBox.question(
                    self, "Tema",
                    "El cambio de tema se aplica al reiniciar."
                    " \u00bfReiniciar ahora?")
                if r == QMessageBox.StandardButton.Yes:
                    self._restart_app()
            else:
                self._apply_theme()
        except Exception:
            pass
        for k, b in self._tema_btns.items():
            on = k == sel
            b.setStyleSheet(
                "QPushButton { color: " + ("#e6edf3" if on else "#8b949e") +
                "; font-size: 12px; font-weight: " + ("700" if on else "500") +
                "; background: " + ("rgba(37,99,235,18)" if on else "transparent") +
                "; border: 1px solid " + ("#2563eb" if on else "#262d3a") +
                "; border-radius: 10px; padding: 7px 14px; }"
                " QPushButton:hover { border: 1px solid #7c5cff; }")

    for k in ("Oscuro", "Claro", "Sistema"):
        b = QPushButton(k)
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        b.clicked.connect(lambda _c, kk=k: _set_tema(kk))
        self._tema_btns[k] = b
        tema_row.addWidget(b)
    tema_row.addStretch(1)
    c1.lay.addLayout(tema_row)
    _set_tema(self.settings.get("theme", "Oscuro"))
    sw_anim = _Switch(self.settings.get("animations", True))
    sw_anim.toggled.connect(lambda v: self.settings.__setitem__("animations", v))
    c1.lay.addLayout(_adj_row("Animaciones", sw_anim))
    sw_sug = _Switch(self.settings.get("suggestions", True))

    def _on_sug(v):
        self.settings["suggestions"] = v
        try:
            if v:
                if getattr(self, "_chat_chips_wrap", None) is None:
                    self._show_chat_chips()
                self.statusBar().showMessage(
                    "Sugerencias de IA activadas: m\u00edralas en Chat IA.")
            else:
                self._hide_chat_chips()
                self.statusBar().showMessage(
                    "Sugerencias de IA desactivadas.")
        except Exception:
            pass

    sw_sug.toggled.connect(_on_sug)
    c1.lay.addLayout(_adj_row("Mostrar sugerencias IA", sw_sug))
    c1.lay.addStretch(1)
    grid.addWidget(c1, 0, 0)

    # --- CARD 2: Conversion de voz ---
    c2 = _AdjCard("mic", "#c9d1d9", "Conversi\u00f3n de voz")
    self.limit_spin = QSpinBox()
    self.limit_spin.setRange(500, 20000)
    self.limit_spin.setSingleStep(500)
    self.limit_spin.setValue(
        min(int(self.settings.get("char_limit", 5000)),
            self._plan_char_limit()))
    self.limit_spin.setStyleSheet(
        "QSpinBox { background: #0d1220; color: #e6edf3;"
        " border: 1px solid #262d3a; border-radius: 8px;"
        " padding: 5px 10px; font-size: 12px; min-width: 90px; }"
        " QSpinBox::up-button, QSpinBox::down-button { width: 0; }")
    self.limit_spin.valueChanged.connect(
        lambda v: self.settings.__setitem__("char_limit", v))
    c2.lay.addLayout(_adj_row("L\u00edmite de caracteres", self.limit_spin))
    sw_count = _Switch(self.settings.get("show_counter", True))
    sw_count.toggled.connect(lambda v: self.settings.__setitem__("show_counter", v))
    c2.lay.addLayout(_adj_row("Mostrar contador de caracteres", sw_count))
    sw_auto = _Switch(self.settings.get("auto_play", True))
    sw_auto.toggled.connect(lambda v: self.settings.__setitem__("auto_play", v))
    c2.lay.addLayout(_adj_row("Reproducir autom\u00e1ticamente al generar", sw_auto))
    qual_cb = _adj_combo(
        ["Alta", "Media", "Baja"],
        self.settings.get("quality", "Alta"),
        lambda v: self.settings.__setitem__("quality", v))
    c2.lay.addLayout(_adj_row("Calidad de audio", qual_cb))
    fmt_cb = _adj_combo(
        ["MP3", "WAV"],
        self.settings.get("export_format", "mp3").upper(),
        lambda v: self.settings.__setitem__("export_format", v.lower()))
    c2.lay.addLayout(_adj_row("Formato de exportaci\u00f3n", fmt_cb))
    c2.lay.addStretch(1)
    grid.addWidget(c2, 0, 1)

    # --- CARD 3: Audio ---
    c3 = _AdjCard("volume", "#2dd4bf", "Audio")
    vol_w, self.vol_slider = _adj_slider(
        0, 100, int(self.settings.get("volume", 100)), "",
        lambda v: self.settings.__setitem__("volume", v))
    c3.lay.addLayout(_adj_row("Volumen predeterminado", vol_w))
    rate_w, self.rate_slider = _adj_slider(
        -10, 10, int(self.settings.get("rate", 0)), "",
        lambda v: self.settings.__setitem__("rate", v))
    c3.lay.addLayout(_adj_row("Velocidad predeterminada", rate_w))
    sw_prev = _Switch(self.settings.get("preview_export", True))
    sw_prev.toggled.connect(lambda v: self.settings.__setitem__("preview_export", v))
    c3.lay.addLayout(_adj_row("Vista previa antes de exportar", sw_prev))
    dev_cb = _adj_combo(
        ["Predeterminado del sistema"],
        "Predeterminado del sistema",
        lambda v: None)
    c3.lay.addLayout(_adj_row("Dispositivo de salida", dev_cb))
    c3.lay.addStretch(1)
    grid.addWidget(c3, 0, 2)

    # --- CARD 4: Apariencia ---
    c4 = _AdjCard("sparkles", "#f5b544", "Apariencia")
    ac_lbl = QLabel("Color de bordes")
    ac_lbl.setStyleSheet("color: #c9d1d9; font-size: 13px;")
    c4.lay.addWidget(ac_lbl)
    dots = _AccentDotGroup(
        ["#3b82f6", "#a855f7", "#2dd4bf", "personalizado"],
        self.settings.get("accent_sel", "#3b82f6"),
        names=["Azul", "Violeta", "Cyan", "Personalizado"],
        rainbow_last=True)
    dots.color_changed.connect(self._on_accent_changed)
    self._accent_dots = dots
    c4.lay.addWidget(dots)
    de_lbl = QLabel("Densidad de interfaz")
    de_lbl.setStyleSheet("color: #c9d1d9; font-size: 13px;")
    c4.lay.addWidget(de_lbl)
    dens_cb = _adj_combo(
        ["C\u00f3moda", "Compacta"],
        self.settings.get("density", "C\u00f3moda"),
        lambda v: self.settings.__setitem__("density", v))
    c4.lay.addWidget(dens_cb)
    c4.lay.addStretch(1)
    grid.addWidget(c4, 1, 0)

    # --- CARD 5: Archivos y almacenamiento ---
    c5 = _AdjCard("folder", "#f5b544", "Archivos y almacenamiento")
    cp_lbl = QLabel("Carpeta de exportaci\u00f3n")
    cp_lbl.setStyleSheet("color: #c9d1d9; font-size: 13px;")
    c5.lay.addWidget(cp_lbl)
    self.export_path_lbl = QLineEdit(
        str(self.settings.get("export_dir",
                              Path.home() / "WillpoVoice")))
    self.export_path_lbl.setReadOnly(True)
    self.export_path_lbl.setStyleSheet(
        "QLineEdit { background: #0d1220; color: #8b949e;"
        " border: 1px solid #262d3a; border-radius: 8px;"
        " padding: 6px 10px; font-size: 11px; }")
    exp_row = QHBoxLayout()
    exp_row.setSpacing(10)
    exp_row.addWidget(self.export_path_lbl, 1)
    chg_btn = QPushButton("Cambiar carpeta")
    chg_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    chg_btn.setStyleSheet(
        "QPushButton { background: #0d1220; color: #c9d1d9;"
        " border: 1px solid #262d3a; border-radius: 8px;"
        " padding: 6px 12px; font-size: 12px; }"
        " QPushButton:hover { border: 1px solid #7c5cff; }")

    def _pick_dir():
        from PySide6.QtWidgets import QFileDialog
        cur = str(self.settings.get("export_dir",
                                    Path.home() / "WillpoVoice"))
        d = QFileDialog.getExistingDirectory(
            self, "Carpeta de exportaci\u00f3n", cur)
        if d:
            self.settings["export_dir"] = d
            self.export_path_lbl.setText(d)

    chg_btn.clicked.connect(_pick_dir)
    exp_row.addWidget(chg_btn)
    c5.lay.addLayout(exp_row)
    sw_h = _Switch(self.settings.get("auto_history", True))
    sw_h.toggled.connect(lambda v: self.settings.__setitem__("auto_history", v))
    c5.lay.addLayout(_adj_row("Guardar autom\u00e1ticamente historial", sw_h))
    tmp_btn = QPushButton("Limpiar")
    tmp_btn.setIcon(QIcon(make_icon("trash", "#c9d1d9", 13)))
    tmp_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    tmp_btn.setStyleSheet(
        "QPushButton { background: #0d1220; color: #c9d1d9;"
        " border: 1px solid #262d3a; border-radius: 8px;"
        " padding: 6px 12px; font-size: 12px; }"
        " QPushButton:hover { border: 1px solid #ef4444; color: #ef4444; }")

    def _clean_tmp():
        import shutil, tempfile, os
        n = 0
        try:
            td = Path(tempfile.gettempdir())
            for f in td.glob("willpo*"):
                try:
                    if f.is_file():
                        f.unlink(); n += 1
                    elif f.is_dir():
                        shutil.rmtree(f, ignore_errors=True); n += 1
                except Exception:
                    pass
        except Exception:
            pass
        self.statusBar().showMessage(
            f"Archivos temporales limpiados ({n}).")

    tmp_btn.clicked.connect(_clean_tmp)
    c5.lay.addLayout(_adj_row("Limpiar archivos temporales", tmp_btn))
    c5.lay.addStretch(1)
    grid.addWidget(c5, 1, 1)

    # --- CARD 6: WillpoVoice Premium (gradiente) ---
    c6 = QFrame()
    c6.setObjectName("premcard")
    c6.setMinimumWidth(280)
    c6.setStyleSheet(
        "#premcard { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
        " stop:0 #4c1d95, stop:0.6 #6d28d9, stop:1 #8b5cf6);"
        " border: 1px solid rgba(139,92,246,120); border-radius: 14px; }"
        " #premcard QLabel { background: transparent; }")
    c6l = QVBoxLayout(c6)
    c6l.setContentsMargins(20, 18, 20, 18)
    c6l.setSpacing(8)
    ch6 = QHBoxLayout()
    ch6.setSpacing(10)
    ic6 = QLabel()
    ic6.setPixmap(make_icon("crown", "#f5b544", 26))
    ch6.addWidget(ic6)
    tt6 = QLabel("WillpoVoice Premium")
    tt6.setStyleSheet("color: #ffffff; font-size: 15px; font-weight: 700;")
    ch6.addWidget(tt6)
    self._c6_title = tt6
    ch6.addStretch(1)
    c6l.addLayout(ch6)
    c6l.addSpacing(6)
    pa = QLabel("Plan actual:")
    pa.setStyleSheet("color: #d8ccff; font-size: 12px;")
    c6l.addWidget(pa)
    try:
        det = license_manager.license_details()
        tier_lbl = det.get("tier", "") or "Plan Est\u00e1ndar"
        if tier_lbl and not tier_lbl.startswith("Plan"):
            tier_lbl = "Plan " + tier_lbl
    except Exception:
        tier_lbl = "Plan Est\u00e1ndar"
    plan_lbl = QLabel(tier_lbl)
    plan_lbl.setStyleSheet("color: #f5b544; font-size: 17px; font-weight: 800;")
    c6l.addWidget(plan_lbl)
    self._c6_plan = plan_lbl
    c6l.addSpacing(4)
    ta = QLabel("Caracteres por conversi\u00f3n:")
    ta.setStyleSheet("color: #d8ccff; font-size: 12px;")
    c6l.addWidget(ta)
    lim = self._plan_char_limit()
    ca = QLabel("Ilimitados" if lim >= 999999 else f"{lim:,} caracteres")
    ca.setStyleSheet("color: #f5b544; font-size: 15px; font-weight: 800;")
    c6l.addWidget(ca)
    self._c6_chars = ca
    c6l.addSpacing(8)
    ver_planes = QPushButton("  Ver planes")
    ver_planes.setIcon(QIcon(make_icon("sparkles", "#f5b544", 14)))
    ver_planes.setCursor(Qt.CursorShape.PointingHandCursor)
    ver_planes.setStyleSheet(
        "QPushButton { background: rgba(255,255,255,14); color: #ffffff;"
        " border: 1px solid rgba(255,255,255,60); border-radius: 10px;"
        " padding: 8px 14px; font-size: 12px; font-weight: 700; }"
        " QPushButton:hover { background: rgba(255,255,255,28); }")
    ver_planes.clicked.connect(lambda: self._open_plans())
    c6l.addWidget(ver_planes)
    c6l.addStretch(1)
    grid.addWidget(c6, 1, 2)
    for _cc in (c1, c2, c3, c4, c5, c6):
        _cc.setMinimumHeight(232)

    a5.addLayout(grid)
    a5.addSpacing(18)

    # --- CARD 7: Acerca de WillpoVoice (full width) ---
    c7 = _AdjCard("info", "#3b82f6", "Acerca de WillpoVoice")
    c7.setMaximumHeight(150)
    ar = QHBoxLayout()
    ar.setSpacing(24)
    vc = QVBoxLayout()
    vc.setSpacing(2)
    v1 = QLabel("Versi\u00f3n")
    v1.setStyleSheet("color: #8b949e; font-size: 12px;")
    v2 = QLabel(f"v{APP_VERSION}")
    v2.setStyleSheet("color: #e6edf3; font-size: 13px; font-weight: 600;")
    vc.addWidget(v1)
    vc.addWidget(v2)
    ar.addLayout(vc)
    mc = QVBoxLayout()
    mc.setSpacing(2)
    m1 = QLabel("Motor de voz")
    m1.setStyleSheet("color: #8b949e; font-size: 12px;")
    m2 = QLabel("WillpoVoice TTS Engine")
    m2.setStyleSheet("color: #e6edf3; font-size: 13px; font-weight: 600;")
    mc.addWidget(m1)
    mc.addWidget(m2)
    ar.addLayout(mc)
    ar.addStretch(1)
    upd_btn = QPushButton("  Buscar actualizaciones")
    upd_btn.setIcon(QIcon(make_icon("download", "#c9d1d9", 14)))
    upd_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    upd_btn.setStyleSheet(
        "QPushButton { background: #0d1220; color: #c9d1d9;"
        " border: 1px solid #262d3a; border-radius: 10px;"
        " padding: 8px 14px; font-size: 12px; }"
        " QPushButton:hover { border: 1px solid #7c5cff; }")

    def _check_upd():
        fn = getattr(self, "_check_for_updates", None)
        if callable(fn):
            try:
                fn()
                return
            except Exception:
                pass
        self.statusBar().showMessage(
            "Buscando actualizaciones en GitHub...")

    upd_btn.clicked.connect(_check_upd)
    ar.addWidget(upd_btn)
    lic_btn = QPushButton("  Ver licencia")
    lic_btn.setIcon(QIcon(make_icon("doc", "#c9d1d9", 14)))
    lic_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    lic_btn.setStyleSheet(
        "QPushButton { background: #0d1220; color: #c9d1d9;"
        " border: 1px solid #262d3a; border-radius: 10px;"
        " padding: 8px 14px; font-size: 12px; }"
        " QPushButton:hover { border: 1px solid #7c5cff; }")
    lic_btn.clicked.connect(lambda: self._open_license_dialog())
    ar.addWidget(lic_btn)
    c7.lay.addLayout(ar)
    a5.addWidget(c7)
    a5.addStretch(1)
    scroll.setWidget(container)
    outer = QVBoxLayout(page6)
    outer.setContentsMargins(0, 0, 0, 0)
    outer.addWidget(scroll)
    self.pages.addWidget(page6)

    # Pagina 7: Clonacion de Voz
    from ui.clone_voice_page import CloneVoicePage
    page7 = CloneVoicePage()
    page7.setStyleSheet("background: transparent;")
    self._clone_page = page7
    self.pages.addWidget(page7)

    # ---------- PANEL DERECHO ----------
    self.right_panel = QFrame()
    self.right_panel.setObjectName("rightPanel")
    self.right_panel.setStyleSheet(f"QFrame#rightPanel {{ background: {BG}; border-left: 1px solid {BORDER}; }}")
    self.right_panel.setMinimumWidth(320)
    self.right_panel.setMaximumWidth(380)
    rp = QVBoxLayout(self.right_panel)
    rp.setContentsMargins(14, 14, 14, 14)
    rp.setSpacing(10)
    rh = QHBoxLayout()
    self._panel_title = QLabel('Solo <span style="color:#a855f7;">Premium</span>')
    rt = self._panel_title
    rt.setStyleSheet(f"color: {TEXT}; font-size: 13px; font-weight: 700;")
    self.btn_ver_all = ToolButton("globe", "Ver todas")
    self.btn_ver_all.setStyleSheet(
        f"ToolButton {{ background: transparent; border: 1px solid {BORDER};"
        f" border-radius: 8px; }} ToolButton:hover {{ background: {CARD2}; }}"
    )
    rh.addWidget(rt)
    rh.addStretch()
    rh.addWidget(self.btn_ver_all)
    rp.addLayout(rh)
    search_row = QHBoxLayout()
    search_box = QFrame()
    search_box.setObjectName("searchBox")
    search_box.setStyleSheet(
        f"QFrame#searchBox {{ background: {CARD}; border: 1px solid"
        f" {BORDER}; border-radius: 10px; }}"
    )
    sbl = QHBoxLayout(search_box)
    sbl.setContentsMargins(10, 0, 10, 0)
    sbl.setSpacing(8)
    sbl.addWidget(IconLabel("search", 13, MUTED))
    self.search_edit = QLineEdit()
    self.search_edit.setPlaceholderText("Buscar voces...")
    self.search_edit.setStyleSheet(
        "QLineEdit { background: transparent; border: none; padding: 8px 0px; }"
    )
    sbl.addWidget(self.search_edit)
    self.filter_btn = SquareButton("filter", "Filtro")
    self.filter_btn.setFixedSize(40, 40)
    search_row.addWidget(search_box, 1)
    search_row.addWidget(self.filter_btn)
    self.filter_btn.clicked.connect(self._open_filter_menu)
    rp.addLayout(search_row)
    tabs = QHBoxLayout()
    tabs.setSpacing(4)
    self.rtab_all = TabButton("Todas")
    self.rtab_pro = TabButton("Premium")
    self.rtab_fav = TabButton("Favoritas")
    self.rtab_all.setIcon(QIcon(make_icon("grid", "#7cb7ff", 14)))
    self.rtab_all.setIconSize(QSize(14, 14))
    self.rtab_pro.setIcon(QIcon(make_icon("crown", "#f5b544", 14)))
    self.rtab_pro.setIconSize(QSize(14, 14))
    self.rtab_fav.setIcon(QIcon(make_icon("heart", "#ff4fd8", 14)))
    self.rtab_fav.setIconSize(QSize(14, 14))
    self.rtab_all.set_active(True)
    tabs.addWidget(self.rtab_all)
    tabs.addWidget(self.rtab_pro)
    tabs.addWidget(self.rtab_fav)
    tabs.addStretch()
    rp.addLayout(tabs)
    self.cards_scroll = QScrollArea()
    self.cards_scroll.setWidgetResizable(True)
    self.cards_scroll.setFrameShape(QFrame.Shape.NoFrame)
    self.cards_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    self.cards_scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
    self.cards_container = QWidget()
    self.cards_container.setStyleSheet("background: transparent;")
    self.voice_cards_layout = QVBoxLayout(self.cards_container)
    self.voice_cards_layout.setContentsMargins(0, 0, 4, 0)
    self.voice_cards_layout.setSpacing(8)
    self.cards_scroll.setWidget(self.cards_container)
    rp.addWidget(self.cards_scroll, 1)
    root.addWidget(self.right_panel)

    self.player = QMediaPlayer(self)
    self.audio_out = QAudioOutput(self)
    self.player.setAudioOutput(self.audio_out)
    self.audio_out.setVolume(1.0)
    self._synth_worker = None
    self._media_ready = False
    self.player_timer = QTimer(self)
    self.player_timer.timeout.connect(self._tick_player)
    # self.player.positionChanged.connect(self._on_position_changed)
    # self.player.durationChanged.connect(self._on_duration_changed)
    # self.player.mediaStatusChanged.connect(self._on_media_status_changed)
    self.progress_slider.sliderPressed.connect(self._on_slider_pressed)
    self.progress_slider.sliderReleased.connect(self._on_slider_released)
    self.vol_slider.valueChanged.connect(self._on_volume_changed)
    self._seconds = 0
    self._switch_page(0)


class SynthWorker(QThread):
    ready = Signal(str)
    error = Signal(str)

    def __init__(self, engine, text, voice, rate, volume):
        super().__init__()
        self.engine = engine
        self.text = text
        self.voice = voice
        self.rate = rate
        self.volume = volume

    def run(self):
        try:
            import tempfile
            from pathlib import Path as _P
            import pythoncom
            import win32com.client
            pythoncom.CoInitialize()
            from core.text_normalizer import (
                needs_homograph_guard,
                normalize_for_tts,
            )
            texto = normalize_for_tts(
                self.text,
                guard=needs_homograph_guard(self.voice or ""),
            )
            tmp = str(_P(tempfile.gettempdir()) / "willpovoice_player.wav")
            adapter = self.engine.adapter
            if self.voice:
                try:
                    adapter.set_voice(self.voice)
                except Exception:
                    first = str(self.voice).split()[0].lower()
                    try:
                        for token in adapter.sapi.GetVoices():
                            if first in token.GetDescription().lower():
                                adapter.sapi.Voice = token
                                break
                    except Exception:
                        pass
            adapter.set_rate(self.rate)
            adapter.set_volume(self.volume)
            sapi = adapter.sapi
            stream = win32com.client.Dispatch("SAPI.SpFileStream")
            stream.Open(tmp, 3, False)
            sapi.AudioOutputStream = stream
            sapi.Speak(texto)
            stream.Close()
            sapi.AudioOutputStream = None
            self.ready.emit(tmp)
        except Exception as exc:
            self.error.emit(str(exc))


def _connect_signals(self):
    self.speak_button.clicked.connect(self.speak_text)
    self.player_play.clicked.connect(self._player_play_clicked)
    self.stop_button.clicked.connect(self._player_play_clicked)
    self.export_button.clicked.connect(self._show_export_menu)
    self.copy_button.clicked.connect(self._copy_text)
    self.open_button.clicked.connect(self._open_document_dialog)
    self.theme_button.clicked.connect(self._quick_toggle_theme)
    self.btn_clear.clicked.connect(lambda: self.text_edit.clear())
    self.btn_paste.clicked.connect(lambda: self.text_edit.paste())
    self.btn_clear_hist.clicked.connect(self.clear_history)
    self.text_edit.textChanged.connect(self._on_text_limited)
    self.text_edit.textChanged.connect(self._auto_text_height)
    self.voice_combo.currentIndexChanged.connect(lambda _i: self._on_combo_voice())
    self.search_edit.textChanged.connect(lambda _t: self._rebuild_cards())
    self.rtab_all.clicked.connect(lambda: self._set_rtab("todas"))
    self.rtab_pro.clicked.connect(lambda: self._set_rtab("premium"))
    self.rtab_fav.clicked.connect(lambda: self._set_rtab("favoritas"))
    self.btn_ver_all.clicked.connect(lambda: self._switch_page(2))
    self.adv_button.clicked.connect(self._toggle_adv)
    self.vol_slider.valueChanged.connect(lambda v: self.engine.set_volume(v))
    self.volume_slider.valueChanged.connect(lambda v: self.engine.set_volume(v))
    def _check_limit(v):
        plan_limit = self._plan_char_limit()
        if v > plan_limit:
            self.limit_spin.blockSignals(True)
            self.limit_spin.setValue(plan_limit)
            self.limit_spin.blockSignals(False)
            self._show_limit_hint()
        else:
            self.settings["char_limit"] = v
        self.update_counter()
    self.limit_spin.valueChanged.connect(_check_limit)
    self.limit_spin.setMaximum(999999)


def _switch_page(self, index):
    if index == 7:
        _tier = ""
        try:
            _det = license_manager.license_details()
            if _det.get("state") == "licensed":
                _tier = _det.get("tier", "")
        except Exception:
            _tier = ""
        if _tier not in ("Platinum",):
            from PySide6.QtWidgets import QMessageBox as _QMB
            _m = _QMB(self)
            _m.setWindowTitle("Función Platinum")
            _m.setIcon(_QMB.Icon.Information)
            _m.setText("La Clonación de Voz está disponible solo para el plan Platinum.")
            _m.setInformativeText("Actualiza tu plan para desbloquear esta función.")
            _m.setStandardButtons(_QMB.StandardButton.Ok)
            _m.exec()
            return
    self.pages.setCurrentIndex(index)
    if index == 5:
        self._layout_chat_bg()
    for i, (btn, _pg) in enumerate(self._nav):
        btn.set_active(i == index)
    self.right_panel.setVisible(index == 0)
    if index == 7:
        self.right_panel.setVisible(False)
    if index == 2 and not getattr(self, "_all_built", False):
        self._all_built = True
        self._rebuild_all_page()
    if index == 2:
        self._voc_built = True
        self._rebuild_voices_page()
    if index == 3 and not getattr(self, "_fav_built", False):
        self._fav_built = True
        self._rebuild_fav_page()


def _toggle_sidebar(self):
    collapsed = self.sidebar.width() > 100
    self.sidebar.setFixedWidth(72 if collapsed else 232)
    sb_lay = self.sidebar.layout()
    if collapsed:
        sb_lay.setContentsMargins(10, 14, 10, 14)
        sb_lay.setAlignment(
            self.hamburger, Qt.AlignmentFlag.AlignHCenter)
    else:
        sb_lay.setContentsMargins(14, 14, 14, 14)
        sb_lay.setAlignment(
            self.hamburger, Qt.AlignmentFlag.AlignLeft)
    for btn, _pg in self._nav:
        btn.set_collapsed(collapsed)
    self._logo_name.setVisible(not collapsed)
    self._logo_ver.setVisible(not collapsed)
    self._prem_card.setVisible(not collapsed)


def _set_rtab(self, tab):
    self._rtab = tab
    self.rtab_all.set_active(tab == "todas")
    self.rtab_pro.set_active(tab == "premium")
    self.rtab_fav.set_active(tab == "favoritas")
    self._rebuild_cards()


def _clear_layout(self, layout):
    while layout.count():
        item = layout.takeAt(0)
        w = item.widget() if item else None
        if w is not None:
            w.deleteLater()


def _favorites(self):
    return set(self.settings.get("favorites", []))


def _make_card(self, name, layout):
    premium = self._is_premium(name)
    favs = self._favorites()
    card = VoiceCardV2(self, name, premium,
                       name == getattr(self, "_selected_voice", ""),
                       name in favs, compact=True)
    from PySide6.QtWidgets import QSizePolicy
    card.setSizePolicy(QSizePolicy.Policy.Expanding,
                       QSizePolicy.Policy.Fixed)
    card.clicked.connect(lambda n=name: self._select_voice(n))
    card.fav_toggled.connect(lambda n=name: self._toggle_fav(n))
    card.preview_toggled.connect(lambda n=name: self._toggle_preview(n))
    layout.addWidget(card)
    # Índice para localizar tarjetas por nombre (spinner de preview)
    if not hasattr(self, "_cards_by_name"):
        self._cards_by_name = {}
    self._cards_by_name[name] = card


def _voice_lang(self, name):
    low = name.lower()
    if "multilingual" in low:
        return "multi"
    if "spanish" in low or "espa" in low or "es-" in low or "(es)" in low:
        return "es"
    if "english" in low or "ingl" in low or "en-" in low or "(en)" in low:
        return "en"
    return "otro"


def _lang_filtered(self, names):
    lang = self.lang_combo.currentText()
    extra = getattr(self, "_extra_filter", None)
    out = []
    for name in names:
        vl = self._voice_lang(name)
        if extra in (None, "premium"):
            if lang.startswith("Espa") and vl != "es":
                continue
            if lang.startswith("Ingl") and vl != "en":
                continue
            if lang.startswith("Multiling") and not self._is_premium(name):
                continue
        if extra == "premium" and not self._is_premium(name):
            continue
        if extra not in (None, "premium") and \
                self._voice_lang2(name) != extra:
            continue
        out.append(name)
    out.sort(key=self._sort_key)
    return out


def _refill_combo(self):
    if not hasattr(self, "voice_combo"):
        return
    cur = self.voice_combo.currentData(Qt.ItemDataRole.UserRole)
    names = self._lang_filtered(getattr(self, "_voices", []))
    self.voice_combo.blockSignals(True)
    self.voice_combo.clear()
    for v in names:
        self.voice_combo.addItem(self._display_voice_name(v))
        idx = self.voice_combo.count() - 1
        self.voice_combo.setItemData(idx, v, Qt.ItemDataRole.UserRole)
    self.voice_combo.blockSignals(False)
    if cur in names:
        self.voice_combo.setCurrentIndex(names.index(cur))
    elif names:
        self.voice_combo.setCurrentIndex(0)
    self._icon_queue = list(range(self.voice_combo.count()))
    if hasattr(self, "_icon_timer"):
        self._icon_timer.start(60)


def _repair_engine(self):
    import sys, os
    if getattr(self, "_repair_tried", False):
        return
    base = os.path.dirname(sys.executable) if getattr(
        sys, "frozen", False) else os.getcwd()
    dll = os.path.join(base, "engine", "x64",
                       "NaturalVoiceSAPIAdapter.dll")
    if not os.path.exists(dll):
        return
    self._repair_tried = True
    import ctypes
    ret = ctypes.windll.shell32.ShellExecuteW(
        None, "runas", "regsvr32.exe",
        '/s "' + dll + '"', None, 0)
    if ret > 32:
        from PySide6.QtCore import QTimer
        self.statusBar().showMessage("Reparando motor de voces...")
        QTimer.singleShot(5000, self._load_voices)


def _on_lang_changed(self):
    idx = self.lang_combo.currentIndex()
    txt = self.lang_combo.currentText()
    if idx == 3 and txt.startswith("Ver todos"):
        self.lang_combo.blockSignals(True)
        self.lang_combo.setCurrentIndex(getattr(self, "_lang_prev", 0))
        self.lang_combo.blockSignals(False)
        self._open_lang_dialog()
        return
    self._lang_prev = idx
    code = next((it[0] for it in LANG_TABLE if it[1] == txt), None)
    self._extra_filter = code if code else None
    self._refill_combo()
    self._rebuild_cards()


def _rebuild_cards(self):
    self._clear_layout(self.voice_cards_layout)
    q = self.search_edit.text().strip().lower()
    self._rec_names = []
    for name in sorted(getattr(self, "_voices", []), key=self._sort_key):
        premium = self._is_premium(name)
        if getattr(self, "_rtab", "todas") == "premium" and not premium:
            continue
        if getattr(self, "_rtab", "todas") == "favoritas" and name not in self._favorites():
            continue
        extra = getattr(self, "_extra_filter", None)
        if extra == "premium" and not premium:
            continue
        if extra not in (None, "premium") and \
                self._voice_lang2(name) != extra:
            continue
        if q and q not in name.lower():
            continue
        if extra in (None, "premium"):
            vl = self._voice_lang(name)
            lang = self.lang_combo.currentText()
            if lang.startswith("Espa") and vl != "es":
                continue
            if lang.startswith("Ingl") and vl != "en":
                continue
        self._rec_names.append(name)
    self._rec_names.sort(
        key=lambda n: (0 if self._is_premium(n) else 1))
    self._rec_shown = 0
    self._rec_more_btn = None
    self._append_rec_cards()
    self.voice_cards_layout.addStretch(1)


def _append_rec_cards(self):
    lay = self.voice_cards_layout
    if lay.count():
        last = lay.itemAt(lay.count() - 1)
        if last is not None and last.spacerItem() is not None:
            lay.takeAt(lay.count() - 1)
    btn = getattr(self, "_rec_more_btn", None)
    if btn is not None:
        self.voice_cards_layout.removeWidget(btn)
        btn.deleteLater()
        self._rec_more_btn = None
    chunk = self._rec_names[self._rec_shown:self._rec_shown + 12]
    for name in chunk:
        self._make_card(name, self.voice_cards_layout)
    self._rec_shown += len(chunk)
    if self._rec_shown < len(self._rec_names):
        more = QPushButton(
            f"Mostrar mas voces ({len(self._rec_names) - self._rec_shown})")
        more.setCursor(Qt.CursorShape.PointingHandCursor)
        more.setStyleSheet(
            "QPushButton { background: transparent; color: " + MUTED + ";"
            " border: 1px dashed " + BORDER + "; border-radius: 10px;"
            f" padding: 8px; }} QPushButton:hover {{ color: {TEXT}; }}"
        )
        more.clicked.connect(self._append_rec_cards)
        self._rec_more_btn = more
        self.voice_cards_layout.addWidget(more)


def _rebuild_all_page(self):
    self._all_built = True
    self._clear_layout(self.all_layout)
    self._all_names = self._lang_filtered(
        list(getattr(self, "_voices", [])))
    self._all_shown = 0
    self._all_more_btn = None
    self._append_all_cards()
    self.all_layout.addStretch(1)


def _append_all_cards(self):
    lay = self.all_layout
    if lay.count():
        last = lay.itemAt(lay.count() - 1)
        if last is not None and last.spacerItem() is not None:
            lay.takeAt(lay.count() - 1)
    btn = getattr(self, "_all_more_btn", None)
    if btn is not None:
        self.all_layout.removeWidget(btn)
        btn.deleteLater()
        self._all_more_btn = None
    chunk = self._all_names[self._all_shown:self._all_shown + 60]
    for name in chunk:
        self._make_card(name, self.all_layout)
    self._all_shown += len(chunk)
    if self._all_shown < len(self._all_names):
        more = QPushButton(
            f"Mostrar mas voces ({len(self._all_names) - self._all_shown})")
        more.setCursor(Qt.CursorShape.PointingHandCursor)
        more.setStyleSheet(
            "QPushButton { background: transparent; color: " + MUTED + ";"
            " border: 1px dashed " + BORDER + "; border-radius: 10px;"
            f" padding: 8px; }} QPushButton:hover {{ color: {TEXT}; }}"
        )
        more.clicked.connect(self._append_all_cards)
        self._all_more_btn = more
        self.all_layout.addWidget(more)


def _rebuild_fav_page(self):
    self._fav_built = True
    self._clear_layout(self.fav_layout)
    added = 0
    for name in sorted(getattr(self, "_voices", []), key=self._sort_key):
        if name in self._favorites():
            card = VoiceCardV2(self, name, self._is_premium(name),
                               name == getattr(self, "_selected_voice", ""),
                               True)
            card.clicked.connect(lambda n=name: self._select_voice(n))
            card.fav_toggled.connect(lambda n=name: self._toggle_fav(n))
            card.preview_toggled.connect(lambda n=name: self._toggle_preview(n))
            self.fav_layout.addWidget(card)
            added += 1
    if not added:
        empty = QLabel("A\u00fan no tienes voces favoritas.\n"
                       "Toca el coraz\u00f3n de cualquier voz para guardarla aqu\u00ed.")
        empty.setStyleSheet("color: #8b949e; font-size: 13px; padding: 40px;")
        empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty.setWordWrap(True)
        self.fav_layout.addWidget(empty)
    self.fav_layout.addStretch()


def _load_voices(self):
    try:
        self.engine.refresh_voices()
        voices = self.engine.get_available_voices()
        voices.sort(key=lambda n: (not self._is_premium(n), n.lower()))
        lowered = [v.lower() for v in voices]
        multi_persons = {
            k for k in PREMIUM_PHOTOS
            if any(k in n and "multilingual" in n for n in lowered)
        }
        dedup = []
        for v in voices:
            low = v.lower()
            person = next((k for k in PREMIUM_PHOTOS if k in low), None)
            if person in multi_persons and "multilingual" not in low:
                continue
            dedup.append(v)
        voices = dedup
        self._voices = voices
        # Inyectar voces clonadas (Alfredo, etc.)
        try:
            from core.pocket_cloner import cloner_instance
            _cloned = cloner_instance.list_saved_voices()
            self._cloned_set = set(_cloned)
            self._voices = [v for v in self._voices if v not in self._cloned_set] + list(_cloned)
        except Exception as _e:
            print("No se pudieron inyectar voces clonadas: " + str(_e))
            self._cloned_set = set()
        if not any(self._is_premium(v) for v in voices):
            self._repair_engine()
        self._refill_combo()
        names = self._lang_filtered(voices)
        last = self.settings.get("last_voice", "")
        if last in names:
            self._select_voice(last)
        elif names:
            pref = next((v for v in names if "SeraphinaMultilingual" in v),
                        names[0])
            self._select_voice(pref)
        self.stat_voices.value_label.setText(f"{len(voices)}+")
        self._all_built = False
        self._fav_built = False
        self._icon_queue = list(range(self.voice_combo.count()))
        if not hasattr(self, "_icon_timer"):
            self._icon_timer = QTimer(self)
            self._icon_timer.timeout.connect(self._chunk_icons)
        self._icon_timer.start(60)
        self._rebuild_cards()
    except Exception as exc:
        self.logger.exception("Error cargando voces.")
        QMessageBox.critical(self, "Error",
                             f"No se pudieron cargar las voces: {exc}")


def _on_combo_voice(self):
    data = self.voice_combo.currentData(Qt.ItemDataRole.UserRole)
    voz_texto = self.voice_combo.currentText().strip()
    was_active = getattr(self, "_started", False)
    try:
        self.engine.stop()
        self._seg_queue = []  # seg-clear
    except Exception:
        pass
    self.player_timer.stop()
    self._started = False
    self._paused = False
    self._saw_running = False
    self._resume_offset = 0
    self._set_player_icon(False)
    self.progress_slider.setValue(0)
    self.time_cur.setText("0:00")
    if isinstance(data, dict):
        desc = data.get("description", "") or voz_texto
    else:
        desc = data or voz_texto
    try:
        self.engine.adapter.set_voice(desc)
        self.statusBar().showMessage(f"Voz cambiada: {_clean_voice_name(voz_texto)}")
        self._last_synth_key = None
        if was_active:
            self.speak_text()
    except Exception as exc:
        self.statusBar().showMessage(f"Error al cambiar voz: {exc}")



def _select_voice(self, name):
    if name in getattr(self, "_cloned_set", set()):
        self._selected_cloned = name
    else:
        self._selected_cloned = ""
    self._selected_voice = name
    if hasattr(self, "pro_badge"):
        self.pro_badge.setVisible(self._is_premium(name))
    for i in range(self.voice_combo.count()):
        if self.voice_combo.itemData(i, Qt.ItemDataRole.UserRole) == name:
            self.voice_combo.blockSignals(True)
            self.voice_combo.setCurrentIndex(i)
            self.voice_combo.blockSignals(False)
            break
    self.statusBar().showMessage(f"Cargando voz: {name}...")
    self._voice_worker = VoiceSelectWorker(self.engine.adapter, name)
    self._voice_worker.done.connect(self._on_voice_loaded)
    self._voice_worker.start()
    self._deferred_rebuilds()


def _toggle_fav(self, name):
    favs = self._favorites()
    if name in favs:
        favs.discard(name)
    else:
        favs.add(name)
    self.settings["favorites"] = sorted(favs)
    self._rebuild_cards()
    self._rebuild_all_page()
    self._rebuild_fav_page()



def _on_text_limited(self):
    self._update_counter_safe()
    limit = min(int(self.settings.get("char_limit", 5000)),
                self._plan_char_limit())
    text = self.text_edit.toPlainText()
    if len(text) > limit:
        self.text_edit.blockSignals(True)
        self.text_edit.setPlainText(text[:limit])
        cursor = self.text_edit.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.text_edit.setTextCursor(cursor)
        self.text_edit.blockSignals(False)
        self._update_counter_safe()
        self._show_limit_overlay()


def _update_counter_safe(self):
    try:
        self.update_counter()
    except Exception:
        pass

def update_counter(self):
    limit = int(self.settings.get("char_limit", 5000))
    total = len(self.text_edit.toPlainText())
    self.counter_label.setText(f"{total} / {limit}")


def _copy_text(self):
    QGuiApplication_clipboard = __import__(
        "PySide6.QtGui", fromlist=["QGuiApplication"]).QGuiApplication
    QGuiApplication_clipboard.clipboard().setText(self.text_edit.toPlainText())
    self.statusBar().showMessage("Texto copiado al portapapeles.")


def _open_document_dialog(self):
    path, _ = QFileDialog.getOpenFileName(
        self, "Abrir documento", "",
        "Archivos (*.txt *.md *.log *.csv *.pdf *.docx *.doc *.rtf *.html)")
    if not path:
        return
    try:
        content = file_reader.extract_text(Path(path))
        self.text_edit.setPlainText(content)
        self._add_to_history(content, file_path=path)
        self.statusBar().showMessage(f"Documento cargado: {Path(path).name}")
    except Exception as exc:
        QMessageBox.warning(self, "WillpoVoice",
                            f"No se pudo leer el archivo: {exc}")


def _show_limit_hint(self):
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QGraphicsOpacityEffect, QFrame
    hint = getattr(self, "_limit_hint", None)
    if hint is None:
        hint = QFrame(self)
        hint.setObjectName("limithint")
        hint.setStyleSheet(
            "#limithint { background: rgba(22,27,34,240);"
            " border: 1px solid #f5b544; border-radius: 10px; }")
        hb = QHBoxLayout(hint)
        hb.setContentsMargins(12, 8, 12, 8)
        hb.setSpacing(8)
        ic = QLabel()
        ic.setPixmap(make_icon("crown", "#f5b544", 14))
        hb.addWidget(ic)
        tx = QLabel(
            "Para añadir más caracteres por conversión, "
            "actualiza tu plan.")
        tx.setStyleSheet("color: #f0d878; font-size: 10.5px;")
        hb.addWidget(tx)
        btn = QPushButton("Ver planes")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(
            "QPushButton { background: #7c5cff; color: white;"
            " border: none; border-radius: 6px; padding: 4px 10px;"
            " font-size: 10px; font-weight: 600; }"
            " QPushButton:hover { background: #8b6eff; }")
        btn.clicked.connect(self._open_plans)
        hb.addWidget(btn)
        self._limit_hint = hint
        self._limit_hint_timer = QTimer(self)
        self._limit_hint_timer.setSingleShot(True)
        self._limit_hint_timer.timeout.connect(
            self._fade_limit_hint)
    hint.adjustSize()
    rect = self.limit_spin.geometry()
    parent = self.limit_spin.parent()
    if parent:
        pos = parent.mapTo(self, rect.bottomLeft())
        hint.move(pos.x(), pos.y() + 6)
    else:
        hint.move(rect.x(), rect.y() + rect.height() + 6)
    if self.settings.get("animations", True):
        eff = QGraphicsOpacityEffect(hint)
        eff.setOpacity(0.0)
        hint.setGraphicsEffect(eff)
        hint.show()
        hint.raise_()
        from PySide6.QtCore import QPropertyAnimation
        anim = QPropertyAnimation(eff, b"opacity")
        anim.setDuration(200)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        self._limit_hint_anim = anim
        anim.start()
    else:
        hint.show()
        hint.raise_()
    self._limit_hint_timer.start(3500)


def _show_limit_overlay(self):
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QGraphicsOpacityEffect, QFrame
    hint = getattr(self, "_limit_overlay", None)
    if hint is None:
        hint = QFrame(self)
        hint.setObjectName("limitoverlay")
        hint.setStyleSheet(
            "#limitoverlay { background: rgba(22,27,34,235);"
            " border: 1px solid #f5b544; border-radius: 10px; }")
        hb = QHBoxLayout(hint)
        hb.setContentsMargins(14, 10, 14, 10)
        hb.setSpacing(8)
        ic = QLabel()
        ic.setPixmap(make_icon("sparkles", "#f5b544", 16))
        hb.addWidget(ic)
        tx = QLabel(
            "¿Necesitas generar un proyecto más grande? Mejora tu plan "
            "y crea proyectos sin límites.")
        tx.setStyleSheet("color: #f0d878; font-size: 11px;")
        tx.setWordWrap(True)
        tx.setMaximumWidth(480)
        hb.addWidget(tx)
        btn = QPushButton("Ver planes")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(
            "QPushButton { background: #7c5cff; color: white;"
            " border: none; border-radius: 6px; padding: 6px 12px;"
            " font-size: 10.5px; font-weight: 600; }"
            " QPushButton:hover { background: #8b6eff; }")
        btn.clicked.connect(self._open_plans)
        hb.addWidget(btn)
        self._limit_overlay = hint
        self._limit_overlay_timer = QTimer(self)
        self._limit_overlay_timer.setSingleShot(True)
        self._limit_overlay_timer.timeout.connect(
            self._fade_limit_overlay)
    hint.adjustSize()
    from PySide6.QtCore import QPoint
    ref = self.text_edit
    pos = ref.mapTo(self, QPoint(0, ref.height() + 8))
    hint.move(pos.x(), pos.y())
    eff = QGraphicsOpacityEffect(hint)
    eff.setOpacity(0.0)
    hint.setGraphicsEffect(eff)
    hint.show()
    hint.raise_()
    from PySide6.QtCore import QPropertyAnimation
    anim = QPropertyAnimation(eff, b"opacity")
    anim.setDuration(250)
    anim.setStartValue(0.0)
    anim.setEndValue(1.0)
    self._limit_overlay_anim = anim
    anim.start()
    self._limit_overlay_timer.start(4500)


def _fade_limit_overlay(self):
    from PySide6.QtCore import QPropertyAnimation
    from PySide6.QtWidgets import QGraphicsOpacityEffect
    hint = getattr(self, "_limit_overlay", None)
    if hint is None:
        return
    eff = hint.graphicsEffect()
    if not isinstance(eff, QGraphicsOpacityEffect):
        eff = QGraphicsOpacityEffect(hint)
        hint.setGraphicsEffect(eff)
    anim = QPropertyAnimation(eff, b"opacity")
    anim.setDuration(400)
    anim.setStartValue(1.0)
    anim.setEndValue(0.0)
    anim.finished.connect(lambda: hint.hide())
    self._limit_overlay_anim = anim
    anim.start()


def _fade_limit_hint(self):
    from PySide6.QtCore import QPropertyAnimation
    from PySide6.QtWidgets import QGraphicsOpacityEffect
    hint = getattr(self, "_limit_hint", None)
    if hint is None:
        return
    eff = hint.graphicsEffect()
    if not isinstance(eff, QGraphicsOpacityEffect):
        eff = QGraphicsOpacityEffect(hint)
        hint.setGraphicsEffect(eff)
    anim = QPropertyAnimation(eff, b"opacity")
    anim.setDuration(350)
    anim.setStartValue(1.0)
    anim.setEndValue(0.0)
    anim.finished.connect(lambda: hint.hide())
    self._limit_hint_anim = anim
    anim.start()


def _auto_text_height(self):
    try:
        te = self.text_edit
        need = int(te.document().size().height()) + 14
        need = max(78, min(420, need))
        te.setMinimumHeight(need)
        te.setMaximumHeight(need)
    except Exception:
        pass


def _animate_text_height(self, h):
    from PySide6.QtCore import (QPropertyAnimation,
                                QParallelAnimationGroup)
    te = self.text_edit
    grp = QParallelAnimationGroup(self)
    starts = {"minimumHeight": te.minimumHeight(),
              "maximumHeight": te.maximumHeight()}
    for name, sv in starts.items():
        a = QPropertyAnimation(te, name.encode())
        a.setDuration(160)
        a.setStartValue(sv)
        a.setEndValue(h)
        grp.addAnimation(a)
    self._text_h_anim = grp
    grp.start()


def _toggle_adv(self):
    show = not self.adv_widget.isVisible()
    self.adv_widget.setVisible(show)
    self._auto_text_height()
    try:
        self.adv_button.set_expanded(show)
    except Exception:
        pass
    # Compactar/expandir tarjetas de Idioma y Voz
    try:
        if show:
            # compactar: ocultar combos, altura 38px
            if hasattr(self, "_lang_combo_ref"):
                self._lang_combo_ref.setVisible(False)
            if hasattr(self, "_voice_combo_ref"):
                self._voice_combo_ref.setVisible(False)
            if hasattr(self, "_lang_card"):
                self._lang_card.setFixedHeight(38)
                self._lang_card_layout.setContentsMargins(12, 8, 12, 6)
            if hasattr(self, "_voice_card"):
                self._voice_card.setFixedHeight(38)
                self._voice_card_layout.setContentsMargins(12, 8, 12, 6)
        else:
            # restaurar
            if hasattr(self, "_lang_combo_ref"):
                self._lang_combo_ref.setVisible(True)
            if hasattr(self, "_voice_combo_ref"):
                self._voice_combo_ref.setVisible(True)
            if hasattr(self, "_lang_card"):
                self._lang_card.setFixedHeight(76)
                self._lang_card_layout.setContentsMargins(12, 8, 12, 8)
            if hasattr(self, "_voice_card"):
                self._voice_card.setFixedHeight(76)
                self._voice_card_layout.setContentsMargins(12, 8, 12, 8)
    except Exception:
        pass


def _toggle_theme_msg(self):
    self.statusBar().showMessage("Tema claro: próximamente.")


def _fmt_time(self, s):
    m = int(s // 60)
    ss = int(s % 60)
    return f"{m}:{ss:02d}"


def _tick_player(self):
    if not getattr(self, "_started", False):
        return
    if getattr(self, "_paused", False):
        return
    if getattr(self, "_seeking", False):
        return
    try:
        st = self.engine.adapter.sapi.Status
        state = int(st.RunningState)
    except Exception:
        return
    if not getattr(self, "_saw_running", False):
        if state == 2:
            self._saw_running = True
            self._set_player_icon(True, loading=False)
            self.statusBar().showMessage("Reproduciendo...")
        else:
            return
    if state != 2:
        import time as _time
        if _time.time() - getattr(self, "_resume_at", 0.0) < 0.6:
            return
        q = getattr(self, "_seg_queue", [])
        if q and getattr(self, "_saw_running", False):
            a, b, boost = q.pop(0)
            self._seg_queue = q
            self._resume_offset = a
            self._saw_running = False
            self._resume_at = _time.time()
            texto = getattr(self, "_texto_para_ratio", "")
            self.engine.set_rate(
                max(-10, min(10, self.rate_slider.value() + boost)))
            self.engine.set_volume(
                min(100, self.volume_slider.value() + (6 if boost else 0)))
            self.engine.speak_async(self._tts_text(texto[a:b]))
            return
        self.player_timer.stop()
        self._started = False
        self._paused = False
        self._resume_offset = 0
        self._set_player_icon(False)
        self.statusBar().showMessage("Reproduccion terminada.")
        return
    try:
        texto = getattr(self, "_texto_para_ratio", "") or self.text_edit.toPlainText()
        offset = getattr(self, "_resume_offset", 0)
        pos = int(st.InputWordPosition)
        full_pos = offset + pos
        if len(texto) > 0 and full_pos > 0:
            ratio = min(1.0, full_pos / max(1, len(texto)))
        else:
            ratio = 0.0
        est = max(1.0, getattr(self, "_est_seconds", 1.0))
        secs = ratio * est
        self._seconds = secs
        self.time_cur.setText(self._fmt_time(secs))
        self.progress_slider.setValue(min(100, int(ratio * 100)))
    except Exception:
        pass



def _on_position_changed(self, pos):
    if not getattr(self, "_media_ready", False):
        return
    if getattr(self, "_seeking", False):
        return
    secs = pos / 1000.0
    self._seconds = secs
    self.time_cur.setText(self._fmt_time(secs))
    dur = self.player.duration()
    if dur > 0:
        pct = int(pos * 100 / dur)
        self.progress_slider.setValue(pct)

def _on_duration_changed(self, dur):
    if dur > 0:
        self.time_tot.setText(self._fmt_time(dur / 1000.0))
        self.progress_slider.setRange(0, 100)

def _on_media_status_changed(self, status):
    if int(status) == 7:
        self._started = False
        self._paused = False
        self._set_player_icon(False)
        self.statusBar().showMessage("Reproduccion terminada.")



def speak_text(self):
    try:
        text = self.text_edit.toPlainText().strip()
        if not text:
            self.statusBar().showMessage("Escribe un texto antes de reproducir.")
            return
        # Desviar a voz clonada si está seleccionada
        if getattr(self, "_selected_cloned", ""):
            self._tts_cloned(self._selected_cloned, text)
            return
        if not self._trial_gate(text):
            return
        try:
            self.engine.stop()
            self._seg_queue = []  # seg-clear
        except Exception:
            pass
        voice_data = self.voice_combo.currentData(Qt.ItemDataRole.UserRole)
        if isinstance(voice_data, dict):
            desc = voice_data.get("description", "") or ""
        else:
            desc = voice_data or ""
        if desc:
            try:
                self.engine.adapter.set_voice(desc)
            except Exception:
                pass
        import re as _re
        frases = [f for f in _re.split(r"(?<=[.!?…])\s+", text)
                  if f.strip()]
        emo = sum(1 for f in frases
                  if ("!" in f or "¡" in f or "?" in f or "¿" in f))
        boost = 0
        if frases and emo > 0 and (emo * 2) >= len(frases):
            boost = 2 if any("!" in f or "¡" in f for f in frases) else 1
        self.engine.set_rate(
            max(-10, min(10, self.rate_slider.value() + boost)))
        self.engine.set_volume(
            min(100, self.volume_slider.value() + (6 if boost else 0)))
        self._add_to_history(text)
        self.settings["conv_today"] = int(self.settings.get("conv_today", 0)) + 1
        self.stat_conv.value_label.setText(str(self.settings["conv_today"]))
        words = len(text.split()) or 1
        factor = 1.0 + self.rate_slider.value() / 20.0
        self._est_seconds = words / (2.8 * factor) + 0.6
        self._seconds = 0
        self._started = True
        self._saw_running = False
        self._paused = False
        self.time_tot.setText(self._fmt_time(self._est_seconds))
        self.time_cur.setText("0:00")
        self.progress_slider.setValue(0)
        self._set_player_icon(True, loading=True)
        self.statusBar().showMessage("Preparando audio...")
        self._texto_para_ratio = text
        self._resume_offset = 0
        self._resume_at = 0.0
        self._last_synth_key = (
            self.voice_combo.currentText().strip(), text)
        segs = self._express_segments(text)
        boosts = {s[2] for s in segs}
        has_emo = any(s[2] > 0 for s in segs)
        if has_emo and len(segs) > 1:
            self._seg_queue = list(segs[1:])
            a, b, boost = segs[0]
            self._resume_offset = a
            self._show_express_hint()
            self.engine.set_rate(
                max(-10, min(10, self.rate_slider.value() + boost)))
            self.engine.set_volume(
                min(100, self.volume_slider.value() + (6 if boost else 0)))
            self.engine.speak_async(self._tts_text(text[a:b]))
        else:
            self._seg_queue = []
            boost = max(s[2] for s in segs) if segs else 0
            self.engine.set_rate(
                max(-10, min(10, self.rate_slider.value() + boost)))
            self.engine.set_volume(
                min(100, self.volume_slider.value() + (6 if boost else 0)))
            self.engine.speak_async(self._tts_text(text))
        self._trial_spend(text)
        self.player_timer.start(50)
    except Exception as exc:
        QMessageBox.warning(self, "Error", f"No se pudo reproducir: {exc}")


def _on_synth_ready(self, wav_path):
    from PySide6.QtCore import QUrl
    self.player.setSource(QUrl.fromLocalFile(wav_path))
    self._media_ready = True
    self.player.play()
    self._set_player_icon(True, loading=False)
    self.statusBar().showMessage("Reproduciendo...")

def _on_synth_error(self, msg):
    self._set_player_icon(False)
    QMessageBox.warning(self, "Error", f"No se pudo sintetizar: {msg}")


def stop_speech(self):
    try:
        self._stop_preview()
        self.engine.stop()
        self._seg_queue = []  # seg-clear
        self.player_timer.stop()
        self._seconds = 0
        self._started = False
        self._paused = False
        self._set_player_icon(False)
        self.time_cur.setText("0:00")
        self.time_tot.setText("0:00")
        self.progress_slider.setValue(0)
        self.statusBar().showMessage("Reproducción detenida.")
    except Exception as exc:
        QMessageBox.warning(self, "Error", f"No se pudo detener: {exc}")


def _show_export_menu(self):
    from PySide6.QtCore import QPoint, QPropertyAnimation
    from PySide6.QtGui import QCursor
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance()
    if "QToolTip" not in (app.styleSheet() or ""):
        app.setStyleSheet(
            (app.styleSheet() or "") +
            " QToolTip { background: #161b22; color: #e6edf3;"
            " border: 1px solid #f5b544; border-radius: 8px;"
            " padding: 6px 10px; font-size: 10.5px; }")
    pop = QFrame(self, Qt.WindowType.Popup)
    pop.setObjectName("exportpop")
    pop.setFixedWidth(252)
    pop.setStyleSheet(
        "#exportpop { background: #161b22; border: 1px solid #30363d;"
        " border-radius: 12px; }")
    v = QVBoxLayout(pop)
    v.setContentsMargins(8, 8, 8, 8)
    v.setSpacing(4)
    opts = (
        ("wav", "wave", "#2dd4bf", "Audio WAV",
         "Máxima calidad, sin compresión. Para editar.",
         self.export_wav),
        ("mp3", "volume", "#7c5cff", "Audio MP3",
         "Comprimido y ligero. Para compartir.",
         self.export_mp3),
    )
    for kind, icon, color, label, tip, cb in opts:
        row = QFrame()
        row.setObjectName("row_" + kind)
        row.setCursor(Qt.CursorShape.PointingHandCursor)
        row.setStyleSheet(
            "#row_" + kind + " { background: transparent;"
            " border-radius: 8px; }"
            " #row_" + kind + ":hover { background: #232b3a; }")
        h = QHBoxLayout(row)
        h.setContentsMargins(10, 9, 10, 9)
        h.setSpacing(10)
        ic = QLabel()
        ic.setPixmap(make_icon(icon, color, 15))
        h.addWidget(ic)
        lb = QLabel(label)
        lb.setStyleSheet(
            "color: #e6edf3; font-size: 12px; font-weight: 600;"
            " background: transparent;")
        h.addWidget(lb)
        h.addStretch(1)
        q = QLabel("?")
        q.setFixedSize(18, 18)
        q.setAlignment(Qt.AlignmentFlag.AlignCenter)
        q.setStyleSheet(
            "background: #232b3a; color: #8b949e; border-radius: 9px;"
            " font-size: 9px; font-weight: 700;")
        q.setToolTip(tip)
        q.mouseReleaseEvent = lambda ev: None
        h.addWidget(q)
        row.mouseReleaseEvent = lambda ev, c=cb: (pop.close(), c())
        v.addWidget(row)
    btn = None
    for name in ("export_button", "btn_export", "export_btn"):
        btn = getattr(self, name, None)
        if btn is not None:
            break
    if btn is not None:
        pos = btn.mapToGlobal(QPoint(0, btn.height() + 6))
    else:
        pos = QCursor.pos()
    pop.move(pos)
    self._export_pop = pop
    pop.show()
    anim = QPropertyAnimation(pop, b"windowOpacity")
    anim.setDuration(140)
    anim.setStartValue(0.0)
    anim.setEndValue(1.0)
    pop._fade = anim
    anim.start()


def export_wav(self):
    text = self.text_edit.toPlainText().strip()
    if not text:
        self.statusBar().showMessage("Escribe un texto antes de exportar.")
        return
    if not self._trial_gate(text):
        return
    if not self._trial_gate(text):
        return
    path, _ = QFileDialog.getSaveFileName(self, "Guardar audio WAV",
                                          "willpovoice_audio.wav",
                                          "Archivos WAV (*.wav)")
    if not path:
        return
    if getattr(self, "_selected_cloned", ""):
        self._export_cloned(text, path, False)
        return
    self._trial_spend(text)
    self._run_export(self._tts_text(text), path, False)


def export_mp3(self):
    import tempfile
    text = self.text_edit.toPlainText().strip()
    if not text:
        self.statusBar().showMessage("Escribe un texto antes de exportar.")
        return
    path, _ = QFileDialog.getSaveFileName(self, "Guardar audio MP3",
                                          "willpovoice_audio.mp3",
                                          "Archivos MP3 (*.mp3)")
    if not path:
        return
    if not path.lower().endswith(".mp3"):
        path += ".mp3"
    self._mp3_final_path = path
    if getattr(self, "_selected_cloned", ""):
        self._export_cloned(text, path, True)
        return
    self._trial_spend(text)
    self._run_export(self._tts_text(text), tempfile.mktemp(suffix=".wav"), True)


from PySide6.QtWidgets import QDialog


class ExportProgressDialog(QDialog):
    """Barra de progreso de exportacion (estilo WillpoVoice)."""

    def __init__(self, parent, title="Exportando audio"):
        super().__init__(parent)
        self.setModal(True)
        self.setFixedWidth(420)
        self.setWindowTitle(title)
        self.setStyleSheet(
            "ExportProgressDialog { background: #0b0e14; }")
        v = QVBoxLayout(self)
        v.setContentsMargins(26, 22, 26, 20)
        v.setSpacing(12)
        row = QHBoxLayout()
        ic = QLabel()
        ic.setPixmap(make_icon("bolt", "#7c5cff", 20))
        row.addWidget(ic)
        ttl = QLabel(title)
        ttl.setStyleSheet(
            "color: #e6edf3; font-size: 14px; font-weight: 700;")
        row.addWidget(ttl)
        row.addStretch(1)
        self._pct = QLabel("0%")
        self._pct.setStyleSheet(
            "color: #7c5cff; font-size: 12px; font-weight: 700;")
        row.addWidget(self._pct)
        v.addLayout(row)
        from PySide6.QtWidgets import QProgressBar
        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setValue(0)
        self.bar.setFixedHeight(10)
        self.bar.setTextVisible(False)
        self.bar.setStyleSheet(
            "QProgressBar { background: #161b22; border: 1px solid #30363d;"
            " border-radius: 5px; }"
            " QProgressBar::chunk { background: qlineargradient("
            "x1:0,y1:0,x2:1,y2:0, stop:0 #6d5df0, stop:1 #7c5cff);"
            " border-radius: 5px; }")
        v.addWidget(self.bar)
        self._status = QLabel("Preparando sintesis...")
        self._status.setStyleSheet("color: #8b949e; font-size: 10.5px;")
        v.addWidget(self._status)
        from PySide6.QtCore import QTimer
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick_est)
        self._est = 1.0
        self._elapsed = 0.0

    def start_estimated(self, seconds):
        self._est = max(1.0, seconds)
        self._elapsed = 0.0
        self._timer.start(100)

    def _tick_est(self):
        self._elapsed += 0.1
        target = 90.0 * min(1.0, self._elapsed / self._est)
        if target > self.bar.value():
            self.bar.setValue(int(target))
            self._pct.setText(f"{int(target)}%")

    def set_progress(self, pct, status=None):
        self._timer.stop()
        pct = max(0, min(100, int(pct)))
        self.bar.setValue(pct)
        self._pct.setText(f"{pct}%")
        if status:
            self._status.setText(status)

    def set_status(self, status):
        self._status.setText(status)

    def finish(self, status="Completado"):
        self._timer.stop()
        self.bar.setValue(100)
        self._pct.setText("100%")
        self._status.setText(status)
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()


def _concat_wavs(self, paths, output):
    import wave
    first = None
    chunks = []
    for pp in paths:
        with wave.open(str(pp), "rb") as seg:
            pr = seg.getparams()
            if first is None:
                first = pr
            chunks.append((pr, seg.readframes(seg.getnframes())))
    with wave.open(str(output), "wb") as out:
        out.setparams(first)
        for pr, data in chunks:
            if (pr.nchannels, pr.sampwidth, pr.framerate) != (
                    first.nchannels, first.sampwidth, first.framerate):
                raise ValueError("formatos de segmento incompatibles")
            out.writeframes(data)


def _run_export_expressive(self, text, path, is_mp3, voice, dlg=None):
    import tempfile
    from PySide6.QtCore import QEventLoop
    segs = self._express_segments(text)
    tmp = Path(tempfile.mkdtemp())
    temp_paths = []
    try:
        n = max(1, len(segs))
        for i, (a, b, boost) in enumerate(segs):
            if dlg is not None:
                dlg.set_progress(
                    int(i * 90 / n),
                    f"Sintetizando fragmento {i + 1} de {n}...")
            seg_text = text[a:b]
            if not seg_text.strip():
                continue
            seg_path = tmp / f"seg_{i}.wav"
            temp_paths.append(seg_path)
            rate = max(-10, min(10, self.rate_slider.value() + boost))
            volume = min(100, self.volume_slider.value() +
                         (6 if boost else 0))
            loop = QEventLoop()
            result = {}
            w = ExportWorker(
                exporter=self.exporter, text=seg_text,
                path=str(seg_path), voice=voice,
                rate=rate, volume=volume)
            w.export_ok.connect(
                lambda p: (result.__setitem__("ok", p), loop.quit()))
            w.export_error.connect(
                lambda m: (result.__setitem__("err", m), loop.quit()))
            w.start()
            loop.exec()
            if "err" in result:
                raise RuntimeError(result["err"])
            if not seg_path.exists():
                raise RuntimeError("segmento no generado")
        if dlg is not None:
            dlg.set_progress(95, "Uniendo audio...")
        self._concat_wavs([str(x) for x in temp_paths], path)
        if dlg is not None:
            dlg.finish("Guardando archivo...")
            dlg.close()
        self.on_export_ok(path)
    finally:
        for x in temp_paths:
            try:
                Path(x).unlink(missing_ok=True)
            except Exception:
                pass
        try:
            tmp.rmdir()
        except Exception:
            pass


def _run_export(self, text, path, is_mp3):
    self._last_export_text = text
    voice = self.voice_combo.currentData(Qt.ItemDataRole.UserRole)
    dlg = ExportProgressDialog(
        self, "Exportando MP3..." if is_mp3 else "Exportando WAV...")
    dlg.show()
    segs = self._express_segments(text)
    has_boost = any(s[2] > 0 for s in segs)
    
    if has_boost:
        # Flujo segmentado (con expresividad)
        self.statusBar().showMessage("Exportando con expresividad...")
        try:
            self._run_export_expressive(text, path, is_mp3, voice, dlg)
        except Exception as exc:
            dlg.close()
            self.on_export_error(str(exc))
    else:
        # Flujo normal (rápido, sin boost)
        self.statusBar().showMessage("Exportando audio...")
        self.export_worker = ExportWorker(
            exporter=self.exporter, text=text, path=path, voice=voice,
            rate=self.rate_slider.value(), volume=self.volume_slider.value())
        words = len(text.split()) or 1
        factor = 1.0 + self.rate_slider.value() / 20.0
        dlg.start_estimated(words / (2.8 * factor) + 0.6)
        dlg.set_status("Sintetizando voz...")
        self.export_worker.export_ok.connect(
            lambda p: (dlg.finish(), dlg.close(), self.on_export_ok(p)))
        self.export_worker.export_error.connect(
            lambda m: (dlg.close(), self.on_export_error(m)))
        self.export_worker.start()


def _register_export_success(self, path, text, voice_name):
    """Registra un export exitoso en history (converted=True) y refresca Proyectos"""
    try:
        _txt = str(text or "").strip()
        if not _txt:
            return
        _items = self.settings.get("history", [])
        _dur = 0.0
        try:
            _dur = self._proj_dur_of(path)
        except Exception:
            _dur = 0.0
        _hit = None
        for _it in _items:
            if isinstance(_it, dict) and \
                    str(_it.get("content", "")).strip() == _txt:
                _hit = _it
                break
        if _hit is None:
            from datetime import datetime as _dt
            _hit = {"content": _txt,
                    "ts": _dt.now().strftime("%d/%m/%Y %H:%M:%S")}
            _items.append(_hit)
        _hit["converted"] = True
        _hit["file"] = str(path)
        if voice_name:
            _hit["voice"] = str(voice_name)
        if _dur:
            _hit["duration"] = _dur
        self.settings["history"] = _items
        try:
            from app.config import save_settings as _ss
            _ss(self.settings)
        except Exception:
            pass
        try:
            self._rebuild_projects()
        except Exception:
            pass
    except Exception:
        pass


def on_export_ok(self, path):
    final_path = path
    mp3_target = getattr(self, "_mp3_final_path", None)
    if mp3_target:
        self._mp3_final_path = None
        try:
            from core.mp3_encoder import wav_to_mp3
            wav_to_mp3(path, mp3_target)
            Path(path).unlink(missing_ok=True)
            final_path = mp3_target
        except Exception as exc:
            QMessageBox.warning(self, "Error",
                                f"No se pudo convertir a MP3: {exc}")
            return
    try:
        _txt = str(getattr(self, "_last_export_text", "") or "").strip()
        _voice = self.voice_combo.currentData(Qt.ItemDataRole.UserRole)
        self._register_export_success(final_path, _txt, _voice)
    except Exception:
        pass
    self.statusBar().showMessage(f"Audio guardado en: {final_path}")
    QMessageBox.information(self, "Exportación exitosa",
                            f"El audio se guardó en: {final_path}")


def on_export_error(self, message):
    QMessageBox.warning(self, "Error",
                        f"No se pudo exportar el audio: {message}")


def _load_history(self):
    self._clear_layout(self.history_layout)
    self._history_full = []
    from datetime import datetime as _dt
    items = self.settings.get("history", [])
    items = [it if isinstance(it, dict) else {
        "content": it, "label": "Texto manual"} for it in items]
    _dirty = False
    for it in items:
        if not it.get("ts"):
            it["ts"] = _dt.now().strftime("%d/%m/%Y %H:%M:%S")
            _dirty = True
    if _dirty:
        self.settings["history"] = items
    q = getattr(self, "_hsearch", "").strip().lower()
    flt = getattr(self, "_hfilter", "todos")
    for idx, it in enumerate(items):
        entry = it if isinstance(it, dict) else {
            "content": it, "label": "Texto manual"}
        label = entry.get("label", "Texto manual")
        is_file = label.lower().endswith(
            (".pdf", ".doc", ".docx", ".rtf", ".txt", ".md", ".log", ".csv"))
        if flt == "textos" and is_file:
            continue
        if flt == "archivos" and not is_file:
            continue
        if q and q not in label.lower() and q not in (
                entry.get("content", "") or "").lower():
            continue
        self._history_full.append(entry)
        card = HistoryCardV2(self, entry)
        card.load_clicked.connect(lambda i=idx: self._load_entry(i))
        card.delete_clicked.connect(lambda i=idx: self._delete_entry(i))
        self.history_layout.addWidget(card)
    if not self._history_full:
        empty = QLabel("No hay entradas que mostrar.")
        empty.setStyleSheet(
            "color: #8b949e; font-size: 13px; padding: 40px;")
        empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.history_layout.addWidget(empty)
    self.history_layout.addStretch()


def _load_entry(self, idx):
    if 0 <= idx < len(self._history_full):
        self.text_edit.setPlainText(
            self._history_full[idx].get("content", ""))
        self._switch_page(0)
        self.statusBar().showMessage("Contenido cargado en el editor.")


def _delete_entry(self, idx):
    items = self.settings.get("history", [])
    items = [it if isinstance(it, dict) else {
        "content": it, "label": "Texto manual"} for it in items]
    if 0 <= idx < len(items):
        items.pop(idx)
        self.settings["history"] = items
        self._load_history()
        self.statusBar().showMessage("Entrada eliminada del historial.")



def clear_history(self):
    self.settings["history"] = []
    self._load_history()
    self.statusBar().showMessage("Historial limpiado.")


def _add_to_history(self, text, file_path=None):
    text = (text or "").strip()
    if not text:
        return
    items = self.settings.get("history", [])
    label = "Texto manual"
    if file_path:
        label = Path(file_path).name
    from datetime import datetime as _dt
    voice = ""
    try:
        voice = self._display_voice_name(
            getattr(self, "_selected_voice", ""))
    except Exception:
        voice = ""
    entry = {"content": text, "label": label,
             "ts": _dt.now().strftime("%d/%m/%Y %H:%M:%S"),
             "voice": voice, "file": file_path, "converted": False}
    items = [it if isinstance(it, dict) else {"content": it, "label": "Texto manual"}
             for it in items]
    items = [it for it in items if it.get("content") != text]
    items.insert(0, entry)
    self.settings["history"] = items[: self.MAX_HISTORY]
    self._load_history()


def open_support(self):
    QDesktopServices.openUrl(QUrl("https://wa.me/51923073560"))
    self.statusBar().showMessage("Abriendo WhatsApp de soporte...")


def show_help(self):
    mb = QMessageBox(self)
    mb.setWindowTitle("Ayuda de WillpoVoice")
    mb.setIcon(QMessageBox.Icon.Information)
    mb.setText(
        "1. Elige una voz en el panel derecho.\n"
        "2. Escribe o pega tu texto.\n"
        "3. Pulsa Reproducir para escucharlo.\n"
        "4. Usa Exportar para guardar WAV/MP3.\n"
        "5. Marca voces con el coraz\u00f3n para favoritas.")
    mb.setStandardButtons(QMessageBox.StandardButton.Ok)
    mb.setStyleSheet(
        "QMessageBox { background: #0d1220; }"
        " QMessageBox QLabel { color: #e6edf3; font-size: 13px; }"
        " QMessageBox QPushButton { background: #1a2138; color: #e6edf3;"
        " border: 1px solid #232f4b; border-radius: 9px;"
        " padding: 8px 26px; font-weight: 600; font-size: 12px;"
        " min-width: 70px; }"
        " QMessageBox QPushButton:hover { border: 1px solid #7c5cff;"
        " background: #232f4b; }")
    for _lb in mb.findChildren(QLabel):
        _lb.setWordWrap(True)
    mb.exec()



def _refresh_prem_card(self):
    try:
        det = license_manager.license_details()
        licensed = det.get("state") == "licensed"
        tier = det.get("tier", "")
        name = tier if tier in ("Platinum", "Gold", "Estándar") else "Estándar"
        if licensed:
            desc = "Plan " + name + " activo permanentemente."
            plan_txt = "Plan " + name + " (permanente)"
        else:
            name = "Premium"
            desc = "Desbloquea todas las voces y funciones premium."
            plan_txt = "Plan Estándar"
        if getattr(self, "_prem_title", None) is not None:
            self._prem_title.setText(
                ("👑  WillpoVoice " + name) if licensed else "WillpoVoice")
        if getattr(self, "_prem_desc", None) is not None:
            self._prem_desc.setText(desc)
        if getattr(self, "_c6_title", None) is not None:
            self._c6_title.setText(
                "WillpoVoice " + (name if licensed else "Premium"))
        if getattr(self, "_c6_plan", None) is not None:
            self._c6_plan.setText(plan_txt)
        if getattr(self, "_c6_chars", None) is not None:
            try:
                lim = self._plan_char_limit()
                self._c6_chars.setText(
                    "Ilimitados" if lim >= 999999 else f"{lim:,} caracteres")
            except Exception:
                pass
        if licensed and not getattr(self, "_thx_shown", False):
            self._thx_shown = True
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(
                self, "¡Gracias por su compra!",
                "Tu licencia " + name + " se activó correctamente.\n"
                "Disfruta de todas las funciones premium.")
    except Exception:
        pass

def _open_license_dialog(self):
    """Abre el dialogo de activacion de licencia y guarda la clave."""
    try:
        state, days_left = license_manager.check_status()
        dialog = LicenseDialog(
            self,
            license_manager.get_machine_id(),
            days_left if state == "trial" else -1,
        )
        dialog.setWindowFlags(
            dialog.windowFlags()
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Dialog
        )
        try:
            self._center_on_screen(dialog)
        except Exception:
            pass
        dialog.exec()
        if getattr(dialog, "activated_key", ""):
            data = license_manager.load_data()
            data["license_key"] = dialog.activated_key
            license_manager.save_data(data)
            try:
                pass  # sin license_label: el estado se muestra en statusBar y tarjeta premium
            except Exception:
                pass
            try:
                self._refresh_token_chip("licensed")
            except Exception:
                pass
            self.statusBar().showMessage(
                "Licencia activada correctamente.", 6000)
            self._refresh_prem_card()
    except Exception:
        try:
            self.logger.exception(
                "No se pudo abrir el dialogo de licencia.")
        except Exception:
            pass


def _check_license(self):
    state, days_left = license_manager.check_status()
    self._refresh_token_chip(state)

    try:
        from PySide6.QtWidgets import QMessageBox
        _st, _dl = license_manager.check_status()
        if _st == "trial" and _dl == 2:
            QTimer.singleShot(1200, lambda: QMessageBox.information(
                self, "Prueba gratuita",
                "Tu periodo de prueba termina en 2 dias.\n"
                "Plan Estándar activo: hasta 5,000 caracteres por conversión.\n\n"
                "Compra un plan para no perder el acceso."))
    except Exception:
        pass
    if state == "licensed":
        pass  # sin license_label: el estado se muestra en statusBar y tarjeta premium
        self.statusBar().showMessage("Version licenciada.")
        return True
    if getattr(self, "_suppress_license_dialog", False) and state == "trial":
        return True
    dialog = LicenseDialog(
        self,
        license_manager.get_machine_id(),
        days_left if state == "trial" else -1,
    )
    dialog.setWindowFlags(
        dialog.windowFlags()
        | Qt.WindowType.WindowStaysOnTopHint
        | Qt.WindowType.Dialog
    )
    dialog.adjustSize()
    self._center_on_screen(dialog)
    dialog.show()
    dialog.raise_()
    dialog.activateWindow()
    dialog.exec()
    if dialog.activated_key:
        data = license_manager.load_data()
        data["license_key"] = dialog.activated_key
        license_manager.save_data(data)
        pass  # sin license_label: el estado se muestra en statusBar y tarjeta premium
        self._refresh_prem_card()
        return True
    return dialog.trial_accepted


def showEvent(self, event):
    if not getattr(self, "_centered_once", False):
        self._centered_once = True
        self._center_on_screen(self)
    QMainWindow.showEvent(self, event)
    if not getattr(self, "_license_checked", False):
        self._license_checked = True
        QTimer.singleShot(300, self._deferred_license)
        QTimer.singleShot(900, self._refresh_prem_card)
    if not getattr(self, "_update_checked", False):
        self._update_checked = True
        QTimer.singleShot(1500, self._check_updates)


def closeEvent(self, event):
    w = getattr(self, "_preview_worker", None)
    if w is not None:
        w.shutdown()
        w.wait(2000)
    try:
        self.settings["last_voice"] = self._current_voice()
        save_settings(self.settings)
        self.engine.stop()
        self._seg_queue = []  # seg-clear
    except Exception:
        self.logger.exception("Error al cerrar.")
    event.accept()


def _plan_char_limit(self):
    from core import license_manager
    details = license_manager.license_details()
    tier = details.get("tier", "")
    if "gold" in tier.lower() or "por vida" in tier.lower() or "lifetime" in tier.lower():
        return 999999
    if "platinum" in tier.lower() or "mensual" in tier.lower():
        return 20000
    return 5000


def _current_voice(self):
    data = self.voice_combo.currentData(Qt.ItemDataRole.UserRole)
    return data or self.voice_combo.currentText()


MainWindow._build_ui = _build_ui
MainWindow._connect_signals = _connect_signals
MainWindow._switch_page = _switch_page
MainWindow._toggle_sidebar = _toggle_sidebar
MainWindow._set_rtab = _set_rtab
MainWindow._clear_layout = _clear_layout
MainWindow._favorites = _favorites
MainWindow._make_card = _make_card
MainWindow._rebuild_cards = _rebuild_cards
MainWindow._rebuild_all_page = _rebuild_all_page
MainWindow._rebuild_fav_page = _rebuild_fav_page
MainWindow._layout_fav_bg = _layout_fav_bg
MainWindow._fav_preview = _fav_preview
MainWindow._rebuild_voices_page = _rebuild_voices_page
MainWindow._voc_set_tab = _voc_set_tab
MainWindow._voc_toggle_all = _voc_toggle_all


def _refresh_card_states(self):
    sel = getattr(self, "_selected_voice", "")
    favs = self._favorites()
    for lay in (getattr(self, "voice_cards_layout", None),
                getattr(self, "all_layout", None)):
        if lay is None:
            continue
        for i in range(lay.count()):
            it = lay.itemAt(i)
            w = it.widget() if it is not None else None
            if isinstance(w, VoiceCardV2):
                w.set_state(w._name == sel, w._name in favs)


MainWindow._refresh_card_states = _refresh_card_states
MainWindow._append_voc_cards = _append_voc_cards
MainWindow._layout_voc_bg = _layout_voc_bg
MainWindow._layout_hist_bg = _layout_hist_bg
MainWindow._layout_adj_bg = _layout_adj_bg


def _on_accent_changed(self, c):
    global ACCENT
    if c == "personalizado":
        from PySide6.QtWidgets import QColorDialog
        col = QColorDialog.getColor(
            QColor(self.settings.get("accent", "#7c5cff")),
            self, "Color de acento personalizado")
        if not col.isValid():
            return
        self.settings["accent"] = col.name()
    else:
        self.settings["accent"] = c
    self.settings["accent_sel"] = c
    ACCENT = self.settings.get("accent", "#7c5cff")
    try:
        self._apply_theme()
    except Exception:
        pass
    try:
        self._rebuild_cards()
        self._rebuild_voices_page()
    except Exception:
        pass
    try:
        self._accent_dots.set_current(c)
    except Exception:
        pass
    self.statusBar().showMessage("Color de acento aplicado.")


def _open_lang_dialog(self):
    try:
        d = _LangDialog(self)
        d.exec()
    except Exception as e:
        import traceback
        traceback.print_exc()
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.critical(self, "Error dialogo idiomas", str(e))


TR_EN = {
    "Inicio": "Home", "Historial": "History", "Voces": "Voices",
    "Favoritos": "Favorites", "Proyectos": "Projects", "Chat IA": "AI Chat",
    "Ajustes": "Settings", "Ayuda": "Help", "Soporte": "Support",
    "Personaliza WillpoVoice seg\u00fan tus preferencias.":
        "Customize WillpoVoice to your preferences.",
    "Restaurar valores": "Restore defaults",
    "General": "General", "Idioma de la aplicaci\u00f3n": "App language",
    "Tema": "Theme", "Oscuro": "Dark", "Claro": "Light", "Sistema": "System",
    "Animaciones": "Animations",
    "Mostrar sugerencias IA": "Show AI suggestions",
    "Conversi\u00f3n de voz": "Voice conversion",
    "L\u00edmite de caracteres": "Character limit",
    "Mostrar contador de caracteres": "Show character counter",
    "Reproducir autom\u00e1ticamente al generar": "Auto-play on generate",
    "Calidad de audio": "Audio quality",
    "Formato de exportaci\u00f3n": "Export format",
    "Audio": "Audio", "Volumen predeterminado": "Default volume",
    "Velocidad predeterminada": "Default speed",
    "Vista previa antes de exportar": "Preview before export",
    "Dispositivo de salida": "Output device",
    "Apariencia": "Appearance", "Color de bordes": "Border color",
    "Densidad de interfaz": "Interface density", "C\u00f3moda": "Comfortable",
    "Azul": "Blue", "Violeta": "Violet", "Personalizado": "Custom",
    "Archivos y almacenamiento": "Files & storage",
    "Carpeta de exportaci\u00f3n": "Export folder",
    "Cambiar carpeta": "Change folder",
    "Guardar autom\u00e1ticamente historial": "Auto-save history",
    "Limpiar archivos temporales": "Clear temporary files",
    "Limpiar": "Clear", "Plan actual:": "Current plan:",
    "Plan Est\u00e1ndar": "Standard plan",
    "Caracteres por conversi\u00f3n:": "Characters per conversion:",
    "5,000 caracteres": "5,000 characters", "Ver planes": "See plans",
    "Acerca de WillpoVoice": "About WillpoVoice", "Versi\u00f3n": "Version",
    "Motor de voz": "Voice engine",
    "Buscar actualizaciones": "Check for updates",
    "Ver licencia": "View license",
    "Texto manual": "Manual text", "Importar archivo": "Import file",
    "Pegar": "Paste", "Idioma": "Language",
    "Voz seleccionada": "Selected voice",
    "Opciones avanzadas": "Advanced options",
    "Reproducir": "Play", "Detener": "Stop", "Exportar": "Export",
    "Voces disponibles": "Available voices", "Idiomas": "Languages",
    "Conversiones hoy": "Conversions today",
    "Solo Premium": "Premium only", "Ver todas": "View all",
    "Buscar voces...": "Search voices...", "Todas": "All",
    "Premium": "Premium", "Favoritas": "Favorites",
    "Escribe aqu\u00ed el texto que quieres convertir a voz...":
        "Type the text you want to convert to voice...",
    "Escribe aqu\u00ed el texto que quieres convertir a voz\u2026":
        "Type the text you want to convert to voice...",
    "Velocidad": "Speed", "Volumen": "Volume",
    "M\u00e1s lenta": "Slower", "M\u00e1s r\u00e1pida": "Faster",
    "Bajo": "Low", "Alto": "High", "Alta": "High", "Media": "Medium",
    "Elige tu <span style=\"color:#a78bfa;\">plan</span>":
        "Choose your <span style=\"color:#a78bfa;\">plan</span>",
    "Voces <span style=\"color:#f472b6;\">premium</span> reales, sin l\u00edmites artificiales.":
        "Real <span style=\"color:#f472b6;\">premium</span> voices, no artificial limits.",
    "Hasta 5,000 caracteres por conversi\u00f3n":
        "Up to 5,000 characters per conversion",
    "Chat IA incluido": "AI Chat included",
    "Todas las voces premium": "All premium voices",
    "Hasta 20,000 caracteres por conversi\u00f3n (\u224822 min)":
        "Up to 20,000 characters per conversion (~22 min)",
    "Soporte prioritario por Discord": "Priority support via Discord",
    "Actualizaciones incluidas": "Updates included",
    "Caracteres ILIMITADOS": "UNLIMITED characters",
    "Sin l\u00edmites artificiales": "No artificial limits",
    "Voces nuevas para siempre": "New voices forever",
    "Soporte prioritario de por vida": "Lifetime priority support",
    "Incluido con tu compra": "Included with your purchase",
    "Comprar": "Buy", "Recomendado": "Recommended",
    "Incluido": "Included", "Pago seguro": "Secure payment",
    "Tus datos est\u00e1n protegidos": "Your data is protected",
    "Acceso inmediato": "Instant access",
    "Disfruta al instante": "Enjoy instantly",
    "Sin renovaciones": "No renewals",
    "Pago \u00fanico, para siempre": "One-time payment, forever",
    "Desbloquea todas las voces y funciones premium.":
        "Unlock all premium voices and features.",
    "Voces de alta calidad para proyectos profesionales.":
        "High-quality voices for professional projects.",
    "Explora todas las voces disponibles en tu sistema.":
        "Explore all the voices available on your system.",
    "Todas las voces": "All voices",
    "Historial de conversiones": "Conversion history",
    "Buscar en el historial...": "Search history...",
    "Filtrar": "Filter", "Texto manual": "Manual text",
    "Escribe tu mensaje...": "Type your message...",
    "Analizar guion y mejorar": "Analyze and improve script",
    "Crear anuncios publicitarios": "Create ad commercials",
    "Voz est\u00e1ndar": "Standard voice",
    "Cargando voces...": "Loading voices...",
    "Predeterminado del sistema": "System default",
    "Predeterminado de": "Default",
    "Plan Est\u00e1ndar": "Standard plan",
    "Plan Platinum": "Platinum Plan", "Plan Gold": "Gold Plan",
    "S/ 30 \u00b7 pago seguro con Yape": "S/ 30 \u00b7 secure payment with Yape",
    "S/ 50 \u00b7 pago seguro con Yape": "S/ 50 \u00b7 secure payment with Yape",
    "Escanea el QR con tu app Yape y paga de forma segura, sin necesidad de nuestro numero.":
        "Scan the QR with your Yape app and pay securely, no need for our number.",
    "1) Escanea el QR con Yape  \u00b7  2) Envia tu comprobante por Discord  \u00b7  3) Recibe tu clave al instante":
        "1) Scan the QR with Yape  \u00b7  2) Send your receipt via Discord  \u00b7  3) Get your key instantly",
    "Pagar con Yape ahora": "Pay with Yape now",
    "Enviar comprobante por Discord": "Send receipt via Discord",
    "Enviar comprobante por WhatsApp": "Send receipt via WhatsApp",
    "Asistente inteligente de WillpoVoice":
        "WillpoVoice intelligent assistant",
    "Configurar API Key": "Configure API Key",
    "Configura tu API Key": "Set up your API Key",
    "Conecta tu API Key para desbloquear todo el poder del Chat IA de WillpoVoice.":
        "Connect your API Key to unlock the full power of WillpoVoice AI Chat.",
    "Eliminar API Key": "Remove API Key",
    "Seguridad de tus datos": "Your data security",
    "Las conversaciones que tienes son privadas.":
        "Your conversations are private.",
    "Acceso Completo": "Full access",
    "Disfruta de respuestas mas rapidas y precisas con Groq.":
        "Enjoy faster and more accurate answers with Groq.",
    "Ingresa tu API Key": "Enter your API Key",
    "Obtener API Key gratis": "Get a free API Key",
    "\u00a1Hola! \u00bfEn qu\u00e9 puedo ayudarte hoy?":
        "Hi! How can I help you today?",
    "Copiar": "Copy", "Agregar a conversi\u00f3n": "Add to conversion",
    "Escuchar": "Listen",
    "Crear un guion / historia": "Create a script / story",
    "Configura tu API Key para empezar...":
        "Set up your API Key to start...",
    "Presiona Enter para conectar  \u00b7  Obt\u00e9n tu clave gratis en console.groq.com ":
        "Press Enter to connect  \u00b7  Get your free key at console.groq.com ",
    "T\u00fa tienes el control absoluto: ":
        "You have full control: ",
}

CURRENT_LANG = "Espa\u00f1ol"
_LIGHT_SUSPEND = False

def _tr(s):
    return TR_EN.get(s, s) if CURRENT_LANG == "English" else s


def _retranslate(self):
    lang = self.settings.get("lang_pref", "Espa\u00f1ol")
    if lang == "English":
        mp = TR_EN
    else:
        mp = {v: k for k, v in TR_EN.items() if v != k}
    from PySide6.QtWidgets import (QLabel as _QL, QPushButton as _QB,
                                   QLineEdit as _QE)
    for lb in self.findChildren(_QL):
        if lb.text() in mp:
            lb.setText(mp[lb.text()])
    for b in self.findChildren(_QB):
        tx = b.text().strip()
        if tx in mp:
            b.setText(mp[tx])
    for e in self.findChildren(_QE):
        if e.placeholderText() in mp:
            e.setPlaceholderText(mp[e.placeholderText()])
    from PySide6.QtWidgets import QComboBox as _QC
    for cb in self.findChildren(_QC):
        for i in range(cb.count()):
            tx = cb.itemText(i).strip()
            if tx in mp:
                cb.setItemText(i, mp[tx])


def _on_lang_pref(self, v):
    self.settings["lang_pref"] = v
    global CURRENT_LANG
    CURRENT_LANG = v
    try:
        self._retranslate()
    except Exception:
        import traceback
        traceback.print_exc()
    self.statusBar().showMessage("Idioma aplicado: " + v)


def _rebuild_settings(self):
    try:
        if hasattr(self, "limit_spin"):
            self.limit_spin.blockSignals(True)
            self.limit_spin.setValue(
                min(int(self.settings.get("char_limit", 5000)),
                    self._plan_char_limit()))
            self.limit_spin.blockSignals(False)
        if hasattr(self, "vol_slider"):
            self.vol_slider.setValue(int(self.settings.get("volume", 100)))
        if hasattr(self, "rate_slider"):
            self.rate_slider.setValue(int(self.settings.get("rate", 0)))
    except Exception:
        pass

MainWindow._rebuild_settings = _rebuild_settings
MainWindow._on_accent_changed = _on_accent_changed
MainWindow._on_lang_pref = _on_lang_pref
MainWindow._retranslate = _retranslate


_orig_retranslate_wp = MainWindow._retranslate


def _retranslate_wp(self, *a, **k):
    r = _orig_retranslate_wp(self, *a, **k)
    try:
        from PySide6.QtCore import QTimer as _QTwp
        _QTwp.singleShot(0, self._refresh_prem_card)
    except Exception:
        pass
    return r


MainWindow._retranslate = _retranslate_wp

def _layout_proj_bg(self):
    try:
        import sys as _sys
        base = Path(getattr(_sys, "_MEIPASS",
                            Path(__file__).resolve().parents[1]))
        pg = getattr(self, "_proj_page", None)
        bg = getattr(self, "_proj_bg", None)
        if pg is None or bg is None:
            return
        if not getattr(self, "_proj_bg_pix", None):
            sp = base / "assets" / "icons" / ("chat_bg_ligth.png" if LIGHT_MODE else "chat_bg.png")
            if sp.exists():
                self._proj_bg_pix = QPixmap(str(sp))
        if getattr(self, "_proj_bg_pix", None):
            bg.setGeometry(0, 0, pg.width(), pg.height())
            bg.setPixmap(self._proj_bg_pix)
            bg.setScaledContents(True)
    except Exception:
        pass


def _set_proj_tab(self, key):
    self._proj_tab = key
    for b, kk in getattr(self, "_proj_tab_group", []):
        b.setChecked(kk == key)
    self._proj_page_num = 0
    self._rebuild_projects()


def _proj_page_go(self, d):
    self._proj_page_num = max(0, self._proj_page_num + d)
    self._rebuild_projects()


def _proj_fmt_dur(self, secs):
    try:
        secs = int(float(secs))
        return "%02d:%02d" % (secs // 60, secs % 60)
    except Exception:
        return "00:00"


def _proj_set_icon(btn, playing):
    try:
        btn.setIcon(QIcon(make_icon("pause" if playing else "play",
                                    "#7cb7ff", 14)))
    except Exception:
        pass


def _proj_dur_of(self, path):
    try:
        p = Path(path)
        if not p.exists():
            return 0.0
        if p.suffix.lower() == ".wav":
            import wave
            with wave.open(str(p), "rb") as wv:
                return wv.getnframes() / float(wv.getframerate())
        if p.suffix.lower() == ".mp3":
            return p.stat().st_size * 8.0 / (192.0 * 1000.0)
    except Exception:
        pass
    return 0.0


def _proj_toggle(self, path, btn):
    from PySide6.QtMultimedia import QMediaPlayer
    pl = getattr(self, "_proj_player", None)
    cur = ""
    if pl is not None:
        try:
            cur = pl.source().toLocalFile()
        except Exception:
            cur = ""
    if pl is not None and cur == str(path):
        st = pl.playbackState()
        if st == QMediaPlayer.PlaybackState.PlayingState:
            pl.pause()
            _proj_set_icon(btn, False)
            return
        if st == QMediaPlayer.PlaybackState.PausedState:
            pl.play()
            _proj_set_icon(btn, True)
            return
    self._proj_play(path)
    for _f2, _b2 in getattr(self, "_proj_btn_by_file", {}).items():
        try:
            _proj_set_icon(_b2, str(_f2) == str(path))
        except Exception:
            pass


def _proj_state_changed(self, st):
    from PySide6.QtMultimedia import QMediaPlayer
    if st == QMediaPlayer.PlaybackState.StoppedState:
        for _b2 in getattr(self, "_proj_btn_by_file", {}).values():
            try:
                _proj_set_icon(_b2, False)
            except Exception:
                pass


def _proj_play(self, path):
    try:
        if not path or not Path(path).exists():
            self.statusBar().showMessage("El archivo de audio no existe.")
            return
        from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
        from PySide6.QtCore import QUrl
        if not getattr(self, "_proj_player", None):
            self._proj_player = QMediaPlayer(self)
            self._proj_player.setAudioOutput(QAudioOutput(self))
            self._proj_player.playbackStateChanged.connect(self._proj_state_changed)
        self._proj_player.setSource(QUrl.fromLocalFile(str(path)))
        self._proj_player.play()
        self.statusBar().showMessage("Reproduciendo proyecto...")
    except Exception:
        pass


def _proj_menu(self, e, anchor):
    from PySide6.QtWidgets import QMenu
    from PySide6.QtCore import QPoint
    m = QMenu(self)
    m.setStyleSheet(
        "QMenu { background: #10141f; color: #e6edf3;"
        " border: 1px solid #232f4b; border-radius: 10px; }"
        " QMenu::item { padding: 8px 18px; }"
        " QMenu::item:selected { background: rgba(124,92,255,40); }")
    favs = set(self.settings.get("proj_favs", []))
    a1 = m.addAction("Quitar favorito" if e["name"] in favs
                     else "Marcar favorito")
    a2 = m.addAction("Abrir carpeta")
    a3 = m.addAction("Eliminar")
    r = m.exec(anchor.mapToGlobal(QPoint(0, anchor.height())))
    if r == a1:
        if e["name"] in favs:
            favs.discard(e["name"])
        else:
            favs.add(e["name"])
        self.settings["proj_favs"] = list(favs)
        self._rebuild_projects()
    elif r == a2:
        from PySide6.QtCore import QUrl
        from PySide6.QtGui import QDesktopServices
        tgt = None
        raw = e.get("raw", {})
        for k in ("output_path", "file", "path", "source",
                  "file_path", "src"):
            v = str(raw.get(k, "") or e.get(k, "") or "")
            if v and Path(v).exists():
                tgt = Path(v).parent if Path(v).is_file() else Path(v)
                break
        if tgt is None and "." in e["name"][-6:]:
            for d in (Path.home() / "Downloads", Path.home() / "Documents",
                      Path.home() / "Desktop", Path.home() / "Descargas",
                      Path.home() / "Escritorio"):
                try:
                    if (d / e["name"]).exists():
                        tgt = d
                        break
                except Exception:
                    pass
        if tgt is None:
            for kk in ("export_dir", "export_folder", "out_dir"):
                exp = str(self.settings.get(kk, "") or "")
                if exp and Path(exp).exists():
                    tgt = Path(exp)
                    break
        if tgt is None:
            tgt = Path.home() / "Documents"
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(tgt)))
        self.statusBar().showMessage("Carpeta abierta: " + str(tgt))
    elif r == a3:
        items = self.settings.get("history", [])
        if 0 <= e["idx"] < len(items):
            items.pop(e["idx"])
            self.settings["history"] = items
            try:
                self._load_history()
            except Exception:
                pass
            self._rebuild_projects()


def _proj_row(self, e, favs):
    row = QFrame()
    row.setObjectName("prow")
    row.setFixedHeight(78)
    row.setStyleSheet(
        "#prow { background: rgba(13,17,26,160); border-radius: 14px;"
        " border: 1px solid rgba(255,255,255,6); }"
        " #prow:hover { border: 1px solid rgba(124,92,255,60); }")
    h = QHBoxLayout(row)
    h.setContentsMargins(14, 0, 12, 0)
    h.setSpacing(14)
    colors = ["#a855f7", "#2dd4bf", "#f59e0b", "#ec4899", "#3b82f6"]
    kinds = ["wave", "doc", "mic"]
    ci = len(e["name"]) % len(colors)
    tile = QLabel()
    tile.setFixedSize(48, 48)
    tile.setPixmap(make_icon(kinds[ci % 3], colors[ci], 20))
    tile.setAlignment(Qt.AlignmentFlag.AlignCenter)
    _rc = int(colors[ci][1:3], 16)
    _gc = int(colors[ci][3:5], 16)
    _bc = int(colors[ci][5:7], 16)
    tile.setStyleSheet(
        "background: rgba(%d,%d,%d,38); border-radius: 12px;"
        % (_rc, _gc, _bc))
    h.addWidget(tile)
    vc = QVBoxLayout()
    vc.setSpacing(3)
    trow = QHBoxLayout()
    trow.setSpacing(8)
    nm = QLabel(e["name"])
    nm.setStyleSheet("color: #ffffff; font-size: 14px; font-weight: 700;")
    trow.addWidget(nm)
    if e["name"] in favs:
        stl = QLabel()
        stl.setPixmap(make_icon("star", "#f5b301", 13))
        trow.addWidget(stl)
    trow.addStretch(1)
    vc.addLayout(trow)
    meta = QHBoxLayout()
    meta.setSpacing(6)
    av = QLabel((e["voice"] or "V")[:1].upper())
    av.setFixedSize(18, 18)
    av.setAlignment(Qt.AlignmentFlag.AlignCenter)
    av.setStyleSheet(
        "border-radius: 9px; background: #232f4b; color: #c4b5fd;"
        " font-size: 9px; font-weight: 700;")
    meta.addWidget(av)
    mv = QLabel(e["voice"] or "Voz estandar")
    mv.setStyleSheet("color: #8b93b0; font-size: 11px;")
    meta.addWidget(mv)
    d1 = QLabel("\u00b7")
    d1.setStyleSheet("color: #4b5568; font-size: 11px;")
    meta.addWidget(d1)
    md = QLabel(e["ts"][:16])
    md.setStyleSheet("color: #8b93b0; font-size: 11px;")
    meta.addWidget(md)
    meta.addStretch(1)
    vc.addLayout(meta)
    h.addLayout(vc, 1)
    rc = QVBoxLayout()
    rc.setSpacing(2)
    rc.addStretch(1)
    rt = QLabel(self._proj_fmt_dur(e["dur"]))
    rt.setStyleSheet("color: #ffffff; font-size: 14px; font-weight: 700;")
    rt.setAlignment(Qt.AlignmentFlag.AlignRight)
    rc.addWidget(rt)
    rl = QLabel("Duraci\u00f3n")
    rl.setStyleSheet("color: #8b93b0; font-size: 10px;")
    rl.setAlignment(Qt.AlignmentFlag.AlignRight)
    rc.addWidget(rl)
    rc.addStretch(1)
    h.addLayout(rc)
    play = QPushButton()
    play.setFixedSize(44, 40)
    play.setIcon(QIcon(make_icon("play", "#7cb7ff", 14)))
    play.setCursor(Qt.CursorShape.PointingHandCursor)
    play.setStyleSheet(
        "QPushButton { background: rgba(59,130,246,18);"
        " border: 1px solid rgba(59,130,246,60); border-radius: 10px; }"
        " QPushButton:hover { background: rgba(59,130,246,40); }")
    if not hasattr(self, "_proj_btn_by_file"):
        self._proj_btn_by_file = {}
    self._proj_btn_by_file[e["file"]] = play
    play.clicked.connect(
        lambda _=False, f=e["file"], pb=play: self._proj_toggle(f, pb))
    h.addWidget(play)
    keb = QPushButton("\u22ee")
    keb.setFixedSize(40, 40)
    keb.setCursor(Qt.CursorShape.PointingHandCursor)
    keb.setStyleSheet(
        "QPushButton { background: rgba(13,17,26,160); color: #8b93b0;"
        " border: 1px solid #232f4b; border-radius: 10px;"
        " font-size: 15px; font-weight: 700; }"
        " QPushButton:hover { border: 1px solid #7c5cff; }")
    keb.clicked.connect(
        lambda _=False, ee=e, kb=keb: self._proj_menu(ee, kb))
    h.addWidget(keb)
    return row


def _rebuild_projects(self):
    lay = getattr(self, "_proj_layout", None)
    if lay is None:
        return
    while lay.count():
        it = lay.takeAt(0)
        if it.widget():
            it.widget().deleteLater()
    self._proj_btn_by_file = {}
    items = self.settings.get("history", [])
    favs = set(self.settings.get("proj_favs", []))
    arch = set(self.settings.get("proj_arch", []))
    from datetime import datetime as _dt, timedelta as _td
    now = _dt.now()
    entries = []
    total_secs = 0.0
    total_mb = 0.0
    voices = set()
    for idx, it in enumerate(items):
        if not isinstance(it, dict) or not it.get("converted"):
            continue
        label = str(it.get("label", "Texto manual"))
        content = str(it.get("content", "") or "")
        name = label if label not in ("", "Texto manual") else (
            (content[:38] + "...") if len(content) > 38 else
            (content or "Proyecto"))
        voice = str(it.get("voice", "") or "")
        ts = str(it.get("ts", "") or "")
        try:
            dur = float(it.get("duration", 0) or 0)
        except Exception:
            dur = 0.0
        if dur <= 0:
            _fp0 = str(it.get("output_path", "") or it.get("file", "") or "")
            if _fp0:
                dur = self._proj_dur_of(_fp0)
        fpath = str(it.get("output_path", "") or it.get("file", "") or "")
        try:
            if fpath and Path(fpath).exists():
                total_mb += Path(fpath).stat().st_size / (1024 * 1024)
        except Exception:
            pass
        total_secs += dur
        if voice:
            voices.add(voice.split("(")[0].strip())
        entries.append({"idx": idx, "name": name, "voice": voice,
                        "ts": ts, "dur": dur, "file": fpath,
                        "content": content, "raw": it})
    st = getattr(self, "_proj_stats", [])
    if len(st) == 4:
        st[0].setText(str(len(entries)))
        hh = int(total_secs // 3600)
        mm = int((total_secs % 3600) // 60)
        st[1].setText("%dh %dm" % (hh, mm) if hh else "%dm" % mm)
        st[2].setText(str(len(voices)))
        st[3].setText("%.0f MB" % total_mb if total_mb < 1024
                      else "%.1f GB" % (total_mb / 1024))
    bar = getattr(self, "_proj_bar", None)
    if bar is not None:
        bar.setValue(min(100, int(total_mb / 10240 * 100)))

    def _age(e):
        try:
            return now - _dt.strptime(e["ts"], "%d/%m/%Y %H:%M:%S")
        except Exception:
            return _td(days=9999)
    pools = {
        "todos": entries,
        "recientes": [e for e in entries if _age(e) <= _td(days=7)],
        "favoritos": [e for e in entries if e["name"] in favs],
        "archivados": [e for e in entries if e["name"] in arch],
    }
    for b, kk in getattr(self, "_proj_tab_group", []):
        base_nm = {"todos": "Todos", "recientes": "Recientes",
                   "favoritos": "Favoritos",
                   "archivados": "Archivados"}[kk]
        b.setText("%s (%d)" % (base_nm, len(pools[kk])))
    pool = pools[getattr(self, "_proj_tab", "todos")]
    q = getattr(self, "_psearch", "")
    if q:
        pool = [e for e in pool if q in e["name"].lower()
                or q in e["content"].lower()]
    fd = getattr(self, "_proj_filter_dur", "todas")
    if fd == "cortas":
        pool = [e for e in pool if e["dur"] < 60]
    elif fd == "medias":
        pool = [e for e in pool if 60 <= e["dur"] <= 300]
    elif fd == "largas":
        pool = [e for e in pool if e["dur"] > 300]
    fv = getattr(self, "_proj_filter_voice", "todas")
    if fv != "todas":
        pool = [e for e in pool if e["voice"].split("(")[0].strip() == fv]
    so = getattr(self, "_proj_sort", None)
    mode = so.currentText() if so is not None else "M\u00e1s recientes"
    if mode == "M\u00e1s antiguos":
        pool.sort(key=lambda e: e["ts"])
    elif mode == "Nombre":
        pool.sort(key=lambda e: e["name"].lower())
    elif mode == "Duraci\u00f3n":
        pool.sort(key=lambda e: -e["dur"])
    else:
        pool.sort(key=lambda e: e["ts"], reverse=True)
    per = 6
    total = len(pool)
    pages = max(1, (total + per - 1) // per)
    self._proj_page_num = min(getattr(self, "_proj_page_num", 0), pages - 1)
    start = self._proj_page_num * per
    chunk = pool[start:start + per]
    for e in chunk:
        lay.addWidget(self._proj_row(e, favs))
    if not chunk:
        emp = QLabel("A\u00fan no hay proyectos exportados.\n"
                     "Convierte y exporta tu primer audio en Inicio.")
        emp.setStyleSheet("color: #8b93b0; font-size: 13px; padding: 40px;")
        emp.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(emp)
    lay.addStretch(1)
    end = min(total, start + per)
    info = getattr(self, "_proj_info", None)
    if info is not None:
        if total:
            info.setText("Mostrando %d a %d de %d proyectos"
                         % (start + 1, end, total))
        else:
            info.setText("Mostrando 0 a 0 de 0 proyectos")
    nums = getattr(self, "_proj_nums", None)
    if nums is not None:
        while nums.count():
            it = nums.takeAt(0)
            if it.widget():
                it.widget().deleteLater()
        for i in range(pages):
            pb = QPushButton(str(i + 1))
            pb.setFixedSize(36, 36)
            pb.setCursor(Qt.CursorShape.PointingHandCursor)
            if i == self._proj_page_num:
                pb.setStyleSheet(
                    "QPushButton { background: #7c5cff; color: white;"
                    " border: none; border-radius: 10px; font-weight: 700; }")
            else:
                pb.setStyleSheet(
                    "QPushButton { background: rgba(13,17,26,160);"
                    " color: #8b93b0; border: 1px solid #232f4b;"
                    " border-radius: 10px; }"
                    " QPushButton:hover { border: 1px solid #7c5cff; }")
            pb.clicked.connect(
                lambda _=False, ii=i: (
                    setattr(self, "_proj_page_num", ii),
                    self._rebuild_projects()))
            nums.addWidget(pb)
    prev = getattr(self, "_proj_prev", None)
    nxt = getattr(self, "_proj_next", None)
    if prev is not None:
        prev.setEnabled(self._proj_page_num > 0)
    if nxt is not None:
        nxt.setEnabled(self._proj_page_num < pages - 1)


MainWindow._layout_proj_bg = _layout_proj_bg
MainWindow._set_proj_tab = _set_proj_tab
MainWindow._proj_page_go = _proj_page_go
MainWindow._proj_fmt_dur = _proj_fmt_dur
MainWindow._proj_play = _proj_play
MainWindow._proj_menu = _proj_menu
MainWindow._proj_row = _proj_row
MainWindow._rebuild_projects = _rebuild_projects
MainWindow._register_export_success = _register_export_success
MainWindow._proj_toggle = _proj_toggle
MainWindow._proj_state_changed = _proj_state_changed
MainWindow._proj_dur_of = _proj_dur_of


def _audio_dur(self, path):
    try:
        if str(path).lower().endswith(".wav"):
            import wave
            with wave.open(str(path)) as wv:
                return wv.getnframes() / float(wv.getframerate())
    except Exception:
        pass
    return 0.0


MainWindow._audio_dur = _audio_dur


def _proj_open_filter(self, btn):
    from PySide6.QtWidgets import QMenu
    m = QMenu(self)
    m.setStyleSheet(
        "QMenu { background: #10141f; color: #e6edf3;"
        " border: 1px solid #232f4b; border-radius: 10px; }"
        " QMenu::item { padding: 8px 18px; }"
        " QMenu::item:selected { background: rgba(124,92,255,40); }")
    md = m.addMenu("Duraci\u00f3n")
    md.setStyleSheet(m.styleSheet())
    cur_d = getattr(self, "_proj_filter_dur", "todas")
    for key, label in [("todas", "Todas"), ("cortas", "Cortas (<1 min)"),
                       ("medias", "Medias (1-5 min)"),
                       ("largas", "Largas (>5 min)")]:
        a = md.addAction(label)
        a.setCheckable(True)
        a.setChecked(cur_d == key)
        a.triggered.connect(
            lambda _=False, kk=key: (
                setattr(self, "_proj_filter_dur", kk),
                self._rebuild_projects()))
    mv = m.addMenu("Voz")
    mv.setStyleSheet(m.styleSheet())
    cur_v = getattr(self, "_proj_filter_voice", "todas")
    voces = sorted({e["voice"].split("(")[0].strip()
                    for e in getattr(self, "_proj_items", [])
                    if e["voice"]})
    av = mv.addAction("Todas")
    av.setCheckable(True)
    av.setChecked(cur_v == "todas")
    av.triggered.connect(
        lambda: (setattr(self, "_proj_filter_voice", "todas"),
                 self._rebuild_projects()))
    for v in voces:
        a = mv.addAction(v)
        a.setCheckable(True)
        a.setChecked(cur_v == v)
        a.triggered.connect(
            lambda _=False, vv=v: (
                setattr(self, "_proj_filter_voice", vv),
                self._rebuild_projects()))
    m.exec(btn.mapToGlobal(QPoint(0, btn.height())))


MainWindow._proj_open_filter = _proj_open_filter


def _quick_toggle_theme(self):
    from PySide6.QtWidgets import QMessageBox
    cur = str(self.settings.get("theme", "Oscuro"))
    sel = "Claro" if cur != "Claro" else "Oscuro"
    self.settings["theme"] = sel
    self.settings["dark_mode"] = (sel != "Claro")
    try:
        from ui.modern_window import save_settings as _ss
        _ss(self.settings)
    except Exception:
        try:
            save_settings(self.settings)
        except Exception:
            pass
    want_light = (sel == "Claro")
    if want_light != bool(globals().get("LIGHT_MODE", False)):
        mb = QMessageBox(self)
        mb.setWindowTitle("Tema")
        mb.setText("El cambio de tema se aplica al reiniciar."
                   " \u00bfReiniciar ahora?")
        _yes = mb.addButton("S\u00ed", QMessageBox.ButtonRole.YesRole)
        _no = mb.addButton("No", QMessageBox.ButtonRole.NoRole)
        mb.setDefaultButton(_no)
        mb.setStyleSheet(
            "QMessageBox { background: #0d1220; }"
            " QMessageBox QLabel { color: #e6edf3; font-size: 13px; }"
            " QMessageBox QPushButton { background: #1a2138; color: #e6edf3;"
            " border: 1px solid #232f4b; border-radius: 9px;"
            " padding: 8px 22px; font-weight: 600; font-size: 12px;"
            " min-width: 70px; }"
            " QMessageBox QPushButton:hover { border: 1px solid #7c5cff;"
            " background: #232f4b; }"
            " QMessageBox QPushButton:default { border: 1px solid #7c5cff;"
            " color: #c4b5fd; }")
        for _lb in mb.findChildren(QLabel):
            _lb.setWordWrap(True)
            _lb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mb.exec()
        if mb.clickedButton() is _yes:
            self._restart_app()


MainWindow._quick_toggle_theme = _quick_toggle_theme


def _restart_app(self):
    import sys
    from PySide6.QtCore import QProcess
    from PySide6.QtWidgets import QApplication
    QProcess.startDetached(sys.executable, [sys.argv[0]])
    QApplication.instance().quit()

MainWindow._restart_app = _restart_app
MainWindow._open_lang_dialog = _open_lang_dialog


def _select_voice_wrapped(self, name):
    _ORIG_SELECT(self, name)
    try:
        self._refresh_card_states()
    except Exception:
        pass


def _toggle_fav_wrapped(self, name):
    _ORIG_FAV(self, name)
    try:
        if getattr(self, "_vtab", "todas") == "favoritas" and getattr(
                self, "_voc_built", False):
            self._rebuild_voices_page()
        else:
            self._refresh_card_states()
    except Exception:
        pass



MainWindow._load_voices = _load_voices
MainWindow._on_combo_voice = _on_combo_voice
MainWindow._select_voice = _select_voice
MainWindow._toggle_fav = _toggle_fav
MainWindow.update_counter = update_counter
MainWindow._copy_text = _copy_text
MainWindow._open_document_dialog = _open_document_dialog
MainWindow._toggle_adv = _toggle_adv
MainWindow._auto_text_height = _auto_text_height
MainWindow._animate_text_height = _animate_text_height
MainWindow._plan_char_limit = _plan_char_limit
MainWindow._show_limit_hint = _show_limit_hint
MainWindow._fade_limit_hint = _fade_limit_hint
MainWindow._show_limit_overlay = _show_limit_overlay
MainWindow._fade_limit_overlay = _fade_limit_overlay
MainWindow._update_counter = update_counter
MainWindow._on_text_limited = _on_text_limited
MainWindow._update_counter_safe = _update_counter_safe
MainWindow._toggle_theme_msg = _toggle_theme_msg
MainWindow._fmt_time = _fmt_time
MainWindow._tick_player = _tick_player
MainWindow.speak_text = speak_text
MainWindow.stop_speech = stop_speech
MainWindow._show_export_menu = _show_export_menu
MainWindow.export_wav = export_wav
MainWindow.export_mp3 = export_mp3
MainWindow._run_export = _run_export
MainWindow._concat_wavs = _concat_wavs
MainWindow._run_export_expressive = _run_export_expressive
MainWindow.on_export_ok = on_export_ok
MainWindow.on_export_error = on_export_error
MainWindow._load_history = _load_history
MainWindow.clear_history = clear_history
MainWindow._add_to_history = _add_to_history
MainWindow.open_support = open_support
MainWindow.show_help = show_help
MainWindow._check_license = _check_license
MainWindow._refresh_prem_card = _refresh_prem_card
MainWindow._open_license_dialog = _open_license_dialog
MainWindow.showEvent = showEvent
MainWindow.closeEvent = closeEvent
MainWindow._current_voice = _current_voice


def eventFilter(self, obj, event):
    try:
        from PySide6.QtCore import QEvent
        if obj is getattr(self, "_chat_page", None) and \
                event.type() == QEvent.Type.Resize:
            self._layout_chat_bg()
        if obj is getattr(self, "_proj_page", None) and \
                event.type() == QEvent.Type.Resize:
            self._layout_proj_bg()
    except Exception:
        pass
    from PySide6.QtCore import QEvent
    if obj is getattr(self, "voice_combo", None) and event.type() in (
            QEvent.Type.Resize, QEvent.Type.Polish, QEvent.Type.Show):
        h = self.voice_combo.height()
        badge = getattr(self, "pro_badge", None)
        if badge is not None:
            badge.move(max(0, self.voice_combo.width() - 78),
                       (h - 22) // 2)
    return QMainWindow.eventFilter(self, obj, event)


MainWindow.eventFilter = eventFilter


class PreviewWorker(QThread):
    """Hilo UNICO y persistente: reutiliza una instancia SAPI."""
    preview_done = Signal(str)

    def __init__(self):
        super().__init__()
        import queue
        self._q = queue.Queue()
        self._stopflag = False
        self._voice_cache = {}  # Cache para evitar iterar 300+ voces
        self._voice_cache = {}  # Caché para evitar iterar 300+ voces

    def request(self, desc):
        self._stopflag = True
        while not self._q.empty():
            try:
                self._q.get_nowait()
            except Exception:
                break
        self._stopflag = False
        self._q.put(desc)

    def request_stop(self):
        self._stopflag = True
        while not self._q.empty():
            try:
                self._q.get_nowait()
            except Exception:
                break

    def shutdown(self):
        self.request_stop()
        self._q.put(None)

    def run(self):
        import pythoncom
        import win32com.client
        import queue as _q
        pythoncom.CoInitialize()
        sapi = None
        try:
            sapi = win32com.client.Dispatch("SAPI.SpVoice")
        except Exception:
            sapi = None
        while True:
            try:
                item = self._q.get(timeout=0.2)
            except _q.Empty:
                continue
            if item is None:
                break
            try:
                if sapi is not None:
                    tok = self._voice_cache.get(item)
                    if tok is None:
                        for tk in sapi.GetVoices():
                            if tk.GetDescription() == item:
                                tok = tk
                                self._voice_cache[item] = tok
                                break
                    if tok is not None:
                        sapi.Voice = tok
                        sapi.Speak("Hola esta es mi voz", 1)
                        saw = False
                        for _ in range(300):
                            if self._stopflag:
                                sapi.Speak("", 2)
                                break
                            st = int(sapi.Status.RunningState)
                            if st == 2:
                                saw = True
                            elif saw:
                                break
                            self.msleep(100)
            except Exception:
                pass
            self.preview_done.emit(item)
        try:
            pythoncom.CoUninitialize()
        except Exception:
            pass


def _get_preview_worker(self):
    w = getattr(self, "_preview_worker", None)
    if w is None:
        w = PreviewWorker()
        w.preview_done.connect(self._on_preview_finished)
        self._preview_worker = w
        w.start()
    return w


def _on_preview_finished(self, name):
    self._preview_playing = False
    old = getattr(self, "_preview_name", "")
    self._preview_name = ""
    if old:
        self.preview_changed.emit(old, False)
    if getattr(self, "_preview_paused_main", False):
        self._preview_paused_main = False
        try:
            import time as _time
            self.engine.adapter.sapi.Resume()
            self._paused = False
            self._resume_at = _time.time()
            self.player_timer.start(50)
            self._set_player_icon(True, loading=False)
            self.statusBar().showMessage("Reanudando reproduccion...")
        except Exception:
            pass


def _toggle_preview(self, name):
    if name in getattr(self, "_cloned_set", set()):
        self._play_cloned_preview(name)
        return
    if getattr(self, "_preview_name", "") == name and getattr(
            self, "_preview_playing", False):
        self._get_preview_worker().request_stop()
        return
    if getattr(self, "_started", False) and not getattr(
            self, "_paused", False):
        try:
            self.engine.adapter.sapi.Pause()
            self._paused = True
            self._preview_paused_main = True
            self.player_timer.stop()
            self._set_player_icon(False)
            self.statusBar().showMessage(
                "Reproduccion pausada por previsualizacion.")
        except Exception:
            pass
    w = self._get_preview_worker()
    self._preview_name = name
    self._preview_playing = True
    self.preview_changed.emit(name, True)
    self.statusBar().showMessage(f"Previsualizando: {_clean_voice_name(name)}")
    w.request(name)


def _stop_preview(self):
    w = getattr(self, "_preview_worker", None)
    if w is not None:
        w.request_stop()



def _check_preview_end(self):
    return



def _player_play_clicked(self):
    if not getattr(self, "_started", False):
        self.speak_text()
        return
    texto = getattr(self, "_texto_para_ratio", "")
    voz = self.voice_combo.currentText().strip()
    if getattr(self, "_last_synth_key", None) != (voz, texto):
        self.speak_text()
        return
    try:
        sapi = self.engine.adapter.sapi
        if getattr(self, "_paused", False):
            sapi.Resume()
            self._paused = False
            import time as _time
            self._resume_at = _time.time()
            self.player_timer.start(50)
            self._set_player_icon(True, loading=False)
            self.statusBar().showMessage("Reanudando reproduccion...")
        else:
            sapi.Pause()
            self._paused = True
            self.player_timer.stop()
            self._set_player_icon(False)
            self.statusBar().showMessage("Reproduccion pausada.")
    except Exception as exc:
        self.statusBar().showMessage(f"Error en pausa: {exc}")



def _set_player_icon(self, playing, loading=False):
    if loading:
        self._spin_angle = 0
        if getattr(self, "_spin_timer", None) is None:
            self._spin_timer = QTimer(self)
            self._spin_timer.timeout.connect(self._spin_tick)
        self._draw_spin()
        self._spin_timer.start(60)
    else:
        st = getattr(self, "_spin_timer", None)
        if st is not None:
            st.stop()
        self.player_play.icon.setPixmap(
            make_icon("pause" if playing else "play", TEXT, 15))

def _spin_tick(self):
    self._spin_angle = (getattr(self, "_spin_angle", 0) + 40) % 360
    self._draw_spin()

def _draw_spin(self):
    from PySide6.QtGui import QPainter, QPen
    from PySide6.QtCore import QRectF
    pix = QPixmap(16, 16)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(QPen(QColor(TEXT), 2))
    p.drawArc(QRectF(1, 1, 14, 14),
              getattr(self, "_spin_angle", 0) * 16, 300 * 16)
    p.end()
    self.player_play.icon.setPixmap(pix)


MainWindow._player_play_clicked = _player_play_clicked


def _on_slider_pressed(self):
    self._seeking = True


def _on_slider_released(self):
    self._seeking = False
    if not getattr(self, "_started", False):
        return
    texto = getattr(self, "_texto_para_ratio", "") or \
        self.text_edit.toPlainText()
    if not texto:
        return
    ratio = self.progress_slider.value() / 100.0
    off = int(ratio * len(texto))
    if 0 < off < len(texto):
        nxt = texto.find(" ", off)
        off = (nxt + 1) if nxt != -1 else off
    off = max(0, min(off, len(texto) - 1))
    sub = texto[off:]
    if not sub.strip():
        return
    try:
        self.engine.stop()
        self._seg_queue = []  # seg-clear
    except Exception:
        pass
    import time as _time
    self._resume_offset = off
    self._saw_running = False
    self._paused = False
    self._resume_at = _time.time()
    self._seconds = ratio * max(1.0, getattr(self, "_est_seconds", 1.0))
    self.engine.speak_async(self._tts_text(sub))
    self.player_timer.start(50)
    self._set_player_icon(True, loading=False)
    self.statusBar().showMessage(
        f"Reproduciendo desde {self._fmt_time(self._seconds)}")


def _on_slider_moved(self, pos):
    if getattr(self, "_media_ready", False):
        dur = self.player.duration()
        if dur > 0:
            self.player.setPosition(int(pos * dur / 100))

def _on_volume_changed(self, value):
    try:
        self.audio_out.setVolume(value / 100.0)
    except Exception:
        pass
    try:
        self.engine.set_volume(value)
    except Exception:
        pass



def _center_on_screen(widget):
    from PySide6.QtWidgets import QApplication
    screen = QApplication.primaryScreen()
    if screen is None:
        return
    geo = screen.availableGeometry()
    x = geo.x() + (geo.width() - widget.width()) // 2
    y = geo.y() + (geo.height() - widget.height()) // 2
    widget.move(QPoint(x, y))


MainWindow._center_on_screen = staticmethod(_center_on_screen)


class VoiceSelectWorker(QThread):
    done = Signal(str)

    def __init__(self, adapter, name):
        super().__init__()
        self.adapter = adapter
        self.name = name

    def run(self):
        import pythoncom
        pythoncom.CoInitialize()
        try:
            self.adapter.set_voice(self.name)
        except Exception:
            pass
        finally:
            pythoncom.CoUninitialize()
        self.done.emit(self.name)


def _on_voice_loaded(self, name):
    if name == getattr(self, "_selected_voice", ""):
        self.statusBar().showMessage(f"Voz lista: {_clean_voice_name(name)}")


def _deferred_rebuilds(self):
    for w in self.findChildren(VoiceCard):
        sel = (w.voice_name == self._selected_voice)
        if getattr(w, "_is_sel", None) != sel:
            w._is_sel = sel
            w.set_selected(sel)


def _deferred_license(self):
    # Solo suprimir el dialogo de licencia si YA hay licencia valida.
    # En instalaciones nuevas (sin license.json) siempre se pide clave.
    try:
        state, _d = license_manager.check_status()
    except Exception:
        state = "trial"
    self._suppress_license_dialog = (state == "licensed")
    if not self._check_license():
        self.close()


_orig_avatar = MainWindow._avatar_pixmap


def _avatar_pixmap_cached(self, name, *args, **kwargs):
    cache = self.__dict__.setdefault("_avatar_cache", {})
    key = (name, args, tuple(sorted(kwargs.items())))
    if key in cache:
        return cache[key]
    pix = _orig_avatar(self, name, *args, **kwargs)
    cache[key] = pix
    return pix


MainWindow._avatar_pixmap = _avatar_pixmap_cached
MainWindow._on_voice_loaded = _on_voice_loaded
MainWindow._deferred_rebuilds = _deferred_rebuilds
MainWindow._deferred_license = _deferred_license

MainWindow._append_rec_cards = _append_rec_cards
MainWindow._append_all_cards = _append_all_cards


def _chunk_icons(self):
    if not getattr(self, "_icon_queue", None):
        self._icon_timer.stop()
        return
    batch = self._icon_queue[:40]
    self._icon_queue = self._icon_queue[40:]
    for idx in batch:
        v = self.voice_combo.itemData(idx, Qt.ItemDataRole.UserRole)
        if v:
            self.voice_combo.setItemIcon(idx, QIcon(self._avatar_pixmap(v)))
    if not self._icon_queue:
        self._icon_timer.stop()


MainWindow._chunk_icons = _chunk_icons


from PySide6.QtWidgets import (QDialog, QPlainTextEdit,
    QProgressBar)


from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput


class UpdateWorker(QThread):
    found = Signal(object)
    none = Signal()

    def run(self):
        try:
            from core import updater
            info = updater.check_update()
            if info:
                self.found.emit(info)
            else:
                self.none.emit()
        except Exception:
            self.none.emit()


class DownloadWorker(QThread):
    progress = Signal(int)
    ok = Signal(str)
    fail = Signal(str)

    def __init__(self, url, dest):
        super().__init__()
        self.url = url
        self.dest = dest

    def run(self):
        try:
            import urllib.request
            req = urllib.request.Request(
                self.url, headers={"User-Agent": "WillpoVoice"})
            with urllib.request.urlopen(req, timeout=60) as r, \
                    open(self.dest, "wb") as f:
                total = int(r.headers.get("Content-Length", 0))
                got = 0
                while True:
                    chunk = r.read(65536)
                    if not chunk:
                        break
                    f.write(chunk)
                    got += len(chunk)
                    if total:
                        self.progress.emit(int(got * 100 / total))
            self.ok.emit(self.dest)
        except Exception as exc:
            self.fail.emit(str(exc))


class UpdateDialog(QDialog):
    def __init__(self, parent, info):
        super().__init__(parent)
        self.info = info
        CARD = "#141922"
        BORDER = "#262d3a"
        TEXT = "#e6edf3"
        MUTED = "#8b949e"
        PURPLE = "#7c5cff"
        self.setWindowTitle("Actualizacion disponible")
        self.setModal(True)
        self.setFixedWidth(480)
        self.setStyleSheet(
            f"UpdateDialog {{ background: #0b0f17; }} QLabel {{ color: {TEXT}; }}"
        )
        lay = QVBoxLayout(self)
        lay.setContentsMargins(26, 22, 26, 20)
        lay.setSpacing(10)
        t1 = QLabel(f"Nueva version disponible:  {info['version']}")
        t1.setStyleSheet("font-size: 16px; font-weight: 700;")
        lay.addWidget(t1)
        notes = QPlainTextEdit()
        notes.setReadOnly(True)
        notes.setPlainText(info["notes"])
        notes.setFixedHeight(140)
        notes.setStyleSheet(
            f"QPlainTextEdit {{ background: {CARD}; color: {MUTED};"
            f" border: 1px solid {BORDER}; border-radius: 10px;"
            " padding: 10px; font-size: 11px; }"
        )
        lay.addWidget(notes)
        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setValue(0)
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(8)
        self.bar.hide()
        lay.addWidget(self.bar)
        self.status = QLabel("")
        self.status.setStyleSheet(f"color: {MUTED}; font-size: 10.5px;")
        lay.addWidget(self.status)
        row = QHBoxLayout()
        row.setSpacing(10)
        self.dl_btn = QPushButton("Descargar e instalar")
        self.dl_btn.setFixedHeight(42)
        self.dl_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.dl_btn.setStyleSheet(
            "QPushButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f" stop:0 #6d5df0, stop:1 {PURPLE}); color: white; border: none;"
            " border-radius: 10px; font-size: 13px; font-weight: 700; }"
            " QPushButton:hover { background: #8d75ff; }"
            " QPushButton:disabled { background: #333a4a; }"
        )
        self.dl_btn.clicked.connect(self.start_download)
        row.addWidget(self.dl_btn, 1)
        later = QPushButton("Ahora no")
        later.setFixedHeight(42)
        later.setCursor(Qt.CursorShape.PointingHandCursor)
        later.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {MUTED};"
            f" border: 1px solid {BORDER}; border-radius: 10px;"
            " font-size: 13px; font-weight: 600; }"
            f" QPushButton:hover {{ color: {TEXT}; }}"
        )
        later.clicked.connect(self.reject)
        row.addWidget(later, 1)
        lay.addLayout(row)

    def start_download(self):
        import tempfile
        from pathlib import Path as _P
        ver = "".join(c for c in self.info["version"] if c.isalnum() or c == ".")
        dest = str(_P(tempfile.gettempdir()) / f"WillpoVoice-Setup-{ver}.exe")
        self.dl_btn.setEnabled(False)
        self.bar.show()
        self.status.setText("Descargando actualizacion...")
        self._dl = DownloadWorker(self.info["url"], dest)
        self._dl.progress.connect(self.bar.setValue)
        self._dl.ok.connect(self.install_and_quit)
        self._dl.fail.connect(self.on_fail)
        self._dl.start()

    def on_fail(self, msg):
        self.status.setText("Error al descargar: " + msg)
        self.dl_btn.setEnabled(True)

    def install_and_quit(self, path):
        import ctypes
        from PySide6.QtWidgets import QApplication
        self.status.setText("Instalando... la app se cerrara.")
        args = "/VERYSILENT /SUPPRESSMSGBOXES /NORESTART"
        ret = ctypes.windll.shell32.ShellExecuteW(
            None, "runas", path, args, None, 1)
        if ret > 32:
            QApplication.quit()
        else:
            self.status.setText("Instalacion cancelada por el usuario.")
            self.dl_btn.setEnabled(True)


def _check_updates(self):
    self._update_worker = UpdateWorker()
    self._update_worker.found.connect(self._on_update_found)
    self._update_worker.start()


def _on_update_found(self, info):
    dlg = UpdateDialog(self, info)
    dlg.exec()


MainWindow._check_updates = _check_updates
MainWindow._on_update_found = _on_update_found

MainWindow._on_position_changed = _on_position_changed

MainWindow._on_duration_changed = _on_duration_changed

MainWindow._on_media_status_changed = _on_media_status_changed

MainWindow._on_slider_moved = _on_slider_moved

MainWindow._on_volume_changed = _on_volume_changed

MainWindow._on_synth_ready = _on_synth_ready

MainWindow._on_synth_error = _on_synth_error

MainWindow._spin_tick = _spin_tick

MainWindow._draw_spin = _draw_spin

MainWindow._set_player_icon = _set_player_icon

MainWindow._on_preview_finished = _on_preview_finished

MainWindow._load_entry = _load_entry
MainWindow._delete_entry = _delete_entry

def _play_cloned_preview(self, name):
    """Genera y reproduce una muestra con la voz clonada (con caché WAV)"""
    self._set_card_spin(name, True)
    if getattr(self, "_prev_player", None):
        try:
            self._prev_player.stop()
        except Exception:
            pass
    # Buscar WAV pregrabado en voices/previews/<name>.wav
    preview_dir = _cloned_preview_dir()
    preview_dir.mkdir(parents=True, exist_ok=True)
    cached = preview_dir / (name + ".wav")
    if cached.exists():
        print(f"▶ Preview instantáneo desde caché: {cached.name}")
        self._on_cloned_preview_ready(str(cached))
        return
    # Primera vez: generar y cachear
    if getattr(self, "_cloned_preview_worker", None) and self._cloned_preview_worker.isRunning():
        self._cloned_preview_worker.quit()
        self._cloned_preview_worker.wait()
    sample = "Hola, esta es mi voz. Soy Alfredo, tu narrador ultrarrealista."
    self._cloned_preview_name = name
    self._cloned_preview_worker = _ClonedPreviewWorker(name, sample, self)
    self._cloned_preview_worker.done.connect(self._on_cloned_preview_cached)
    self._cloned_preview_worker.failed.connect(self._on_cloned_preview_failed)
    self._cloned_preview_worker.start()

def _on_cloned_preview_cached(self, wav_path):
    """Guarda el WAV en caché y lo reproduce"""
    preview_dir = _cloned_preview_dir()
    preview_dir.mkdir(parents=True, exist_ok=True)
    cached = preview_dir / (Path(wav_path).stem.replace("_cloned", "") + ".wav")
    try:
        import shutil
        shutil.copy2(wav_path, str(cached))
        print(f"💾 Preview cacheado: {cached.name}")
    except Exception:
        pass
    self._on_cloned_preview_ready(wav_path)


def _on_cloned_preview_ready(self, wav_path):
    """Reproduce el WAV generado con QMediaPlayer"""
    name = getattr(self, "_cloned_preview_name", "") or getattr(self, "_preview_name", "") or getattr(self, "_selected_cloned", "")
    if name:
        self._set_card_spin(name, False)
    from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
    from PySide6.QtCore import QUrl
    if not hasattr(self, "_prev_player"):
        self._prev_player = QMediaPlayer(self)
        self._prev_audio = QAudioOutput(self)
        self._prev_player.setAudioOutput(self._prev_audio)
    self._prev_player.stop()
    self._prev_player.setSource(QUrl.fromLocalFile(wav_path))
    self._prev_player.play()


def _on_cloned_preview_failed(self, err):
    name = getattr(self, "_cloned_preview_name", "") or getattr(self, "_preview_name", "") or getattr(self, "_selected_cloned", "")
    if name:
        self._set_card_spin(name, False)
    print(f"Error en preview clonada: {err}")


def _tts_cloned(self, voice_name, text):
    """Genera audio completo con voz clonada en hilo separado"""
    if getattr(self, "_cloned_tts_worker", None) and self._cloned_tts_worker.isRunning():
        return
    self._set_player_icon(True, loading=True)
    self.statusBar().showMessage("Generando audio con voz clonada...")
    self._cloned_tts_worker = _ClonedPreviewWorker(voice_name, text, self)
    self._cloned_tts_worker.done.connect(self._on_tts_cloned_done)
    self._cloned_tts_worker.failed.connect(self._on_tts_cloned_failed)
    self._cloned_tts_worker.start()


def _on_tts_cloned_done(self, wav_path):
    """Reproduce el audio generado completo"""
    from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
    from PySide6.QtCore import QUrl
    if not hasattr(self, "_tts_player"):
        self._tts_player = QMediaPlayer(self)
        self._tts_audio = QAudioOutput(self)
        self._tts_player.setAudioOutput(self._tts_audio)
    self._tts_player.stop()
    self._tts_player.setSource(QUrl.fromLocalFile(wav_path))
    self._tts_player.play()
    self._set_player_icon(True, loading=False)
    print(f"Audio clonado reproducido: {wav_path}")


def _on_tts_cloned_failed(self, err):
    self._set_player_icon(False)
    self.statusBar().showMessage(f"Error al generar con voz clonada: {err}")
    print(f"Error al generar con voz clonada: {err}")


def _export_cloned(self, text, path, is_mp3):
    """Exporta audio con voz clonada directamente a archivo (sin SAPI)"""
    if getattr(self, "_cloned_export_worker", None) and self._cloned_export_worker.isRunning():
        self.statusBar().showMessage("Ya hay una exportacion en curso...")
        return
    self._export_target = (path, is_mp3)
    self._last_cloned_text = text
    dlg = ExportProgressDialog(
        self, "Exportando MP3..." if is_mp3 else "Exportando WAV...")
    dlg.show()
    words = len(text.split()) or 1
    factor = 1.0 + self.rate_slider.value() / 20.0
    dlg.start_estimated(words / (1.6 * factor) + 2.0)
    dlg.set_status("Generando voz clonada (offline)...")
    self._cloned_export_dlg = dlg
    self.statusBar().showMessage("Generando audio con voz clonada...")
    self._cloned_export_worker = _ClonedPreviewWorker(self._selected_cloned, text, self)
    self._cloned_export_worker.done.connect(self._on_export_cloned_done)
    self._cloned_export_worker.failed.connect(self._on_export_cloned_failed)
    self._cloned_export_worker.start()


def _on_export_cloned_done(self, wav_path):
    """Copia o convierte el WAV generado al destino de exportacion"""
    import shutil
    path, is_mp3 = getattr(self, "_export_target", ("", False))
    dlg = getattr(self, "_cloned_export_dlg", None)
    try:
        if dlg is not None:
            dlg.set_progress(95, "Finalizando exportacion...")
        if is_mp3:
            from core.mp3_encoder import wav_to_mp3
            wav_to_mp3(wav_path, path)
        else:
            shutil.copy2(wav_path, path)
        if dlg is not None:
            dlg.finish()
            dlg.close()
            self._cloned_export_dlg = None
        self.statusBar().showMessage(f"Audio exportado: {path}")
        print(f"💾 Audio clonado exportado: {path}")
        _ct = str(getattr(self, "_last_cloned_text", "") or "")
        _cv = str(getattr(self, "_selected_cloned", "") or "")
        self._register_export_success(path, _ct, _cv)
    except Exception as e:
        if dlg is not None:
            dlg.close()
            self._cloned_export_dlg = None
        self.statusBar().showMessage(f"Error al exportar: {e}")
        print(f"⚠️ Error al exportar audio clonado: {e}")


def _on_export_cloned_failed(self, err):
    dlg = getattr(self, "_cloned_export_dlg", None)
    if dlg is not None:
        dlg.close()
        self._cloned_export_dlg = None
    self.statusBar().showMessage(f"No se pudo exportar: {err}")
    print(f"⚠️ Error en exportacion clonada: {err}")


def _set_card_spin(self, name, on):
    """Activa/desactiva un spinner sobre el PreviewPhoto de la tarjeta"""
    cards = getattr(self, "_cards_by_name", {})
    card = cards.get(name)
    if card is None:
        return
    photo = getattr(card, "photo", None)
    if photo is None:
        return
    overlay = getattr(card, "_spin_overlay", None)
    timer = getattr(card, "_spin_timer", None)

    if on:
        if overlay is None:
            from PySide6.QtWidgets import QLabel
            from PySide6.QtCore import Qt, QTimer
            overlay = QLabel(photo)
            overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            overlay.setStyleSheet("background: transparent;")
            overlay.setGeometry(0, 0, photo.width(), photo.height())
            overlay.show()
            overlay.raise_()
            card._spin_overlay = overlay
            card._spin_angle = 0

            def _tick():
                from PySide6.QtGui import QPainter, QPen, QColor
                from PySide6.QtCore import QRectF
                card._spin_angle = (card._spin_angle + 40) % 360
                pix = overlay.pixmap()
                if pix is None or pix.isNull() or pix.size() != overlay.size():
                    from PySide6.QtGui import QPixmap
                    pix = QPixmap(overlay.size())
                pix.fill(Qt.GlobalColor.transparent)
                p = QPainter(pix)
                p.setRenderHint(QPainter.RenderHint.Antialiasing)
                p.setPen(QPen(QColor("#7c5cff"), 3))
                w, h = pix.width(), pix.height()
                side = min(w, h) - 4
                x = (w - side) // 2
                y = (h - side) // 2
                p.drawArc(QRectF(x, y, side, side),
                          card._spin_angle * 16, 300 * 16)
                p.end()
                overlay.setPixmap(pix)

            card._spin_tick = _tick
            timer = QTimer(card)
            timer.timeout.connect(_tick)
            timer.start(60)
            card._spin_timer = timer
            _tick()
        else:
            overlay.show()
            overlay.raise_()
            if timer and not timer.isActive():
                timer.start(60)
    else:
        if overlay is not None:
            overlay.hide()
        if timer is not None and timer.isActive():
            timer.stop()


MainWindow._set_card_spin = _set_card_spin
def _cloned_preview_dir():
    """Carpeta de cache de previews en zona escribible del usuario"""
    import os
    base = os.environ.get("LOCALAPPDATA") or os.environ.get("TEMP") or str(Path.home())
    d = Path(base) / "WillpoVoice" / "previews"
    try:
        d.mkdir(parents=True, exist_ok=True)
    except Exception:
        import tempfile
        d = Path(tempfile.gettempdir()) / "WillpoVoice_previews"
        d.mkdir(parents=True, exist_ok=True)
    return d


MainWindow._toggle_preview = _toggle_preview
MainWindow._play_cloned_preview = _play_cloned_preview
MainWindow._on_cloned_preview_ready = _on_cloned_preview_ready
MainWindow._on_cloned_preview_cached = _on_cloned_preview_cached
MainWindow._on_cloned_preview_failed = _on_cloned_preview_failed
MainWindow._tts_cloned = _tts_cloned
MainWindow._on_tts_cloned_done = _on_tts_cloned_done
MainWindow._on_tts_cloned_failed = _on_tts_cloned_failed
MainWindow._export_cloned = _export_cloned
MainWindow._on_export_cloned_done = _on_export_cloned_done
MainWindow._on_export_cloned_failed = _on_export_cloned_failed

MainWindow._stop_preview = _stop_preview
MainWindow._check_preview_end = _check_preview_end
MainWindow._avatar_pixmap_cached = _avatar_pixmap_cached

MainWindow._get_preview_worker = _get_preview_worker

MainWindow._voice_lang = _voice_lang

MainWindow._lang_filtered = _lang_filtered


def _sort_key(self, name):
    low = (name or "").lower()
    if name in getattr(self, "_cloned_set", set()):
        return -1
    if "multilingual" in low:
        return 0
    try:
        vl = self._voice_lang(name)
    except Exception:
        vl = "otro"
    return 2 if vl == "es" else 1

MainWindow._sort_key = _sort_key

MainWindow._refill_combo = _refill_combo

MainWindow._on_lang_changed = _on_lang_changed

MainWindow._on_slider_pressed = _on_slider_pressed

MainWindow._on_slider_released = _on_slider_released

MainWindow._repair_engine = _repair_engine


def _trial_active(self):
    try:
        state, _ = license_manager.check_status()
        return state == "trial"
    except Exception:
        return False


def _trial_gate(self, text):
    return True

def _trial_spend(self, text):
    return

def _update_token_chip(self):
    txt = getattr(self, "_token_chip_text", None)
    if txt is None:
        return
    txt.setText("Plan Estándar")


def _refresh_token_chip(self, state):
    icon = getattr(self, "_token_chip_icon", None)
    txt = getattr(self, "_token_chip_text", None)
    if icon is None or txt is None:
        return
    wrap = getattr(self, "_token_chip_wrap", None)
    if state == "trial":
        trial_tokens.ensure_init()
        if wrap is not None:
            wrap.setVisible(True)
        icon.setVisible(True)
        txt.setVisible(True)
        txt.setText("Plan Estándar")
    else:
        if wrap is not None:
            wrap.setVisible(False)
        icon.setVisible(False)
        txt.setVisible(False)


def _show_no_tokens(self):
    from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                   QPushButton, QFrame)
    from PySide6.QtGui import (QDesktopServices, QPixmap, QPainter, QIcon,
                               QColor)
    from PySide6.QtCore import QUrl, QTimer, Qt, QByteArray, QSize
    from PySide6.QtSvg import QSvgRenderer
    import time
    import sys as _sys

    def _svg(path_data, color, size, rule="nonzero"):
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
               f'<path fill="{color}" fill-rule="{rule}" d="{path_data}"/></svg>')
        r = QSvgRenderer(QByteArray(svg.encode("utf-8")))
        pm = QPixmap(size, size)
        pm.fill(Qt.GlobalColor.transparent)
        p = QPainter(pm)
        r.render(p)
        p.end()
        return pm

    IC_WARN = "M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"
    IC_ZAP = "M13 2 3 14h9l-1 8 10-12h-9l1-8z"
    IC_SHIELD = ("M12 1 3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 "
                 "9-12V5l-9-4zm-2 16-4-4 1.41-1.41L10 14.17l6.59-6.59L18 "
                 "9l-8 8z")
    IC_GIFT = ("M20 6h-2.18c.11-.31.18-.65.18-1 0-1.66-1.34-3-3-3-1.05 0-"
               "1.96.54-2.5 1.35l-.5.67-.5-.68C10.96 2.54 10.05 2 9 2 7.34 "
               "2 6 3.34 6 5c0 .35.07.69.18 1H4c-1.11 0-1.99.89-1.99 2L2 "
               "19c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V8c0-1.11-.89-2-2-2zm-"
               "5-2c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zM9 4c.55 "
               "0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm11 15H4v-2h16v2z"
               "m0-5H4V8h5.08L7 10.83 8.62 12 11 8.76l1-1.36 1 1.36L15.38 "
               "12 17 10.83 14.92 8H20v6z")
    IC_TOKEN = ("M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm0 3a7 7"
                " 0 1 1 0 14 7 7 0 0 1 0-14zm-1 3h2v6h-2z")
    IC_MIC = ("M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 "
              "1.66 1.34 3 3 3zm5.3-3c0 3-2.54 5.1-5.3 5.1S6.7 14 6.7 11H5c0 "
              "3.41 2.72 6.23 6 6.72V21h2v-3.28c3.28-.48 6-3.3 6-6.72h-1.7z")
    IC_DOC = ("M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 2 2h12c1.1 0 "
              "2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 "
              "9H13z")
    IC_HEAD = ("M12 1c-4.97 0-9 4.03-9 9v7c0 1.66 1.34 3 3 3h3v-8H5v-2c0-"
               "3.87 3.13-7 7-7s7 3.13 7 7v2h-4v8h3c1.66 0 3-1.34 3-3v-7c0-"
               "4.97-4.03-9-9-9z")
    IC_WA = ("M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471"
             "-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644"
             ".075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653"
             "-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149"
             "-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669"
             "-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01"
             "-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 "
             "2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 "
             "4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118."
             "571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-"
             ".074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-"
             "5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 "
             "0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 "
             "1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 "
             "9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 "
             "0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305"
             "-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 "
             "11.893-11.893a11.821 11.821 0 00-3.485-8.413Z")
    IC_DC = ("M20.317 4.37a19.79 19.79 0 0 0-4.885-1.515.074.074 0 0 0-.079"
             ".037c-.21.375-.444.865-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64"
             " 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0"
             " 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099"
             " 18.058a.082.082 0 0 0 .031.056 19.9 19.9 0 0 0 5.993 3.03.078"
             ".078 0 0 0 .084-.028 14.09 14.09 0 0 0 1.226-1.994.076.076 0 0"
             " 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008"
             "-.128 10.2 10.2 0 0 0 .372-.291.074.074 0 0 1 .077-.01c3.928"
             " 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246"
             ".198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873"
             ".892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076"
             ".076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0"
             " 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031"
             "-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956"
             "-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956"
             " 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0"
             "-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0"
             " 1.333-.946 2.418-2.157 2.418Z")

    W, H = 560, 800
    d = QDialog(self)
    d.setModal(True)
    d.setFixedSize(W, H)
    d.setWindowTitle("Mejora tu plan")
    d.setStyleSheet(
        "QDialog { background: #0a0d12; }"
        " QLabel { background: transparent; border: none; }")

    # ---------- FONDO: tu imagen + overlay ----------
    bg = QLabel(d)
    bg.setGeometry(0, 0, W, H)
    bg.lower()
    pm = QPixmap(W, H)
    pm.fill(QColor("#0a0d12"))
    p = QPainter(pm)
    base = Path(getattr(_sys, "_MEIPASS",
                        Path(__file__).resolve().parents[1]))
    src = None
    for cand in ("assets/icons/tokens_bg.png", "assets/img/tokens_bg.png",
                 "assets/tokens_bg.png"):
        cp = base / cand
        if cp.exists():
            src = cp
            break
    if src is not None:
        scaled = QPixmap(str(src)).scaled(
            W, H, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation)
        p.drawPixmap((W - scaled.width()) // 2,
                     (H - scaled.height()) // 2, scaled)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor(10, 13, 18, 175))
    p.drawRect(0, 0, W, H)
    p.end()
    bg.setPixmap(pm)

    v = QVBoxLayout(d)
    v.setContentsMargins(30, 26, 30, 24)
    v.setSpacing(12)

    v.addSpacing(6)

    tbox = QVBoxLayout()
    tbox.setSpacing(0)
    t1 = QLabel("Compra")
    t1.setStyleSheet("color: #ffffff; font-size: 50px; font-weight: 900;")
    tbox.addWidget(t1)
    trow = QHBoxLayout()
    trow.setSpacing(1)
    _grad = ["#8b5cf6", "#7d6ffb", "#6f83fb", "#6196fc", "#53a9fc", "#45bcfd"]
    for _ch, _cc in zip("Tokens", _grad):
        _l = QLabel(_ch)
        _l.setStyleSheet(
            f"color: {_cc}; font-size: 50px; font-weight: 900;")
        trow.addWidget(_l)
    trow.addStretch(1)
    tbox.addLayout(trow)
    v.addLayout(tbox)
    sub = QLabel("Más caracteres, más posibilidades.\n"
                 "Convierte texto en voz sin l\u00edmites.")
    sub.setStyleSheet("color: #8b949e; font-size: 12px;")
    v.addWidget(sub)
    v.addSpacing(2)

    # ---------- 3 MINI CARDS ----------
    cards = QHBoxLayout()
    cards.setSpacing(10)
    for path, color, ctitle, cdesc, crule in [
        ("bolt", "#bc8cff", "M\u00e1s conversiones", "Convierte m\u00e1s texto en voz", "app"),
        (IC_SHIELD, "#58a6ff", "Seguro y r\u00e1pido", "Transacciones 100% seguras", "nonzero"),
        ("coins", "#f5b544", "Platinum", "20,000 caracteres por conversión", "app"),
    ]:
        fr = QFrame()
        fr.setObjectName("ntCard")
        fr.setStyleSheet(
            "#ntCard { background: rgba(22,27,34,200);"
            " border: 1px solid rgba(124,92,255,70); border-radius: 10px; }")
        fv = QVBoxLayout(fr)
        fv.setContentsMargins(12, 10, 12, 10)
        fv.setSpacing(5)
        icl = QLabel()
        if crule == "app":
            icl.setPixmap(make_icon(path, color, 18))
        else:
            icl.setPixmap(_svg(path, color, 18, crule))
        fv.addWidget(icl)
        ttl = QLabel(ctitle)
        ttl.setStyleSheet("color: #e6edf3; font-size: 11px; font-weight: 700;")
        fv.addWidget(ttl)
        dsc = QLabel(cdesc)
        dsc.setStyleSheet("color: #8b949e; font-size: 9.5px;")
        dsc.setWordWrap(True)
        fv.addWidget(dsc)
        cards.addWidget(fr)
    v.addLayout(cards)

    # ---------- OFERTA 24H ----------
    offer = QFrame()
    offer.setObjectName("ntOffer")
    offer.setStyleSheet(
        "#ntOffer { background: rgba(20,16,31,220);"
        " border: 1.5px solid #6b3fa8; border-radius: 14px; }")
    ov = QVBoxLayout(offer)
    ov.setContentsMargins(18, 14, 18, 14)
    ov.setSpacing(8)
    badge = QLabel("  OFERTA LIMITADA  \u00b7  24 HORAS")
    badge.setStyleSheet(
        "QLabel { background: #f5b544; color: #1a0f05; font-size: 10px;"
        " font-weight: 800; letter-spacing: 1.5px; padding: 4px 12px;"
        " border-radius: 4px; }")
    badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
    badge.setFixedHeight(22)
    ov.addWidget(badge, 0, Qt.AlignmentFlag.AlignCenter)
    oh = QLabel("Tu primer mes Pro al 50% de descuento")
    oh.setStyleSheet("color: #ffffff; font-size: 15px; font-weight: 700;")
    oh.setAlignment(Qt.AlignmentFlag.AlignCenter)
    ov.addWidget(oh)
    price_row = QHBoxLayout()
    price_row.setSpacing(10)
    price_row.addStretch(1)
    old_price = QLabel("S/ 30")
    old_price.setStyleSheet(
        "color: #8b949e; font-size: 20px; font-weight: 500;"
        " text-decoration: line-through;")
    price_row.addWidget(old_price)
    new_price = QLabel("S/ 5")
    new_price.setFixedHeight(44)
    new_price.setStyleSheet("color: #f5b544; font-size: 34px; font-weight: 900;")
    price_row.addWidget(new_price)
    price_row.addStretch(1)
    ov.addLayout(price_row)
    cd = QLabel("00:00:00")
    cd.setFixedHeight(58)
    cd.setAlignment(Qt.AlignmentFlag.AlignCenter)
    cd.setStyleSheet(
        "QLabel { background: #0a0d12; color: #ffffff; font-size: 26px;"
        " font-weight: 800; font-family: 'Consolas', monospace;"
        " border-radius: 8px; letter-spacing: 3px; }")
    ov.addWidget(cd)
    cd_label = QLabel("TIEMPO RESTANTE PARA APROVECHAR LA OFERTA")
    cd_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    cd_label.setStyleSheet("color: #8b949e; font-size: 9.5px; letter-spacing: 1.2px;")
    ov.addWidget(cd_label)
    v.addWidget(offer)

    # ---------- BOTONES ----------
    b_wa = QPushButton("  Comprar por WhatsApp  ")
    b_wa.setFixedHeight(44)
    b_wa.setCursor(Qt.CursorShape.PointingHandCursor)
    b_wa.setIcon(QIcon(_svg(IC_WA, "#ffffff", 20)))
    b_wa.setIconSize(QSize(20, 20))
    b_wa.setStyleSheet(
        "QPushButton { background: #25D366; color: white; border: none;"
        " border-radius: 10px; font-size: 13px; font-weight: 700; }"
        " QPushButton:hover { background: #20ba5a; }")
    v.addWidget(b_wa)
    b_dc = QPushButton("  Comprar por Discord  ")
    b_dc.setFixedHeight(38)
    b_dc.setCursor(Qt.CursorShape.PointingHandCursor)
    b_dc.setIcon(QIcon(_svg(IC_DC, "#ffffff", 20)))
    b_dc.setIconSize(QSize(20, 20))
    b_dc.setStyleSheet(
        "QPushButton { background: #5865F2; color: white; border: none;"
        " border-radius: 10px; font-size: 13px; font-weight: 600; }"
        " QPushButton:hover { background: #4752c4; }")
    v.addWidget(b_dc)
    b_lk = QPushButton("Ya tengo una clave de licencia")
    b_lk.setFixedHeight(28)
    b_lk.setCursor(Qt.CursorShape.PointingHandCursor)
    b_lk.setStyleSheet(
        "QPushButton { background: transparent; color: #8b949e; border: none;"
        " font-size: 11px; text-decoration: underline; }"
        " QPushButton:hover { color: #c9d1d9; }")
    v.addWidget(b_lk)

    b_wa.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(YAPE_URL_MENSUAL)))
    b_dc.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(DISCORD_URL)))
    b_lk.clicked.connect(lambda: (d.accept(), self._open_license_dialog()))

    offer_state = trial_tokens.get_offer()
    offer_id = "no_tokens_v1"
    if offer_state and offer_state.get("id") == offer_id:
        end_ts = int(offer_state["ts"]) + 86400
    else:
        end_ts = int(time.time()) + 86400
        trial_tokens.set_offer_claimed(offer_id)

    def tick():
        left = max(0, end_ts - int(time.time()))
        h, rem = divmod(left, 3600)
        m, s = divmod(rem, 60)
        cd.setText(f"{h:02d}:{m:02d}:{s:02d}" if left > 0 else "--:--:--")
    tick()
    timer = QTimer(d)
    timer.timeout.connect(tick)
    timer.start(1000)
    d.exec()


MainWindow._show_no_tokens = _show_no_tokens
MainWindow._trial_active = _trial_active
MainWindow._trial_gate = _trial_gate
MainWindow._trial_spend = _trial_spend
MainWindow._update_token_chip = _update_token_chip
MainWindow._refresh_token_chip = _refresh_token_chip


# ==== Canales de venta (llenalos cuando los tengas) ====
DISCORD_URL = "https://discord.gg/sq64dVJbDG"
YAPE_URL_MENSUAL = ""
YAPE_URL_LIFETIME = ""


class PaymentDialog(QDialog):
    def __init__(self, parent, plan, price, yape_url):
        super().__init__(parent)
        self.setModal(True)
        self.setFixedWidth(430)
        self.setWindowTitle("Comprar " + plan)
        self._plan = plan
        self.setStyleSheet("PaymentDialog { background: #0b0e14; }")
        v = QVBoxLayout(self)
        v.setContentsMargins(22, 14, 22, 14)
        v.setSpacing(8)
        ic = QLabel()
        ic.setPixmap(make_icon("smartphone", "#7c5cff", 42))
        ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(ic)
        t1 = QLabel("Plan " + plan)
        t1.setStyleSheet(
            "color: #e6edf3; font-size: 18px; font-weight: 800;")
        t1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(t1)
        t2 = QLabel("S/ " + str(price) + " · pago seguro con Yape")
        t2.setStyleSheet(
            "color: #f5b544; font-size: 13px; font-weight: 700;")
        t2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(t2)
        tit = QLabel("Titular: Anton Val*")
        tit.setStyleSheet("color: #c9d1d9; font-size: 11.5px;")
        tit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(tit)
        self._qr_wrap = QFrame()
        self._qr_wrap.setObjectName("qrwrap")
        self._qr_wrap.setStyleSheet(
            "#qrwrap { background: #ffffff; border-radius: 14px; }")
        qv = QVBoxLayout(self._qr_wrap)
        qv.setContentsMargins(10, 10, 10, 10)
        self._qr_label = QLabel()
        self._qr_label.setFixedSize(170, 170)
        qv.addWidget(self._qr_label)
        v.addWidget(self._qr_wrap, 0, Qt.AlignmentFlag.AlignCenter)
        self._load_qr()
        info = QLabel("Escanea el QR con tu app Yape y paga de forma "
                      "segura, sin necesidad de nuestro numero.")
        info.setStyleSheet("color: #8b949e; font-size: 11px;")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setWordWrap(True)
        v.addWidget(info)
        v.addSpacing(4)
        if yape_url:
            by = QPushButton("Pagar con Yape ahora")
            by.setFixedHeight(42)
            by.setCursor(Qt.CursorShape.PointingHandCursor)
            by.setStyleSheet(
                "QPushButton { background: qlineargradient(x1:0,y1:0,"
                "x2:1,y2:0, stop:0 #6d5df0, stop:0.5 #7c5cff,"
                " stop:1 #6d5df0); color: white; border: none;"
                " border-radius: 10px; font-weight: 700; }"
                " QPushButton:hover { background: #8d75ff; }")
            by.clicked.connect(
                lambda: QDesktopServices.openUrl(QUrl(yape_url)))
            v.addWidget(by)
        bd = QPushButton("Enviar comprobante por Discord")
        bd.setFixedHeight(42)
        bd.setCursor(Qt.CursorShape.PointingHandCursor)
        bd.setStyleSheet(
            "QPushButton { background: #5865F2; color: white;"
            " border: none; border-radius: 10px; font-weight: 700; }"
            " QPushButton:hover { background: #6a76ff; }")
        bd.clicked.connect(self._open_discord)
        v.addWidget(bd)
        bw = QPushButton("Enviar comprobante por WhatsApp")
        bw.setFixedHeight(42)
        bw.setCursor(Qt.CursorShape.PointingHandCursor)
        bw.setStyleSheet(
            "QPushButton { background: #2ea043; color: white;"
            " border: none; border-radius: 10px; font-weight: 700; }"
            " QPushButton:hover { background: #3fb950; }")
        bw.clicked.connect(self._open_whatsapp)
        v.addWidget(bw)
        bk = QPushButton("Ingresar clave de licencia")
        bk.setFixedHeight(42)
        bk.setCursor(Qt.CursorShape.PointingHandCursor)
        bk.setStyleSheet(
            "QPushButton { background: transparent; color: #7c5cff;"
            " border: 1px solid #7c5cff; border-radius: 10px;"
            " font-weight: 700; }"
            " QPushButton:hover { background: rgba(124,92,255,35); }")
        bk.clicked.connect(self._enter_key)
        v.addWidget(bk)
        self._hint = QLabel("")
        self._hint.setStyleSheet("color: #ef4444; font-size: 10.5px;")
        self._hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._hint.setWordWrap(True)
        v.addWidget(self._hint)
        st = QLabel("1) Escanea el QR con Yape  ·  2) Envia tu "
                    "comprobante por Discord  ·  3) Recibe tu clave al instante")
        st.setStyleSheet("color: #8b949e; font-size: 10px;")
        st.setAlignment(Qt.AlignmentFlag.AlignCenter)
        st.setWordWrap(True)
        v.addWidget(st)

        try:
            _pw = self.parent()
            if _pw is not None and hasattr(_pw, "_retranslate"):
                _pw._retranslate()
        except Exception:
            pass

        # _plans_i18n: traduce el dialogo en English al abrirse
        try:
            _lang = CURRENT_LANG
            print("[i18n] PlansDialog lang:", repr(_lang))
            if _lang == "English":
                from PySide6.QtWidgets import (QLabel as _QL2,
                                               QPushButton as _QB2)
                _txts = [_x.text() for _x in self.findChildren(_QL2)]
                print("[i18n] muestras:", _txts[:8])
                print("[i18n] clave en TR:",
                      "Hasta 5,000 caracteres por conversi\u00f3n" in TR_EN)
                _n = 0
                for _lb in self.findChildren(_QL2):
                    if _lb.text() in TR_EN:
                        _lb.setText(TR_EN[_lb.text()])
                        _n += 1
                for _b in self.findChildren(_QB2):
                    _tx = _b.text().strip()
                    if _tx in TR_EN:
                        _b.setText(TR_EN[_tx])
                        _n += 1
                print("[i18n] PlansDialog traducidos:", _n)
        except Exception:
            import traceback
            traceback.print_exc()

    def _load_qr(self):
        import sys
        base = Path(getattr(sys, "_MEIPASS",
                            Path(__file__).resolve().parents[1]))
        plan = getattr(self, "_plan", "").lower()
        dirs = [base / "assets" / "icons", base / "assets",
                Path("assets") / "icons", Path("assets")]
        cands = []
        for d in dirs:
            try:
                for f in d.iterdir():
                    low = f.name.lower()
                    if f.is_file() and low.endswith(
                            (".png", ".jpg", ".jpeg", ".webp")) and (
                            "qr" in low or "yape" in low):
                        cands.append(f)
            except Exception:
                pass

        def score(f):
            low = f.name.lower()
            if low.startswith("yape_qr_" + plan):
                return 0
            if low.startswith("yape_qr"):
                return 1
            if "yape" in low and "qr" in low:
                return 2
            return 3

        cands.sort(key=score)
        print("QR candidatos:", [c.name for c in cands])
        for fp in cands:
            px = QPixmap(str(fp)).scaled(
                170, 170, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            if not px.isNull():
                self._qr_label.setPixmap(px)
                self._qr_label.setAlignment(
                    Qt.AlignmentFlag.AlignCenter)
                return
        self._qr_wrap.setVisible(False)


    def _open_whatsapp(self):
        import urllib.parse
        plan = getattr(self, "_plan", "")
        msg = ("Hola WillpoVoice, acabo de pagar el plan " + plan +
               " con Yape. Adjunto mi comprobante.")
        url = ("https://wa.me/51923073560?text=" +
               urllib.parse.quote(msg))
        QDesktopServices.openUrl(QUrl(url))

    def _open_discord(self):
        if DISCORD_URL:
            QDesktopServices.openUrl(QUrl(DISCORD_URL))
        else:
            self._hint.setText(
                "Discord aun no configurado en esta version. "
                "Usa el boton Soporte de la ventana principal.")
    def _enter_key(self):
        try:
            # subir por la cadena de padres hasta MainWindow
            w = self.parent()
            while w is not None and not hasattr(w, "_open_license_dialog"):
                w = w.parent()
            plans = self.parent()
            self.accept()
            # cerrar el dialogo de planes para que se reabra fresco
            if plans is not None and plans is not w:
                try:
                    plans.accept()
                except Exception:
                    pass
            if w is not None:
                w._open_license_dialog()
        except Exception:
            pass



class _HexIcon(QWidget):
    def __init__(self, pix, color, size=52, parent=None):
        super().__init__(parent)
        self._pix = pix
        self._color = color
        self.setFixedSize(size, size)

    def paintEvent(self, ev):
        import math
        from PySide6.QtGui import QPolygonF, QPen
        from PySide6.QtCore import QPointF
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        s = self.width()
        c = s / 2
        r = s / 2 - 2
        pts = [QPointF(c + r * math.cos(math.radians(60 * k - 30)),
                       c + r * math.sin(math.radians(60 * k - 30)))
               for k in range(6)]
        fill = QColor(self._color)
        fill.setAlpha(38)
        p.setBrush(fill)
        p.setPen(QPen(QColor(self._color), 1.5))
        p.drawPolygon(QPolygonF(pts))
        p.setPen(Qt.PenStyle.NoPen)
        ip = self._pix
        p.drawPixmap(int(c - ip.width() / 2), int(c - ip.height() / 2), ip)
        p.end()


def _medal_pixmap(w=34, h=50):
    """Medalla colgante: cinta vertical con muesca V y circulo con diamante."""
    from PySide6.QtSvg import QSvgRenderer
    from PySide6.QtCore import QByteArray
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 72">'
           '<defs>'
           '<linearGradient id="rb" x1="0" y1="0" x2="0" y2="1">'
           '<stop offset="0" stop-color="#8b5cf6"/>'
           '<stop offset="1" stop-color="#6d28d9"/>'
           '</linearGradient>'
           '<linearGradient id="cg" x1="0" y1="0" x2="1" y2="1">'
           '<stop offset="0" stop-color="#a78bfa"/>'
           '<stop offset="1" stop-color="#7c3aed"/>'
           '</linearGradient>'
           '</defs>'
           '<path d="M14 0 h20 v60 l-10 -9 -10 9 z" fill="url(#rb)"/>'
           '<path d="M14 0 h20 v5 h-20 z" fill="#5b21b6" opacity="0.55"/>'
           '<circle cx="24" cy="24" r="15" fill="url(#cg)"/>'
           '<circle cx="24" cy="24" r="15" fill="none" '
           'stroke="#e9d5ff" stroke-width="2"/>'
           '<path d="M18 21 h12 l4 5 -10 11 -10 -11 z" fill="#ffffff"/>'
           '<path d="M18 21 l6 5 6 -5 M24 26 v11 M14 26 h20" '
           'stroke="#ddd6fe" stroke-width="1" fill="none" opacity="0.8"/>'
           '</svg>')
    r = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    pm = QPixmap(w, h)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    r.render(p)
    p.end()
    return pm


class PlansDialog(QDialog):
    _GIFT = ("M20 6h-2.18c.11-.31.18-.65.18-1a3 3 0 0 0-5.5-1.65l-.5.67-.5-.68"
             "A3 3 0 0 0 6 5c0 .35.07.69.18 1H4a2 2 0 0 0-2 2v11a2 2 0 0 0 2 2h16"
             "a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2zm-5-2a1 1 0 1 1 0 2 1 1 0 0 1 0-2zM9 4"
             "a1 1 0 1 1 0 2 1 1 0 0 1 0-2zm11 15H4v-2h16v2zm0-5H4V8h5.08L7 10.83"
             " 8.62 12 11 8.76l1-1.36 1 1.36L15.38 12 17 10.83 14.92 8H20v6z")
    _CART = ("M7 18c-1.1 0-1.99.9-1.99 2S5.9 22 7 22s2-.9 2-2-.9-2-2-2zM1 2v2h2l3.6 7.59"
             "-1.35 2.45c-.16.28-.25.61-.25.96 0 1.1.9 2 2 2h12v-2H7.42c-.14 0-.25-.11"
             "-.25-.25l.03-.12.9-1.63h7.45c.75 0 1.41-.41 1.75-1.03l3.58-6.49A1 1 0 0 0 "
             "20 4H5.21l-.94-2H1zm16 16c-1.1 0-1.99.9-1.99 2s.89 2 1.99 2 2-.9 2-2"
             "-.9-2-2-2z")
    _CAL = ("M19 4h-1V2h-2v2H8V2H6v2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 "
            "2-2V6a2 2 0 0 0-2-2zm0 16H5V10h14v10zM5 8V6h14v2H5z")
    _REFRESH = ("M17.65 6.35A7.95 7.95 0 0 0 12 4a8 8 0 1 0 7.73 10h-2.08A6 6 0 1 1 "
                "12 6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z")
    _GEM = ("M6 3h12l4 6-10 12L2 9l4-6zm2 2L5.5 8.5 12 17l6.5-8.5L16 5H8z")
    _CHECK = "M9 16.17 4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"
    _BOLT = "M7 2v11h3v9l7-12h-4l4-8z"
    _SHIELD = ("M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm-2 "
               "16l-4-4 1.41-1.41L10 14.17l6.59-6.59L18 9l-8 8z")

    def __init__(self, *a, **k):
        global _LIGHT_SUSPEND
        _LIGHT_SUSPEND = True
        try:
            self._plans_init_orig(*a, **k)
        finally:
            _LIGHT_SUSPEND = False

    def _plans_init_orig(self, parent):
        super().__init__(parent)
        self.setModal(True)
        self.setFixedWidth(540)
        try:
            from PySide6.QtGui import QGuiApplication
            _scr = QGuiApplication.primaryScreen()
            if _scr is not None:
                self.setMaximumHeight(
                    int(_scr.availableSize().height() * 0.92))
        except Exception:
            pass
        self.setWindowTitle("WillpoVoice Premium")
        self.setStyleSheet("PlansDialog { background: #0a0c14; }")
        self._bg = QLabel(self)
        self._bg.setStyleSheet("background: transparent;")
        self._bg.lower()

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }")
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        v = QVBoxLayout(content)
        v.setContentsMargins(22, 14, 22, 14)
        v.setSpacing(8)

        hd = QLabel()
        hd.setPixmap(make_icon("crown", "#f5b544", 32))
        hd.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(hd)
        t1 = QLabel('Elige tu <span style="color:#a78bfa;">plan</span>')
        t1.setStyleSheet(
            "color: #ffffff; font-size: 20px; font-weight: 800;")
        t1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(t1)
        t2 = QLabel('Voces <span style="color:#f472b6;">premium</span> reales, '
                    'sin l\u00edmites artificiales.')
        t2.setStyleSheet("color: #9aa4c0; font-size: 11px;")
        t2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(t2)
        v.addSpacing(4)

        self._card(v, "#00d0ff", "flask", None, "Estándar", "Incluido",
                   ["Hasta 5,000 caracteres por conversión", "Chat IA incluido",
                    "Hasta 5,000 caracteres por conversi\u00f3n",
                    "Todas las voces premium"],
                   btn_text="Incluido con tu compra",
                   btn_icon=self._GIFT, solid=False,
                   on_buy=self._start_trial)
        _GEM_PATH = "M6 3 L18 3 L22 9 L12 21 L2 9 Z M2 9 L22 9 M9 9 L12 21 M15 9 L12 21 M9 9 L11 3 M15 9 L13 3"
        self._card(v, "#a855f7", None, _GEM_PATH, "Platinum", "S/ 30",
                   ["Hasta 20,000 caracteres por conversión (≈22 min)", "Soporte prioritario por Discord",
                    "Todas las voces premium", "Actualizaciones incluidas"],
                   btn_text="Comprar", btn_icon=self._CART, solid=False,
                   on_buy=lambda: self._buy(
                       "Platinum", 30, YAPE_URL_MENSUAL))
        self._card(v, "#ffb020", "star", None, "Gold", "S/ 50",
                   ["Caracteres ILIMITADOS", "Sin límites artificiales",
                    "Voces nuevas para siempre",
                    "Soporte prioritario de por vida"],
                   btn_text="Comprar", btn_icon=None, solid=True,
                   badge="Recomendado", ribbon=True,
                   on_buy=lambda: self._buy(
                       "Gold", 50, YAPE_URL_LIFETIME))

        v.addSpacing(2)
        foot = QFrame()
        foot.setObjectName("plansFooter")
        foot.setStyleSheet(
            "#plansFooter { background: #10141f; border: 1px solid #1c2333;"
            " border-radius: 12px; }")
        fv = QHBoxLayout(foot)
        fv.setContentsMargins(14, 8, 14, 8)
        fv.setSpacing(10)
        for path, color, title, sub in [
            (self._SHIELD, "#4cc2ff", "Pago seguro",
             "Tus datos est\u00e1n protegidos"),
            (self._BOLT, "#bc8cff", "Acceso inmediato",
             "Disfruta al instante"),
            (self._REFRESH, "#4cc2ff", "Sin renovaciones",
             "Pago \u00fanico, para siempre"),
        ]:
            it = QHBoxLayout()
            it.setSpacing(10)
            ic = QLabel()
            ic.setPixmap(_chat_svg(path, color, 16))
            it.addWidget(ic)
            tx = QVBoxLayout()
            tx.setSpacing(2)
            a = QLabel(title)
            a.setStyleSheet(
                "color: #e6edf3; font-size: 10.5px; font-weight: 700;")
            tx.addWidget(a)
            b = QLabel(sub)
            b.setStyleSheet("color: #7d8590; font-size: 9px;")
            tx.addWidget(b)
            it.addLayout(tx)
            fv.addLayout(it)
            fv.addStretch(1)
        v.addWidget(foot)
        scroll.setWidget(content)
        outer.addWidget(scroll)
        content.adjustSize()
        try:
            from PySide6.QtGui import QGuiApplication
            _scr = QGuiApplication.primaryScreen()
            maxh = int(_scr.availableSize().height() * 0.92) if _scr else 900
        except Exception:
            maxh = 900
        want = content.sizeHint().height() + 46
        self.resize(540, min(want, maxh))
        scroll.setMinimumHeight(320)

        # _plans_i18n: traduce el selector de planes en English
        try:
            if CURRENT_LANG == "English":
                from PySide6.QtWidgets import (QLabel as _QL3,
                                               QPushButton as _QB3)
                for _lb in self.findChildren(_QL3):
                    if _lb.text() in TR_EN:
                        _lb.setText(TR_EN[_lb.text()])
                for _b in self.findChildren(_QB3):
                    _tx = _b.text().strip()
                    if _tx in TR_EN:
                        _b.setText(TR_EN[_tx])
        except Exception:
            pass

    def _card(self, v, color, icon_kind, icon_path, name, price, feats,
              btn_text=None, btn_icon=None, solid=False, badge=None,
              ribbon=False, on_buy=None):
        is_active = False
        try:
            det = license_manager.license_details()
            if det.get("state") == "licensed":
                tt = det.get("tier", "")
                act = ("Platinum" if tt == "Platinum"
                       else ("Gold" if tt == "Gold" else "Estándar"))
                is_active = (act == name)
        except Exception:
            is_active = False
        if is_active:
            btn_text = "Plan Activado Permanente"
        def _A(c, a):
            return "#" + a + c[1:]
        card = QFrame()
        card.setObjectName("plancard_" + name)
        bord = color if badge else _A(color, "99")
        bgs = {"#00d0ff": "0b1322", "#a855f7": "130e26",
               "#ffb020": "181007"}
        rgb = bgs.get(color, "10141f")
        card.setStyleSheet(
            "#plancard_" + name + " { background: qlineargradient("
            "x1:0,y1:0,x2:0,y2:1, stop:0 #33" + rgb + ", stop:1 #14"
            + rgb + "); border: 1.5px solid " + bord +
            "; border-radius: 16px; }")
        cv = QVBoxLayout(card)
        cv.setContentsMargins(14, 12, 14, 12)
        cv.setSpacing(6)
        top = QHBoxLayout()
        top.setSpacing(14)
        if icon_kind:
            pix = make_icon(icon_kind, color, 22)
        else:
            pix = _chat_svg(icon_path, color, 22)
        hexic = _HexIcon(pix, color, 44)
        top.addWidget(hexic)
        if name == "Gold":
            from PySide6.QtWidgets import QGraphicsOpacityEffect
            from PySide6.QtCore import QPropertyAnimation, QEasingCurve
            eff = QGraphicsOpacityEffect(hexic)
            hexic.setGraphicsEffect(eff)
            an = QPropertyAnimation(eff, b"opacity")
            an.setStartValue(0.55)
            an.setEndValue(1.0)
            an.setDuration(900)
            an.setLoopCount(-1)
            an.setEasingCurve(QEasingCurve(QEasingCurve.Type.InOutSine))
            an.start()
            self._gold_shine = an
        nrow = QHBoxLayout()
        nrow.setSpacing(10)
        nm = QLabel(name)
        nm.setStyleSheet(
            "color: #ffffff; font-size: 14px; font-weight: 800;")
        nrow.addWidget(nm)
        if badge:
            bd = QFrame()
            bd.setStyleSheet(
                "QFrame { background: rgba(245,181,68,26);"
                " border: 1px solid rgba(245,181,68,70);"
                " border-radius: 12px; }")
            bh = QHBoxLayout(bd)
            bh.setContentsMargins(10, 4, 10, 4)
            bh.setSpacing(6)
            bic = QLabel()
            bic.setPixmap(make_icon("star", "#f5b544", 11))
            bic.setStyleSheet("background: transparent; border: none;")
            bh.addWidget(bic)
            btx = QLabel(badge)
            btx.setStyleSheet(
                "color: #f5d98f; font-size: 10px; font-weight: 700;"
                " background: transparent; border: none;")
            bh.addWidget(btx)
            nrow.addWidget(bd)
        nrow.addStretch(1)
        pr = QLabel(price)
        pr.setStyleSheet(
            "color: " + color + "; border: 1px solid " + _A(color, "66") + ";"
            " border-radius: 12px; padding: 4px 12px;"
            " font-size: 12px; font-weight: 800;"
            " background: rgba(0,0,0,60);")
        nrow.addWidget(pr)
        top.addLayout(nrow)
        cv.addLayout(top)
        cv.addSpacing(2)
        for f in feats:
            fr = QHBoxLayout()
            fr.setSpacing(10)
            fr.setContentsMargins(6, 0, 0, 0)
            ck = QLabel()
            ck.setPixmap(_chat_svg(self._CHECK, color, 12))
            fr.addWidget(ck)
            fl = QLabel(f)
            fl.setStyleSheet("color: #c9d1d9; font-size: 10.5px;")
            fr.addWidget(fl)
            fr.addStretch(1)
            cv.addLayout(fr)
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(
            "border-top: 1px dashed " + _A(color, "44") + ";"
            " background: transparent;")
        cv.addWidget(sep)
        if btn_text:
            b = QPushButton(btn_text)
            b.setFixedHeight(36 if solid else 32)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            if solid:
                b.setStyleSheet(
                    "QPushButton { background: qlineargradient(x1:0,y1:0,"
                    "x2:1,y2:0, stop:0 #8d5cf0, stop:1 #6d2fd0);"
                    " color: white; border: none; border-radius: 12px;"
                    " font-weight: 800; font-size: 13px; }"
                    " QPushButton:hover { background: #9d70ff; }")
                b.setIcon(QIcon(make_icon("crown", "#fbbf24", 16)))
            else:
                b.setStyleSheet(
                    "QPushButton { background: transparent; color: "
                    + color + "; border: 1px solid " + _A(color, "88") + ";"
                    " border-radius: 10px; font-weight: 700;"
                    " font-size: 12px; }"
                    " QPushButton:hover { background: " + _A(color, "22") + "; }")
                if btn_icon:
                    b.setIcon(QIcon(_chat_svg(btn_icon, color, 15)))
            if on_buy:
                b.clicked.connect(on_buy)
            cv.addWidget(b)
        if is_active:
            try:
                b.setEnabled(False)
                b.setStyleSheet(
                    "QPushButton { background: rgba(46,160,67,28);"
                    " color: #3fb950; border: 1px solid #2ea043;"
                    " border-radius: 10px; font-weight: 700; }")
            except Exception:
                pass
        v.addWidget(card)
        if ribbon:
            gem = QLabel(card)
            gem.setFixedSize(34, 50)
            gem.setPixmap(_medal_pixmap(34, 50))
            gem.setStyleSheet("background: transparent;")
            host = v.parent()
            if host is not None:
                gem.setParent(host)

            def _place(g=gem, c=card, h=host):
                try:
                    from PySide6.QtCore import QPoint
                    if h is not None:
                        g.move(c.mapTo(h, QPoint(c.width() - 30, 0)))
                    else:
                        g.move(c.width() - 30, 0)
                    g.raise_()
                    g.show()
                except Exception:
                    pass
            QTimer.singleShot(0, _place)

    def _build_bg(self):
        import sys
        base = Path(getattr(sys, "_MEIPASS",
                            Path(__file__).resolve().parents[1]))
        src = base / "assets" / "icons" / "licencia_left.png"
        if not src.exists():
            return
        w = self.width()
        h = self.height()
        if w <= 0 or h <= 0:
            return
        out = QPixmap(w, h)
        out.fill(QColor("#0a0c14"))
        p = QPainter(out)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setOpacity(0.30)
        scaled = QPixmap(str(src)).scaled(
            w, h, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation)
        p.drawPixmap((w - scaled.width()) // 2,
                     (h - scaled.height()) // 2, scaled)
        p.end()
        self._bg.setPixmap(out)
        self._bg.setGeometry(0, 0, w, h)
        self._bg.lower()

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        self._build_bg()

    def _start_trial(self):
        try:
            state, days = license_manager.check_status()
        except Exception:
            state, days = "trial", 7
        d = TrialActivatedDialog(
            self, max(0, days if state == "trial" else 7))
        d.exec()

    def _buy(self, plan, price, yape_url):
        d = PaymentDialog(self, plan, price, yape_url)
        d.exec()


def _open_plans(self):
    d = PlansDialog(self)
    d.exec()
    try:
        st, _d = license_manager.check_status()
        self._refresh_token_chip(st)
    except Exception:
        pass


MainWindow._open_plans = _open_plans


class _Bubble(QWidget):
    def __init__(self, text, is_user, ts, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        v = QVBoxLayout(self)
        v.setContentsMargins(16, 12, 16, 8)
        v.setSpacing(6)
        lbl = QLabel(text)
        lbl.setWordWrap(True)
        lbl.setStyleSheet(
            "color: #ffffff; font-size: 12.5px; background: transparent;")
        v.addWidget(lbl)
        trow = QHBoxLayout()
        trow.setSpacing(4)
        trow.addStretch(1)
        tlabel = QLabel(ts + ("  \u2713\u2713" if is_user else ""))
        tlabel.setStyleSheet(
            "color: " + ("rgba(255,255,255,0.75)" if is_user else "#8b949e") +
            "; font-size: 9.5px; background: transparent;")
        trow.addWidget(tlabel)
        v.addLayout(trow)

    def paintEvent(self, ev):
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
            if LIGHT_MODE:
                g.setColorAt(0, QColor("#ffffff"))
                g.setColorAt(1, QColor("#eef1f8"))
            else:
                g.setColorAt(0, QColor("#141b32"))
                g.setColorAt(1, QColor("#0e1526"))
            p.fillPath(path, g)
            p.setPen(QPen(QColor("#d5dcea" if LIGHT_MODE else "#2a3552"), 1))
            p.drawPath(path)
        p.end()


def _add_chat_bubble(self, text, is_user, temp=False):
    from PySide6.QtCore import QTime
    ts = QTime.currentTime().toString("h:mm AP")
    row = QHBoxLayout()
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(10)
    if not is_user:
        av = QLabel()
        av.setFixedSize(40, 40)
        av.setPixmap(self.windowIcon().pixmap(24, 24))
        av.setAlignment(Qt.AlignmentFlag.AlignCenter)
        av.setStyleSheet(
            "background: #0d1220; border: 2px solid #7c5cff;"
            " border-radius: 20px;")
        row.addWidget(av, 0, Qt.AlignmentFlag.AlignTop)
    bub = _Bubble(text, is_user, ts)
    bub.setMaximumWidth(560)
    if is_user:
        row.addStretch(1)
        row.addWidget(bub)
    else:
        col = QVBoxLayout()
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(4)
        col.addWidget(bub)
        if not temp:
            acts = QHBoxLayout()
            acts.setSpacing(8)
            acts.setContentsMargins(6, 0, 0, 0)
            ghost = ("QPushButton { background: transparent;"
                     " color: #8b949e; border: none; font-size: 10px;"
                     " font-weight: 600; padding: 2px 6px;"
                     " border-radius: 6px; }"
                     " QPushButton:hover { color: #e6edf3;"
                     " background: rgba(139,148,158,30); }")
            b_copy = QPushButton(_tr("Copiar"))
            b_copy.setIcon(QIcon(make_icon("copy", "#8b949e", 12)))
            b_copy.setStyleSheet(ghost)
            b_copy.setCursor(Qt.CursorShape.PointingHandCursor)
            b_copy.clicked.connect(
                lambda _=False, txt=text: self._copy_chat_text(txt))
            acts.addWidget(b_copy)
            b_add = QPushButton(_tr("Agregar a conversi\u00f3n"))
            b_add.setIcon(QIcon(make_icon("paste", "#8b949e", 12)))
            b_add.setStyleSheet(ghost)
            b_add.setCursor(Qt.CursorShape.PointingHandCursor)
            b_add.clicked.connect(
                lambda _=False, txt=text: self._add_to_conversion(txt))
            acts.addWidget(b_add)
            b_speak = QPushButton(_tr("Escuchar"))
            b_speak.setIcon(QIcon(_speak_head_icon(13)))
            b_speak.setStyleSheet(ghost)
            b_speak.setCursor(Qt.CursorShape.PointingHandCursor)
            b_speak.clicked.connect(
                lambda _=False, btn=b_speak, txt=text: self._toggle_speak_btn(btn, txt))
            acts.addWidget(b_speak)
            acts.addStretch(1)
            col.addLayout(acts)
        row.addLayout(col)
        row.addStretch(1)
    wrap = QWidget()
    wrap.setLayout(row)
    wrap.setProperty("temp", temp)
    self._chat_layout.insertWidget(self._chat_layout.count() - 1, wrap)
    self._chat_scroll.verticalScrollBar().setValue(
        self._chat_scroll.verticalScrollBar().maximum())
    return wrap


def _on_chat_response(self, response, temp_bubble):
    if temp_bubble is not None:
        try:
            temp_bubble.setParent(None)
            temp_bubble.deleteLater()
        except Exception:
            pass
    self._add_chat_bubble(response, is_user=False)
    if hasattr(self, "_chat_history"):
        self._chat_history.append(
            {"role": "assistant", "content": response})
    self._show_chat_chips()


def _layout_chat_bg(self):
    try:
        import sys as _sys
        from PySide6.QtSvg import QSvgRenderer
        base = Path(getattr(_sys, "_MEIPASS",
                            Path(__file__).resolve().parents[1]))
        if not getattr(self, "_chat_bg_pix", None):
            pm = QPixmap(1400, 900)
            pm.fill(Qt.GlobalColor.transparent)
            pr = QPainter(pm)
            pr.setOpacity(0.30)
            sp_png = base / "assets" / "icons" / ("chat_bg_ligth.png" if LIGHT_MODE else "chat_bg.png")
            sp_svg = base / "assets" / "banner.svg"
            if sp_png.exists():
                src = QPixmap(str(sp_png))
                scaled = src.scaled(
                    1400, 900,
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation)
                pr.drawPixmap((1400 - scaled.width()) // 2,
                              (900 - scaled.height()) // 2, scaled)
            elif sp_svg.exists():
                QSvgRenderer(str(sp_svg)).render(pr)
            pr.end()
            self._chat_bg_pix = pm
        w = self.pages.width() or 1200
        h = self.pages.height() or 800
        self._chat_bg.setGeometry(0, 0, w, h)
        self._chat_bg.setPixmap(self._chat_bg_pix)
        self._chat_bg.setScaledContents(True)
    except Exception:
        pass


MainWindow._layout_chat_bg = _layout_chat_bg
def _save_groq_key(self):
    from PySide6.QtCore import QSettings
    key = self._groq_key_input.text().strip()
    if not key:
        return
    s = QSettings("WillpoVoice", "WillpoVoice")
    s.setValue("groq_api_key", key)
    self._chat_banner.setVisible(False)
    self._set_chat_locked(False)
    self._add_chat_bubble(
        "API Key conectada. ¡Listo para chatear!", is_user=False)


def _toggle_key_vis(self):
    le = self._groq_key_input
    if le.echoMode() == QLineEdit.EchoMode.Password:
        le.setEchoMode(QLineEdit.EchoMode.Normal)
        self._key_eye.setIcon(QIcon(_chat_svg(_EYE_ON, "#8b949e", 16)))
    else:
        le.setEchoMode(QLineEdit.EchoMode.Password)
        self._key_eye.setIcon(QIcon(_chat_svg(_EYE_OFF, "#8b949e", 16)))


def _set_chat_locked(self, locked):
    try:
        self._chat_input.setEnabled(not locked)
        self._chat_send_btn.setEnabled(not locked)
        self._chat_input.setPlaceholderText(
            "Configura tu API Key para empezar..." if locked
            else "Escribe tu pregunta...")
        self._chat_send_btn.setStyleSheet(
            "QPushButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            " stop:0 #8d75ff, stop:1 #6d5df0); border: none;"
            " border-radius: 12px; }"
            " QPushButton:hover { background: #9d87ff; }"
            " QPushButton:disabled { background: #232c47; }")
        self._chat_input.setStyleSheet(
            "QLineEdit { background: transparent; border: none;"
            " color: #e6edf3; font-size: 13px; padding: 0 6px; }"
            " QLineEdit:disabled { color: #55618a; }")
    except Exception:
        pass


def _copy_chat_text(self, txt):
    try:
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(txt)
        self.statusBar().showMessage(
            "Respuesta copiada al portapapeles", 3000)
    except Exception:
        pass


def _add_to_conversion(self, txt):
    target = None
    for name in ("text_edit", "text_input", "input_text",
                 "text_area", "editor", "txt_input"):
        w = getattr(self, name, None)
        if w is not None and (hasattr(w, "setPlainText")
                              or hasattr(w, "setText")):
            target = w
            break
    if target is None:
        from PySide6.QtWidgets import QTextEdit, QPlainTextEdit
        for w in self.findChildren((QTextEdit, QPlainTextEdit)):
            if w is not getattr(self, "_chat_input", None):
                target = w
                break
    if target is not None:
        try:
            if hasattr(target, "setPlainText"):
                target.setPlainText(txt)
            else:
                target.setText(txt)
            self._switch_page(0)
            self.statusBar().showMessage(
                "Texto agregado a la conversi\u00f3n", 3000)
        except Exception:
            pass


def _on_chat_chip(self, label):
    respuestas = {
        "Crear un guion / historia":
            "\u00a1Perfecto! \u00bfDe qu\u00e9 tratar\u00e1 tu historia o guion? "
            "Dame los detalles exactos y lo crear\u00e9 \u2728",
        "Analizar guion y mejorar":
            "\u00a1Perfecto! Comp\u00e1rteme tu guion para mejorarlo.",
        "Crear anuncios publicitarios":
            "\u00a1Perfecto! Vamos a crear tu anuncio publicitario. "
            "Necesitar\u00e9 lo siguiente:\n"
            "- Nombre de tu negocio:\n"
            "- De qu\u00e9 trata tu negocio:\n"
            "- Qu\u00e9 producto vas a ofrecer:\n"
            "- Precio",
    }
    self._add_chat_bubble(label, is_user=True)
    self._chat_mode = label
    try:
        self._chat_chips_wrap.setParent(None)
        self._chat_chips_wrap.deleteLater()
    except Exception:
        pass
    resp = respuestas.get(label, "")
    if not hasattr(self, "_chat_history"):
        self._chat_history = []
    self._chat_history.append({"role": "user", "content": label})
    self._chat_history.append({"role": "assistant", "content": resp})
    self._add_chat_bubble(resp, is_user=False)


def _show_chat_chips(self):
    if not self.settings.get("suggestions", True):
        return
    try:
        old = getattr(self, "_chat_chips_wrap", None)
        if old is not None:
            old.setParent(None)
            old.deleteLater()
    except Exception:
        pass
    chips = QHBoxLayout()
    chips.setSpacing(10)
    chips.setContentsMargins(52, 4, 8, 0)
    chip_style = (
        "QPushButton { background: transparent; color: #cfe3ff;"
        " border: 1px solid #2f4c79; border-radius: 16px;"
        " padding: 8px 14px; font-size: 11px; font-weight: 600; }"
        " QPushButton:hover { background: rgba(88,166,255,25); }")
    for glyph, label in [("doc", "Crear un guion / historia"),
                         ("search", "Analizar guion y mejorar"),
                         ("bolt", "Crear anuncios publicitarios")]:
        ch = QPushButton("  " + label)
        ch.setIcon(QIcon(make_icon(glyph, "#7cb7ff", 13)))
        ch.setCursor(Qt.CursorShape.PointingHandCursor)
        ch.setStyleSheet(chip_style)
        ch.clicked.connect(
            lambda _=False, lb=label: self._on_chat_chip(lb))
        chips.addWidget(ch)
    chips.addStretch(1)
    x = QPushButton()
    x.setFixedSize(26, 26)
    x.setIcon(QIcon(make_icon("x", "#8b949e", 12)))
    x.setCursor(Qt.CursorShape.PointingHandCursor)
    x.setToolTip("Cerrar sugerencias")
    x.setStyleSheet(
        "QPushButton { background: transparent; border: none;"
        " border-radius: 13px; }"
        " QPushButton:hover { background: rgba(139,148,158,40); }")
    x.clicked.connect(self._hide_chat_chips)
    chips.addWidget(x)
    wrap = QWidget()
    wrap.setLayout(chips)
    self._chat_chips_wrap = wrap
    self._chat_layout.insertWidget(
        self._chat_layout.count() - 1, wrap)
    self._chat_scroll.verticalScrollBar().setValue(
        self._chat_scroll.verticalScrollBar().maximum())


def _hide_chat_chips(self):
    try:
        w = getattr(self, "_chat_chips_wrap", None)
        if w is not None:
            w.setParent(None)
            w.deleteLater()
        self._chat_chips_wrap = None
    except Exception:
        pass


MainWindow._show_chat_chips = _show_chat_chips
MainWindow._hide_chat_chips = _hide_chat_chips
MainWindow._on_chat_chip = _on_chat_chip
MainWindow._copy_chat_text = _copy_chat_text
def _speak_head_svg(size=14):
    """Cabeza parlante (Escuchar)."""
    from PySide6.QtSvg import QSvgRenderer
    from PySide6.QtCore import QByteArray
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
        'fill="none" stroke="#ffffff" stroke-width="1.7" '
        'stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M12 2a7 7 0 0 0-7 7v2c0 1.5-.6 2.5-1 3v2a1 1 0 0 0 1 1h2v4a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2v-4h2a1 1 0 0 0 1-1v-2c-.4-.5-1-1.5-1-3V9a7 7 0 0 0-7-7z"/>'
        '<path d="M18 10a2 2 0 1 1 4 0"/>'
        '<path d="M19 7a5 5 0 0 1 0 6"/>'
        '</svg>')
    r = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    pm = QPixmap(size, size); pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm); r.render(p); p.end()
    return pm


def _pause_svg(size=14):
    from PySide6.QtSvg import QSvgRenderer
    from PySide6.QtCore import QByteArray
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
           'fill="#ffffff">'
           '<rect x="6" y="5" width="4" height="14" rx="1"/>'
           '<rect x="14" y="5" width="4" height="14" rx="1"/></svg>')
    r = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    pm = QPixmap(size, size); pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm); r.render(p); p.end()
    return pm


def _play_svg(size=14):
    from PySide6.QtSvg import QSvgRenderer
    from PySide6.QtCore import QByteArray
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
           'fill="#ffffff"><path d="M7 4l12 8-12 8z"/></svg>')
    r = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    pm = QPixmap(size, size); pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm); r.render(p); p.end()
    return pm


def _spinner_pixmap(size=14, angle=0):
    """Arco que rota (spinner de carga)."""
    from PySide6.QtCore import QRectF
    from PySide6.QtGui import QPen
    pm = QPixmap(size, size); pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.translate(size / 2, size / 2)
    p.rotate(angle)
    pen = QPen(QColor("#cfe3ff"))
    pen.setWidthF(max(1.2, size / 11))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    p.setPen(pen)
    margin = max(1.5, size / 10)
    r = QRectF(-size / 2 + margin, -size / 2 + margin,
               size - 2 * margin, size - 2 * margin)
    p.drawArc(r, 90 * 16, 270 * 16)
    p.end()
    return pm


class _SpinnerWidget(QLabel):
    def __init__(self, size=13, parent=None):
        super().__init__(parent)
        self._size = size
        self._angle = 0
        self.setFixedSize(size + 6, size + 6)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(35)
        self._tick()

    def _tick(self):
        self._angle = (self._angle + 18) % 360
        self.setPixmap(_spinner_pixmap(self._size, self._angle))

    def stop(self):
        try:
            self._timer.stop()
        except Exception:
            pass


def _toggle_speak_btn(self, btn, text):
    """Maquina de estados: ESCUCHAR -> SPINNER -> PAUSA <-> PLAY -> ESCUCHAR."""
    # Inicializar registro si no existe
    if not hasattr(self, "_chat_speakers"):
        self._chat_speakers = {}
    state = self._chat_speakers.get(id(btn), {}).get("state", "idle")

    # ===== IDLE: iniciar narracion =====
    if state == "idle":
        self._chat_speakers[id(btn)] = {
            "state": "loading", "text": text,
            "spinner": None, "poll": None, "was_paused": False,
        }
        btn.setIcon(QIcon())
        sp = _SpinnerWidget(13, btn)
        btn.layout() if btn.layout() else None
        btn.setText("")
        self._chat_speakers[id(btn)]["spinner"] = sp
        # Centrar spinner en el boton
        g = btn.geometry()
        sp.setParent(btn)
        sp.move((btn.width() - sp.width()) // 2,
                (btn.height() - sp.height()) // 2)
        sp.raise_()
        sp.show()

        eng = getattr(self, "engine", None)
        if eng is None:
            self._chat_reset_btn(btn); return
        try:
            try:
                eng.select_voice("Seraphina")
            except Exception:
                pass
            eng.speak_async(text)
        except Exception as exc:
            print(f"TTS fallo: {exc}")
            self._chat_reset_btn(btn); return

        # Quitar spinner y pasar a PAUSA tras ~400ms (arranca el audio)
        def _to_pausing():
            entry = self._chat_speakers.get(id(btn))
            if not entry: return
            sp = entry.get("spinner")
            if sp is not None:
                sp.stop(); sp.setParent(None); sp.deleteLater()
            entry["spinner"] = None
            entry["state"] = "speaking"
            btn.setIcon(QIcon(_pause_svg(13)))
            btn.setText("Pausa")
            # Poller: detecta fin del audio via SAPI Status
            poll = QTimer(btn)
            poll.timeout.connect(lambda: self._chat_poll_sapi(btn))
            poll.start(250)
            entry["poll"] = poll
        QTimer.singleShot(450, _to_pausing)
        self.statusBar().showMessage("Hablando con Seraphina", 2500)
        return

    # ===== SPEAKING (PAUSA visible): pausar =====
    if state == "speaking":
        eng = getattr(self, "engine", None)
        try:
            if eng and eng.adapter and eng.adapter.sapi is not None:
                eng.adapter.sapi.Pause()
        except Exception:
            pass
        self._chat_speakers[id(btn)]["state"] = "paused"
        self._chat_speakers[id(btn)]["was_paused"] = True
        btn.setIcon(QIcon(_play_svg(13)))
        btn.setText("Reanudar")
        return

    # ===== PAUSED (PLAY visible): reanudar =====
    if state == "paused":
        eng = getattr(self, "engine", None)
        try:
            if eng and eng.adapter and eng.adapter.sapi is not None:
                eng.adapter.sapi.Resume()
        except Exception:
            pass
        self._chat_speakers[id(btn)]["state"] = "speaking"
        btn.setIcon(QIcon(_pause_svg(13)))
        btn.setText("Pausa")
        return


def _chat_poll_sapi(self, btn):
    """Revisa si el audio termino para volver a IDLE."""
    entry = self._chat_speakers.get(id(btn))
    if not entry:
        return
    eng = getattr(self, "engine", None)
    if eng is None:
        self._chat_reset_btn(btn); return
    try:
        sapi = eng.adapter.sapi
        rs = sapi.Status.RunningState  # 0=done 1=waiting 2=speaking
    except Exception:
        rs = 0
    if rs == 0:  # termino
        self._chat_reset_btn(btn)


def _chat_reset_btn(self, btn):
    """Vuelve el boton a estado ESCUCHAR (idle) y limpia recursos."""
    entry = self._chat_speakers.get(id(btn))
    if not entry: return
    sp = entry.get("spinner")
    if sp is not None:
        try:
            sp.stop(); sp.setParent(None); sp.deleteLater()
        except Exception:
            pass
    poll = entry.get("poll")
    if poll is not None:
        try:
            poll.stop()
        except Exception:
            pass
    self._chat_speakers[id(btn)] = {"state": "idle"}
    btn.setIcon(QIcon(_speak_head_svg(13)))
    btn.setText("Escuchar")


MainWindow._toggle_speak_btn = _toggle_speak_btn
MainWindow._chat_poll_sapi = _chat_poll_sapi
MainWindow._chat_reset_btn = _chat_reset_btn
MainWindow._speak_chat_text = _toggle_speak_btn
MainWindow._add_to_conversion = _add_to_conversion
MainWindow._set_chat_locked = _set_chat_locked
def _delete_groq_key(self):
    from PySide6.QtCore import QSettings
    s = QSettings("WillpoVoice", "WillpoVoice")
    s.remove("groq_api_key")
    try:
        self._groq_key_input.clear()
    except Exception:
        pass
    self._set_chat_locked(True)
    self._chat_banner.setVisible(True)
    self._add_chat_bubble(
        "API Key eliminada. Configura una nueva cuando quieras.",
        is_user=False)


MainWindow._delete_groq_key = _delete_groq_key
MainWindow._save_groq_key = _save_groq_key
MainWindow._toggle_key_vis = _toggle_key_vis
def _configure_groq_key(self):
    self._switch_page(5)
    vis = self._chat_banner.isVisible()
    self._chat_banner.setVisible(not vis)
    if not vis:
        try:
            self._groq_key_input.setFocus()
        except Exception:
            pass


# TODO: def _send_chat_message faltante\nMainWindow._configure_groq_key = _configure_groq_key
def _show_chat_tutorial(self):
    """Mini tutorial en GIF, ventana compacta con piel de la app."""
    import sys
    from PySide6.QtGui import QMovie, QImageReader
    from PySide6.QtCore import QSize
    base = Path(getattr(sys, "_MEIPASS",
                        Path(__file__).resolve().parents[1]))
    gif = base / "assets" / "tutorial.gif"
    if not gif.exists():
        self.statusBar().showMessage(
            "Tutorial no disponible (assets/tutorial.gif)", 3000)
        return
    d = QDialog(self)
    d.setWindowTitle("WillpoVoice - Mini tutorial")
    d.setWindowIcon(self.windowIcon())
    d.setStyleSheet("QDialog { background: #0a0c14; }")
    d.setFixedWidth(520)
    v = QVBoxLayout(d)
    v.setContentsMargins(20, 16, 20, 16)
    v.setSpacing(10)

    tt = QLabel("Mini tutorial")
    tt.setStyleSheet(
        "color: #ffffff; font-size: 16px; font-weight: 800;")
    tt.setAlignment(Qt.AlignmentFlag.AlignCenter)
    v.addWidget(tt)
    st = QLabel("Aprende el Chat IA en segundos")
    st.setStyleSheet("color: #8b949e; font-size: 10.5px;")
    st.setAlignment(Qt.AlignmentFlag.AlignCenter)
    v.addWidget(st)

    lbl = QLabel()
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setStyleSheet(
        "background: rgba(12,16,28,120);"
        " border: 1.5px solid rgba(139,117,255,80);"
        " border-radius: 16px;")
    fs = QImageReader(str(gif)).size()
    tw, th = 460, 300
    if fs.width() > 0 and fs.height() > 0:
        th = int(fs.height() * tw / fs.width())
        if th > 420:
            th = 420
            tw = int(fs.width() * th / fs.height())
    movie = QMovie(str(gif))
    movie.setScaledSize(QSize(tw, th))
    movie.start()
    lbl.setMovie(movie)
    lbl.setFixedSize(tw + 24, th + 24)
    v.addWidget(lbl, 0, Qt.AlignmentFlag.AlignHCenter)

    b = QPushButton("Entendido")
    b.setFixedHeight(36)
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    b.setStyleSheet(
        "QPushButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
        " stop:0 #8d5cf0, stop:1 #6d2fd0); color: white; border: none;"
        " border-radius: 12px; font-weight: 800; font-size: 12px; }"
        " QPushButton:hover { background: #9d70ff; }")
    b.clicked.connect(d.accept)
    v.addWidget(b)

    d.adjustSize()
    self._center_on_screen(d)
    d.exec()


MainWindow._show_chat_tutorial = _show_chat_tutorial

def _send_chat_message(self):
    text = self._chat_input.text().strip()
    if not text:
        return
    self._add_chat_bubble(text, is_user=True)
    self._chat_input.clear()
    if not hasattr(self, "_chat_history"):
        self._chat_history = []
    hist = list(self._chat_history)
    self._chat_history.append({"role": "user", "content": text})
    try:
        thinking = self._add_chat_bubble(
            "Pensando...", is_user=False, temp=True)
        worker = _ChatWorker(text, hist, getattr(self, "_chat_mode", None))
        worker.resultado.connect(
            lambda r, tb=thinking: self._on_chat_response(r, tb))
        if not hasattr(self, "_chat_workers"):
            self._chat_workers = []
        self._chat_workers.append(worker)
        worker.finished.connect(
            lambda w=worker: self._chat_workers.remove(w)
            if w in self._chat_workers else None)
        worker.start()
    except Exception as exc:
        self._add_chat_bubble(f"Error al enviar: {exc}", is_user=False)


MainWindow._send_chat_message = _send_chat_message
MainWindow._add_chat_bubble = _add_chat_bubble
MainWindow._on_chat_response = _on_chat_response

MainWindow._open_plans = _open_plans


def _clean_voice_name(name):
    n = (name or "").strip()
    if n.lower().startswith("microsoft "):
        n = n[10:]
    low = n.lower()
    if "multilingual" in low:
        base = low.split("multilingual")[0].strip()
        if base:
            base = base[0].upper() + base[1:]
        return f"{base} Multilingüe" if base else "Multilingüe"
    n = (n.replace("Online (Natural)", " ").replace("(Natural)", " ")
           .replace("Online", " "))
    return " ".join(n.split())




def _es_spanish(text):
    import re as _re
    low = (text or "").lower()
    if _re.search(r"[\u00bf\u00a1\u00f1\u00e1\u00e9\u00ed\u00f3\u00fa\u00fc]", low):
        return True
    common = (" el ", " la ", " los ", " las ", " de ", " que ", " y ",
              " en ", " por ", " para ", " con ", " una ", " un ", " es ", " son ")
    return sum(1 for w in common if w in low) >= 2


def _tts_text(self, text):
    if getattr(self, "_selected_cloned", ""):
        self._tts_cloned(self._selected_cloned, text)
        return text  # Devolver texto para no romper el flujo SAPI
    voz = ""
    try:
        voz = self.voice_combo.currentText()
    except Exception:
        pass
    import re as _re
    text = (text or "").replace("*", "").replace("#", "")
    text = _re.sub(r"\b[Ee]lige\b", "elije", text)
    text = _re.sub(r"([.!?])\s+elije\b", ", elije", text)
    if "multilingual" not in voz.lower():
        return text
    repl = {
        "\u00f1a": "nia", "\u00f1e": "nie", "\u00f1i": "niie", "\u00f1o": "nio", "\u00f1u": "niu",
        "\u00d1a": "Nia", "\u00d1e": "Nie", "\u00d1i": "Niie", "\u00d1o": "Nio", "\u00d1u": "Niu",
        "\u00d1A": "NIA", "\u00d1E": "NIE", "\u00d1I": "NIIE", "\u00d1O": "NIO", "\u00d1U": "NIU",
    }
    out = text
    for k, v in repl.items():
        out = out.replace(k, v)
    out = _re.sub(r"!+", "!!", out)
    out = _re.sub(r"\?+", "??", out)
    return out

MainWindow._tts_text = _tts_text


def _express_segments(self, text):
    # Desactivar modo expresivo para voces clonadas (solo SAPI)
    if getattr(self, "_selected_cloned", ""):
        return [(0, len(text or ""), 0)]
    import re as _re
    parts = []
    last = 0
    for m in _re.finditer(r"(?<=[.!?…])\s+", text):
        parts.append((last, m.start()))
        last = m.end()
    if last < len(text):
        parts.append((last, len(text)))
    segs = []
    for a, b in parts:
        s = text[a:b]
        if not s.strip():
            continue
        lead = len(s) - len(s.lstrip())
        m = _re.search(r"[¡¿]", s)
        if m and m.start() > lead:
            # prefijo descriptivo neutro + tramo expresivo que inicia con ¡/¿
            segs.append((a, a + m.start(), 0))
            boost = 2 if s[m.start()] == "¡" else 1
            segs.append((a + m.start(), b, boost))
        else:
            st = s.strip()
            if st.startswith(("¡", "!")):
                segs.append((a, b, 2))
            elif st.startswith(("¿", "?")):
                segs.append((a, b, 1))
            else:
                segs.append((a, b, 0))
    merged = []
    for a, b, boost in segs:
        if merged and merged[-1][2] == boost:
            merged[-1] = (merged[-1][0], b, boost)
        else:
            merged.append((a, b, boost))
    return merged


MainWindow._express_segments = _express_segments


def _show_express_hint(self):
    # No mostrar hint de modo expresivo para voces clonadas
    if getattr(self, "_selected_cloned", ""):
        return
    from PySide6.QtCore import QTimer, QPropertyAnimation
    from PySide6.QtWidgets import QGraphicsOpacityEffect
    hint = getattr(self, "_express_hint", None)
    if hint is None:
        hint = QFrame(self)
        hint.setObjectName("expresshint")
        hint.setStyleSheet(
            "#expresshint { background: rgba(22,27,34,235);"
            " border: 1px solid #30363d; border-radius: 10px; }")
        hb = QHBoxLayout(hint)
        hb.setContentsMargins(12, 8, 12, 8)
        hb.setSpacing(8)
        ic = QLabel()
        ic.setPixmap(make_icon("sparkles", "#f5b544", 14))
        hb.addWidget(ic)
        tx = QLabel(
            "Modo expresivo activo: la vista previa en vivo puede "
            "incluir micro-pausas entre frases. "
            "Al exportar, tu audio quedara fluido y sin cortes.")
        tx.setStyleSheet("color: #c9d1d9; font-size: 10.5px;")
        tx.setWordWrap(True)
        tx.setMaximumWidth(560)
        hb.addWidget(tx)
        self._express_hint = hint
        self._express_hint_timer = QTimer(self)
        self._express_hint_timer.setSingleShot(True)
        self._express_hint_timer.timeout.connect(
            self._fade_express_hint)
    hint.adjustSize()
    from PySide6.QtCore import QPoint
    cw = self.centralWidget()
    ref = getattr(self, "text_edit", None) or cw
    if ref is not None:
        bx = ref.mapTo(self, QPoint(0, 0)).x()
        x = bx + (ref.width() - hint.width()) // 2
    else:
        x = (self.width() - hint.width()) // 2
    y = (cw.mapTo(self, QPoint(0, 0)).y() + 70) if cw is not None else 70
    hint.move(x, y)
    eff = QGraphicsOpacityEffect(hint)
    eff.setOpacity(0.0)
    hint.setGraphicsEffect(eff)
    hint.show()
    hint.raise_()
    anim = QPropertyAnimation(eff, b"opacity")
    anim.setDuration(250)
    anim.setStartValue(0.0)
    anim.setEndValue(1.0)
    self._express_hint_anim = anim
    anim.start()
    self._express_hint_timer.start(4200)


def _fade_express_hint(self):
    from PySide6.QtCore import QPropertyAnimation
    from PySide6.QtWidgets import QGraphicsOpacityEffect
    hint = getattr(self, "_express_hint", None)
    if hint is None:
        return
    eff = hint.graphicsEffect()
    if not isinstance(eff, QGraphicsOpacityEffect):
        eff = QGraphicsOpacityEffect(hint)
        hint.setGraphicsEffect(eff)
    anim = QPropertyAnimation(eff, b"opacity")
    anim.setDuration(400)
    anim.setStartValue(1.0)
    anim.setEndValue(0.0)
    anim.finished.connect(lambda: hint.hide())
    self._express_hint_anim = anim
    anim.start()


MainWindow._show_express_hint = _show_express_hint
MainWindow._fade_express_hint = _fade_express_hint


LANG_TABLE = [
    ("es", "Español", "es", ["spanish", "espa", "(es)", "es-"]),
    ("en", "Inglés", "us", ["english", "ingl", "(en)", "en-"]),
    ("de", "Alemán", "de", ["german", "alem", "(de)", "de-"]),
    ("fr", "Francés", "fr", ["french", "franc", "(fr)", "fr-"]),
    ("it", "Italiano", "it", ["italian", "ital", "(it)", "it-"]),
    ("pt", "Portugués", "br", ["portug", "(pt)", "pt-"]),
    ("zh", "Chino", "cn", ["chinese", "chino", "(zh)", "zh-"]),
    ("ja", "Japonés", "jp", ["japanese", "japon", "(ja)", "ja-"]),
    ("ko", "Coreano", "kr", ["korean", "core", "(ko)", "ko-"]),
    ("ru", "Ruso", "ru", ["russian", "ruso", "(ru)", "ru-"]),
    ("ar", "Árabe", "sa", ["arabic", "arab", "(ar)", "ar-"]),
    ("hi", "Hindi", "in", ["hindi", "(hi)", "hi-"]),
    ("nl", "Neerlandés", "nl", ["dutch", "neerland", "(nl)", "nl-"]),
    ("pl", "Polaco", "pl", ["polish", "polaco", "(pl)", "pl-"]),
    ("tr", "Turco", "tr", ["turkish", "turco", "(tr)", "tr-"]),
    ("sv", "Sueco", "se", ["swedish", "sueco", "(sv)", "sv-"]),
    ("da", "Danés", "dk", ["danish", "danes", "(da)", "da-"]),
    ("no", "Noruego", "no", ["norwegian", "noruego", "(nb)"]),
    ("fi", "Finés", "fi", ["finnish", "fines", "(fi)", "fi-"]),
    ("el", "Griego", "gr", ["greek", "griego", "(el)", "el-"]),
    ("cs", "Checo", "cz", ["czech", "checo", "(cs)", "cs-"]),
    ("hu", "Húngaro", "hu", ["hungarian", "hungar", "(hu)", "hu-"]),
    ("ro", "Rumano", "ro", ["romanian", "rumano", "(ro)", "ro-"]),
    ("sk", "Eslovaco", "sk", ["slovak", "eslovaco", "(sk)", "sk-"]),
    ("th", "Tailandés", "th", ["thai", "tailand", "(th)", "th-"]),
    ("vi", "Vietnamita", "vn", ["vietnam", "(vi)", "vi-"]),
    ("id", "Indonesio", "id", ["indonesian", "indonesio", "(id)"]),
    ("he", "Hebreo", "il", ["hebrew", "hebreo", "(he)", "he-"]),
    ("uk", "Ucraniano", "ua", ["ukrainian", "ucraniano", "(uk)"]),
]


def _voice_lang2(self, name):
    low = name.lower()
    if "multilingual" in low:
        return "multi"
    for code, label, flag, keys in LANG_TABLE:
        if any(k in low for k in keys):
            return code
    return "otro"


def _available_langs(self):
    out = []
    for item in LANG_TABLE:
        code = item[0]
        if any(self._voice_lang2(v) == code
               for v in getattr(self, "_voices", [])):
            out.append(item)
    return out


def _flag_pix(self, code, size=18):
    from PySide6.QtSvg import QSvgRenderer
    from PySide6.QtCore import QByteArray
    import sys
    base = Path(getattr(sys, "_MEIPASS",
                        Path(__file__).resolve().parents[1]))
    fp = base / "assets" / "icons" / "svg" / f"flag_{code}.svg"
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    if fp.exists():
        try:
            r = QSvgRenderer(QByteArray(fp.read_bytes()))
            if r.isValid():
                q = QPainter(pix)
                r.render(q)
                q.end()
                return pix
        except Exception:
            pass
    q = QPainter(pix)
    q.setBrush(QColor("#30363d"))
    q.setPen(Qt.PenStyle.NoPen)
    q.drawEllipse(0, 0, size, size)
    q.end()
    return pix


def _open_filter_menu(self):
    try:
        self._open_filter_menu_impl()
    except Exception:
        import traceback
        traceback.print_exc()


def _open_filter_menu_impl(self):
    from PySide6.QtWidgets import QMenu
    from PySide6.QtCore import QPoint
    m = QMenu(self)
    m.setStyleSheet(
        "QMenu { background: #161b22; border: 1px solid #30363d;"
        " border-radius: 10px; padding: 6px; }"
        " QMenu::item { color: #e6edf3; padding: 6px 20px 6px 10px;"
        " border-radius: 6px; }"
        " QMenu::item:selected { background: #232b3a; }"
        " QMenu::separator { height: 1px; background: #30363d;"
        " margin: 6px 10px; }"
        " QMenu::indicator { width: 14px; height: 14px; }")
    cur = getattr(self, "_extra_filter", None)
    a_all = m.addAction(
        QIcon(make_icon("globe", "#58a6ff", 14)), "Todos los idiomas")
    a_all.setData("all")
    a_all.setCheckable(True)
    a_all.setChecked(cur is None)
    a_pre = m.addAction(
        QIcon(make_icon("crown", "#f5b544", 14)), "Solo Premium")
    a_pre.setData("premium")
    a_pre.setCheckable(True)
    a_pre.setChecked(cur == "premium")
    m.addSeparator()
    for code, label, flag, keys in self._available_langs():
        a = m.addAction(QIcon(self._flag_pix(flag)), label)
        a.setData(code)
        a.setCheckable(True)
        a.setChecked(cur == code)
    m.triggered.connect(self._apply_filter)
    pos = self.filter_btn.mapToGlobal(
        QPoint(0, self.filter_btn.height() + 4))
    m.exec(pos)


def _apply_filter(self, action):
    data = action.data()
    self._extra_filter = None if data == "all" else data
    try:
        self.lang_combo.blockSignals(True)
        if data == "es":
            self.lang_combo.setCurrentIndex(1)
        elif data == "en":
            self.lang_combo.setCurrentIndex(2)
        elif data in (None, "all", "premium"):
            self.lang_combo.setItemText(3, "Ver todos los idiomas")
            self.lang_combo.setItemIcon(
                3, QIcon(self._flag_pixmap("world")))
            self.lang_combo.setCurrentIndex(3)
        else:
            lab = next((it[1] for it in LANG_TABLE if it[0] == data), "Todos")
            flg = next((it[2] for it in LANG_TABLE if it[0] == data), "world")
            self.lang_combo.setItemText(3, lab)
            self.lang_combo.setItemIcon(3, QIcon(self._flag_pix(flg)))
            self.lang_combo.setCurrentIndex(3)
    finally:
        self.lang_combo.blockSignals(False)
    if data == "all":
        title = "Todos los idiomas"
    elif data == "premium":
        title = "Solo Premium"
    else:
        title = next((it[1] for it in LANG_TABLE if it[0] == data),
                     "Voces")
    if hasattr(self, "_panel_title"):
        self._panel_title.setText(title)
    self._refill_combo()
    self._rebuild_cards()
    if getattr(self, "_all_built", False):
        self._rebuild_all_page()
    self.filter_btn.setToolTip(f"Filtro activo: {action.text()}")


MainWindow._voice_lang2 = _voice_lang2
MainWindow._available_langs = _available_langs
MainWindow._flag_pix = _flag_pix
MainWindow._open_filter_menu = _open_filter_menu
MainWindow._open_filter_menu_impl = _open_filter_menu_impl
MainWindow._apply_filter = _apply_filter

MainWindow._configure_groq_key = _configure_groq_key

def _chat_svg(path_data, color, size):
    """Renderiza un path SVG Material como QPixmap."""
    from PySide6.QtSvg import QSvgRenderer
    from PySide6.QtCore import QByteArray
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
           'fill="' + color + '"><path d="' + path_data + '"/></svg>')
    r = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    r.render(p)
    p.end()
    return pm

class _ChatWorker(QThread):
    resultado = Signal(str)

    def __init__(self, texto, historial=None, modo=None):
        super().__init__()
        self._texto = texto
        self._historial = historial or []
        self._modo = modo

    def run(self):
        try:
            from core import brain
            try:
                from PySide6.QtCore import QSettings
                _k = QSettings("WillpoVoice", "WillpoVoice").value(
                    "groq_api_key", "")
                if _k:
                    brain.GROQ_API_KEY = _k
            except Exception:
                pass
            resp = brain.pensar(self._texto, self._historial, self._modo)
        except Exception as exc:
            resp = f"Error de conexi\u00f3n con la IA: {exc}"
        self.resultado.emit(resp)

def _speak_head_icon(size=14):
    return _speak_head_svg(size)

_EYE_ON = ("M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 "
           "11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 "
           "5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 "
           "3-1.34 3-3-1.34-3-3-3z")
_EYE_OFF = ("M12 7c2.76 0 5 2.24 5 5 0 .65-.13 1.26-.36 1.83l2.92 2.92c1.51-"
            "1.26 2.7-2.89 3.43-4.75-1.73-4.39-6-7.5-11-7.5-1.4 0-2.74.25-"
            "3.98.7l2.16 2.16C10.74 7.13 11.35 7 12 7zM2 4.27l2.28 2.28.46.46"
            "C3.08 8.3 1.78 10.02 1 12c1.73 4.39 6 7.5 11 7.5 1.55 0 3.03-.3"
            "4.38-.84l.42.42L19.73 22 21 20.73 3.27 3 2 4.27zM7.53 9.8l1.55"
            "1.55c-.05.21-.08.43-.08.65 0 1.66 1.34 3 3 3 .22 0 .44-.03.65-.08"
            "l1.55 1.55c-.67.37-1.43.59-2.2.59-2.76 0-5-2.24-5-5 0-.77.22-1.53"
            ".59-2.2z")
_ORIG_SELECT = MainWindow._select_voice
_ORIG_FAV = MainWindow._toggle_fav
MainWindow._select_voice = _select_voice_wrapped
MainWindow._toggle_fav = _toggle_fav_wrapped


def _warm_faces(self):
    if getattr(self, "_face_warm", False):
        return
    self._face_warm = True
    self._face_warm_q = list(dict.fromkeys(
        list(PREMIUM_PHOTOS.values()) + ["face_f.png", "face_m.png"]))
    if not hasattr(self, "_face_timer"):
        self._face_timer = QTimer(self)
        self._face_timer.timeout.connect(self._warm_face_step)
    self._face_timer.start(40)


def _warm_face_step(self):
    q = getattr(self, "_face_warm_q", None)
    if not q:
        self._face_timer.stop()
        return
    fname = q.pop(0)
    fpath = self._resource_path(Path("assets") / "icons" / fname)
    if not fpath.exists():
        return
    src = QPixmap(str(fpath))
    if src.isNull():
        return
    for size in (34, 96):
        ckey = (fname, size)
        if ckey in _FACE_CACHE:
            continue
        out = QPixmap(size, size)
        out.fill(Qt.GlobalColor.transparent)
        p = QPainter(out)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        clip = QPainterPath()
        clip.addEllipse(0, 0, size, size)
        p.setClipPath(clip)
        sc = src.scaled(size, size,
                        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                        Qt.TransformationMode.SmoothTransformation)
        p.drawPixmap(0, 0, sc, (sc.width() - size) // 2,
                     (sc.height() - size) // 2, size, size)
        p.end()
        _FACE_CACHE[ckey] = out


MainWindow._warm_faces = _warm_faces
MainWindow._warm_face_step = _warm_face_step
_orig_load_voices = getattr(MainWindow, "_load_voices", None)
if _orig_load_voices is not None:
    def _load_voices_wrapped(self):
        _orig_load_voices(self)
        try:
            QTimer.singleShot(1000, self._warm_faces)
        except Exception:
            pass
    MainWindow._load_voices = _load_voices_wrapped


# REDIRECCION: el rebuild viejo de la pagina Voces ahora usa
# el nuevo (cards grandes + chunked + cache). Sin esto, el
# heart rellenaba all_layout con las cards antiguas chicas.
if hasattr(MainWindow, "_rebuild_all_page"):
    MainWindow._rebuild_all_page = MainWindow._rebuild_voices_page


# ---- i18n startup hook ----
if not getattr(MainWindow, "_retr_hooked", False):
    MainWindow._retr_hooked = True
    _orig_show_i18n = getattr(MainWindow, "showEvent", None)

    def _show_wrap_i18n(self, ev):
        global CURRENT_LANG
        if _orig_show_i18n is not None:
            _orig_show_i18n(self, ev)
        if not getattr(self, "_retr_done", False):
            self._retr_done = True
            try:
                CURRENT_LANG = str(self.settings.get(
                    "lang_pref", "Espa\u00f1ol"))
                self._retranslate()
            except Exception:
                import traceback
                traceback.print_exc()

    MainWindow.showEvent = _show_wrap_i18n

if not getattr(MainWindow, "_proj_hooked", False):
    MainWindow._proj_hooked = True
    _orig_switch_proj = MainWindow._switch_page

    def _switch_wrap_proj(self, idx):
        _orig_switch_proj(self, idx)
        if idx == 4:
            try:
                self._layout_proj_bg()
                self._rebuild_projects()
            except Exception:
                pass

    MainWindow._switch_page = _switch_wrap_proj


# ---- tema claro: activacion diferida ----
LIGHT_MODE = _light_theme_enabled()
if LIGHT_MODE:
    BG = "#f3f5fa"
    SIDE_BG = "#e9edf5"
    CARD = "#ffffff"
    CARD2 = "#f2f4fa"
    BORDER = "#d5dcea"
    TEXT = "#17203a"
    MUTED = "#5b6478"
    _LIGHT_HEX = {
        "#ffffff": "#17203a",
        "#e6edf3": "#17203a", "#eef2ff": "#17203a",
        "#c9d1d9": "#3c465e", "#cfe3ff": "#1d4ed8",
        "#cdd5ea": "#5b6478",
        "#c4b5fd": "#6d28d9", "#a78bfa": "#6d28d9",
        "#bc8cff": "#7c3aed", "#7cb7ff": "#2563eb",
        "#8b949e": "#5b6478", "#8b93b0": "#5b6478",
        "#93a0c2": "#5b6478", "#9aa4b2": "#5b6478",
        "#0b0f1a": "#f3f5fa", "#0d1220": "#ffffff",
        "#10141f": "#ffffff", "#141b30": "#ffffff",
        "#161b22": "#ffffff", "#1a2138": "#eef1f8",
        "#262d3a": "#d5dcea", "#232f4b": "#d5dcea",
        "#30363d": "#d0d7e2", "#232b3a": "#d5dcea",
        "rgba(13,17,26,160)": "rgba(255,255,255,215)",
        "rgba(13,17,26,214)": "rgba(255,255,255,235)",
        "rgba(10,14,24,214)": "rgba(255,255,255,235)",
        "rgba(13,17,26,140)": "rgba(255,255,255,205)",
        "rgba(12,16,28,120)": "rgba(255,255,255,200)",
        "rgba(22,27,34,235)": "rgba(255,255,255,235)",
        "rgba(22,27,34,240)": "rgba(255,255,255,240)",
        "rgba(13,18,32,180)": "rgba(255,255,255,220)",
        # Clone voice page constants
        "#0d1224": "#e9edf5",
        "rgba(17, 24, 39, 180)": "rgba(255, 255, 255, 220)",
        "rgba(15, 22, 41, 180)": "rgba(242, 244, 250, 220)",
        "rgba(11, 17, 32, 180)": "rgba(255, 255, 255, 200)",
        "#1e2942": "#d5dcea",
        "#2a3a5c": "#c0c8d8",
        "#94a3b8": "#3c465e",
        "rgba(255,255,255,6)": "rgba(23,32,58,8)",
        "rgba(255,255,255,14)": "rgba(23,32,58,10)",
        "rgba(88,166,255,25)": "rgba(37,99,235,16)",
        "rgba(148,163,255,20)": "rgba(124,92,255,14)",
    }
    from PySide6.QtWidgets import QWidget as _WBaseL
    _orig_sssL = _WBaseL.setStyleSheet

    def _light_rgb(h):
        return int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)

    def _light_lum(h):
        r, g, b = _light_rgb(h)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    def _light_sat(h):
        r, g, b = _light_rgb(h)
        return max(r, g, b) - min(r, g, b)

    def _translate_light_qss(qss):
        import re as _re
        for _k, _v in {"#c4b5fd": "#6d28d9", "#a78bfa": "#6d28d9",
                       "#bc8cff": "#7c3aed", "#7cb7ff": "#2563eb",
                       "#cfe3ff": "#1d4ed8", "#cdd5ea": "#5b6478",
                       "#93a0c2": "#5b6478"}.items():
            qss = qss.replace(_k, _v)
        for _k, _v in {"#000": "#0b0f1a", "#111": "#10141f",
                       "#222": "#232f4b", "#333": "#30363d",
                       "#444": "#4b5568", "#fff": "#ffffff",
                       "#eee": "#e6edf3", "#ddd": "#c9d1d9"}.items():
            qss = _re.sub(r"(?<![0-9a-fA-F])" + _k + r"(?![0-9a-fA-F])",
                          _v, qss)
        for _sc, _col in (("::groove", "#d5dcea"),
                            ("::add-page", "#d5dcea"),
                            ("::sub-page", "#3b82f6")):
            qss = _re.sub(r"(" + _sc + r"[^;]*?background\s*:\s*)([^;}]+)",
                          lambda m, c=_col: m.group(1) + c, qss)

        def _txt(m):
            h = m.group(2)
            if _light_sat(h) >= 60:
                return m.group(0)
            L = _light_lum(h)
            if L > 190:
                return m.group(1) + "#17203a"
            if L > 150:
                return m.group(1) + "#3c465e"
            if L > 100:
                return m.group(1) + "#5b6478"
            return m.group(0)

        def _bg(m):
            h = m.group(2)
            if _light_sat(h) >= 60:
                return m.group(0)
            if _light_lum(h) < 130:
                return m.group(1) + "#ffffff"
            return m.group(0)

        def _brd(m):
            h = m.group(2)
            if _light_sat(h) >= 60:
                return m.group(0)
            if _light_lum(h) < 130:
                return m.group(1) + "#d5dcea"
            return m.group(0)

        def _rgba(m):
            r, g, b, a = (int(x) for x in m.groups())
            if max(r, g, b) < 80:
                return "rgba(255,255,255,%d)" % a
            if min(r, g, b) > 200 and a < 60:
                return "rgba(23,32,58,%d)" % a
            return m.group(0)

        def _hex8(m):
            aa, rgb = m.group(1), m.group(2)
            if _light_sat("#" + rgb) >= 60:
                return m.group(0)
            if _light_lum("#" + rgb) < 130:
                return "#" + aa + "ffffff"
            return m.group(0)
        qss = _re.sub(r"#([0-9a-fA-F]{2})([0-9a-fA-F]{6})(?![0-9a-fA-F])",
                      _hex8, qss)
        qss = _re.sub(r"(color\s*:\s*)(#[0-9a-fA-F]{6})(?![0-9a-fA-F])", _txt, qss)
        qss = _re.sub(r"(background(?:-color)?\s*:\s*)(#[0-9a-fA-F]{6})(?![0-9a-fA-F])", _bg, qss)
        qss = _re.sub(r"(stop:\d\s*)(#[0-9a-fA-F]{6})(?![0-9a-fA-F])", _bg, qss)
        qss = _re.sub(r"(border[^:;]*:\s*[^;#]*)(#[0-9a-fA-F]{6})(?![0-9a-fA-F])", _brd, qss)
        qss = _re.sub(r"rgba\((\d+),(\d+),(\d+),(\d+)\)", _rgba, qss)
        return qss

    def _sss_lightL(self, qss):
        try:
            if not globals().get("_LIGHT_SUSPEND", False):
                qss = _translate_light_qss(qss)
        except Exception:
            pass
        _orig_sssL(self, qss)

    _WBaseL.setStyleSheet = _sss_lightL


# ---- sombra playerBar en claro (post-show, robusta) ----
if LIGHT_MODE:
    from PySide6.QtWidgets import QGraphicsDropShadowEffect as _QSE
    from PySide6.QtGui import QColor as _QCsh2
    from PySide6.QtCore import QTimer as _QTsh
    _orig_show_sh = MainWindow.show

    def _show_shadow(self):
        _orig_show_sh(self)

        def _apply_sh():
            w = self.findChild(QFrame, "playerBar")
            if w is not None:
                sh = _QSE(w)
                sh.setBlurRadius(24)
                sh.setOffset(0, 6)
                sh.setColor(_QCsh2(90, 100, 130, 180))
                w.setGraphicsEffect(sh)
        _QTsh.singleShot(300, _apply_sh)

    MainWindow.show = _show_shadow
