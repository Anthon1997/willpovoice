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
    QComboBox, QFileDialog, QFrame, QGraphicsDropShadowEffect, QGridLayout,
    QHBoxLayout, QLabel, QLineEdit, QListWidget, QMainWindow, QMenu,
    QMessageBox, QPlainTextEdit, QProgressDialog, QPushButton,
    QScrollArea, QSizePolicy, QSlider, QSpinBox, QStackedWidget,
    QVBoxLayout, QWidget,
)

from PySide6.QtWidgets import QSpacerItem
from app.config import load_settings, save_settings
from core import file_reader, license_manager
from core.audio_exporter import AudioExporter
from core.tts_engine import TTSEngine
from ui.main_window import ExportWorker, LicenseDialog

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

PREMIUM_PHOTOS = {
    "andrew": "ms_andrew.png", "ava": "ms_ava.png", "brian": "ms_brian.png",
    "emma": "ms_emma.png", "florian": "ms_florian.png",
    "giuseppe": "ms_giuseppe.png", "hyunsu": "ms_hyunsu.png",
    "remy": "ms_remy.png", "seraphina": "ms_seraphina.png",
    "william": "ms_william.png", "vivienne": "ms_vivienne.png",
    "thalita": "ms_thalita.png", "elvira": "ms_elvira.png",
    "alonso": "ms_alonso.png", "dalia": "ms_dalia.png",
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
            g = QLabel("WillpoVoice Premium")
            g.setStyleSheet(
                "color: #f5b301; font-size: 10px; font-weight: 600;"
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


class MainWindow(QMainWindow):
    MAX_HISTORY = 10
    preview_changed = Signal(str, bool)

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("naturalvoice_tts.ui")
        self.settings = load_settings()
        self.setWindowTitle("WillpoVoice v1.2.5")
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

    def mouseReleaseEvent(self, event):
        self.clicked.emit()



def _build_ui(self):
    central = QWidget()
    central.setObjectName("centralMain")
    central.setStyleSheet(
        "QWidget#centralMain { background: #0d1424; }"
    )
    self.setCentralWidget(central)
    self.setStyleSheet("QMainWindow { background: #0d1424; }")
    root = QHBoxLayout(central)
    root.setContentsMargins(0, 0, 0, 0)
    root.setSpacing(0)

    # ---------- SIDEBAR ----------
    self.sidebar = QFrame()
    self.sidebar.setFixedWidth(232)
    self.sidebar.setObjectName("sideBar")
    self.sidebar.setStyleSheet(f"QFrame#sideBar {{ background: {SIDE_BG}; border: none; }}")
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
    self._logo_ver = QLabel("v1.2.5")
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
        ("folder", "Proyectos", 4), ("gear", "Ajustes", 5),
    ):
        btn = NavButton(glyph, text)
        btn.clicked.connect(lambda _=False, pg=page: self._switch_page(pg))
        sb.addWidget(btn)
        self._nav.append((btn, page))
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
    sb.addStretch()
    self._prem_card = QFrame()
    self._prem_card.setStyleSheet(
        "QFrame { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
        " stop:0 #241a3d, stop:1 #3b2a63); border-radius: 14px; }"
    )
    pl = QVBoxLayout(self._prem_card)
    pl.setContentsMargins(14, 14, 14, 14)
    pt = QLabel("👑  WillpoVoice Premium")
    pt.setStyleSheet(f"color: {TEXT}; font-size: 12px; font-weight: 700; background: transparent;")
    pd = QLabel("Desbloquea todas las voces y funciones premium.")
    pd.setWordWrap(True)
    pd.setStyleSheet(f"color: {MUTED}; font-size: 10px; background: transparent;")
    pb = QPushButton("✨ Ver planes")
    pb.setCursor(Qt.CursorShape.PointingHandCursor)
    pb.setStyleSheet(
        "QPushButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
        f" stop:0 {BLUE}, stop:1 {PURPLE}); color: white; border: none;"
        " border-radius: 8px; padding: 7px 12px; font-weight: 600; }"
    )
    pb.clicked.connect(self.open_support)
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
    header.setFixedHeight(190)
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
    if cp.exists():
        cover.setPixmap(QPixmap(str(cp)))
    cover.setScaledContents(True)
    cover.setStyleSheet("background: transparent; border-radius: 16px;")
    hg.addWidget(cover, 0, 0)
    titles = QWidget()
    titles.setStyleSheet("background: transparent;")
    tl2 = QVBoxLayout(titles)
    tl2.setContentsMargins(24, 16, 0, 16)
    t1 = QLabel("WillpoVoice")
    t1.setStyleSheet("color: white; font-size: 26px; font-weight: 700; background: transparent;")
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
        stats.addWidget(s)
    p0.addLayout(stats)

    card = QFrame()
    card.setObjectName("convCard")
    card.setStyleSheet(f"QFrame#convCard {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 16px; }}")
    cl = QVBoxLayout(card)
    cl.setContentsMargins(18, 14, 18, 16)
    cl.setSpacing(12)
    top = QHBoxLayout()
    self.tab_text = TabButton("Texto manual")
    self.tab_file = TabButton("Importar archivo")
    self.tab_text.set_active(True)
    self.tab_text.setIcon(QIcon(make_icon("text", BLUE, 14)))
    self.tab_text.setIconSize(QSize(14, 14))
    self.tab_file.setIcon(QIcon(make_icon("doc", MUTED, 14)))
    self.tab_file.setIconSize(QSize(14, 14))
    self.tab_file.clicked.connect(self._open_document_dialog)
    top.addWidget(self.tab_text)
    top.addWidget(self.tab_file)
    top.addStretch()
    self.btn_clear = ToolButton("trash", "Limpiar")
    self.btn_paste = ToolButton("paste", "Pegar")
    top.addWidget(self.btn_clear)
    top.addWidget(self.btn_paste)
    cl.addLayout(top)

    self.text_edit = QPlainTextEdit()
    self.text_edit.setPlaceholderText("Escribe aquí el texto que quieres convertir a voz...")
    self.text_edit.setFixedHeight(120)
    self.text_edit.setMinimumWidth(150)
    self.text_edit.setStyleSheet(
        f"QPlainTextEdit {{ background: #0d1424; color: {TEXT};"
        f" border: 1px solid {BORDER}; border-radius: 12px; padding: 10px;"
        " font-size: 14px; selection-background-color: #3b82f6; }"
    )
    cl.addWidget(self.text_edit)
    self.counter_label = QLabel("0 / 5000")
    self.counter_label.setAlignment(Qt.AlignmentFlag.AlignRight)
    self.counter_label.setStyleSheet(
        f"color: {MUTED}; font-size: 10px; background: transparent;"
    )
    cl.addWidget(self.counter_label)

    sel = QHBoxLayout()
    sel.setSpacing(12)
    combo_qss = (
        f"QComboBox {{ background: #0d1424; color: {TEXT}; border: 1px solid"
        f" {BORDER}; border-radius: 10px; padding: 7px 12px;"
        " font-size: 13px; }"
        " QComboBox:hover { border: 1px solid #34406b; }"
        " QComboBox::drop-down { border: none; width: 30px; }"
        f" QComboBox QAbstractItemView {{ background: #10162a; color: {TEXT};"
        f" border: 1px solid {BORDER}; selection-background-color: {CARD2};"
        " padding: 6px; }"
    )
    col1 = QVBoxLayout()
    col1.setSpacing(4)
    l1 = QLabel("Idioma")
    l1.setStyleSheet(
        f"color: {MUTED}; font-size: 11px; background: transparent;"
    )
    self.lang_combo = QComboBox()
    self.lang_combo.addItems(["Multilingüe Premium", "Español (España)", "Inglés (EEUU)", "Todos"])
    self.lang_combo.setItemIcon(0, QIcon(make_icon("crown", "#f5b544", 16)))
    self.lang_combo.setItemIcon(1, QIcon(self._flag_pixmap("es")))
    self.lang_combo.setItemIcon(2, QIcon(self._flag_pixmap("us")))
    self.lang_combo.setItemIcon(3, QIcon(self._flag_pixmap("world")))
    self.lang_combo.currentIndexChanged.connect(
        lambda _i: self._on_lang_changed())
    self.lang_combo.setCurrentIndex(0)
    self.lang_combo.setStyleSheet(combo_qss)
    self.lang_combo.setFixedHeight(38)
    self.lang_combo.setSizePolicy(
        QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    self.lang_combo.setMinimumWidth(0)
    col1.addWidget(l1)
    col1.addWidget(self.lang_combo)
    sel.addLayout(col1, 1)
    col2 = QVBoxLayout()
    col2.setSpacing(4)
    l2 = QLabel("Voz seleccionada")
    l2.setStyleSheet(
        f"color: {MUTED}; font-size: 11px; background: transparent;"
    )
    self.voice_combo = QComboBox()
    self.voice_combo.setStyleSheet(
        combo_qss + " QComboBox { padding: 7px 84px 7px 12px; }"
    )
    self.pro_badge = QLabel("Pro", self.voice_combo)
    self.pro_badge.setStyleSheet(
        f"background: {PURPLE}; color: white; border-radius: 6px;"
        " font-size: 9px; font-weight: 700; padding: 3px 6px;"
    )
    self.pro_badge.setAttribute(
        Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    self.voice_combo.setFixedHeight(38)
    self.voice_combo.setSizePolicy(
        QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    self.voice_combo.setMinimumWidth(0)
    self.voice_combo.installEventFilter(self)
    for _cb in (self.lang_combo, self.voice_combo):
        _cb.setFixedHeight(38)
        _cb.setIconSize(QSize(18, 14))
        _cb.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    col2.addWidget(l2)
    col2.addWidget(self.voice_combo)
    sel.addLayout(col2, 1)
    cl.addLayout(sel)

    self.adv_button = QPushButton("＞  Opciones avanzadas")
    self.adv_button.setCursor(Qt.CursorShape.PointingHandCursor)
    self.adv_button.setStyleSheet(
        f"QPushButton {{ background: {CARD2}; color: {TEXT}; border: 1px solid {BORDER}; border-radius: 10px; padding: 8px 14px; text-align: left; }}"
    )
    cl.addWidget(self.adv_button)
    self.adv_widget = QWidget()
    al = QHBoxLayout(self.adv_widget)
    al.setContentsMargins(0, 4, 0, 4)
    al.addWidget(QLabel("Velocidad"))
    self.rate_slider = QSlider(Qt.Orientation.Horizontal)
    self.rate_slider.setRange(-10, 10)
    al.addWidget(self.rate_slider, 1)
    al.addSpacing(14)
    al.addWidget(QLabel("Volumen"))
    self.volume_slider = QSlider(Qt.Orientation.Horizontal)
    self.volume_slider.setRange(0, 100)
    self.volume_slider.setValue(100)
    al.addWidget(self.volume_slider, 1)
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
    p0.addLayout(acts)
    self._add_neon(self.speak_button, BLUE)
    self._add_neon(self.stop_button, MAGENTA)
    self._add_neon(self.export_button, TEAL)

    player = QFrame()
    player.setFixedHeight(64)
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
    self.pages.addWidget(page0)

    page1 = QWidget()
    h1 = QVBoxLayout(page1)
    h1.setContentsMargins(20, 16, 20, 16)
    h1.setSpacing(12)
    ht = QLabel("Historial")
    ht.setStyleSheet(f"color: {TEXT}; font-size: 20px; font-weight: 700;")
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
    self.history_layout.setContentsMargins(0, 0, 6, 0)
    self.history_layout.setSpacing(8)
    self.hist_scroll.setWidget(self.hist_container)
    self.btn_clear_hist = QPushButton("Limpiar historial")
    self.btn_clear_hist.setCursor(Qt.CursorShape.PointingHandCursor)
    self.btn_clear_hist.setStyleSheet(
        "QPushButton { background: transparent; color: " + RED + ";"
        f" border: 1px solid {BORDER}; border-radius: 10px;"
        " padding: 8px 16px; }"
        " QPushButton:hover { background: rgba(239,68,68,40); }"
    )
    h1.addWidget(ht)
    h1.addWidget(self.hist_scroll, 1)
    h1.addWidget(self.btn_clear_hist, 0, Qt.AlignmentFlag.AlignLeft)
    self.pages.addWidget(page1)

    page2 = QWidget()
    v2 = QVBoxLayout(page2)
    v2.setContentsMargins(20, 16, 20, 16)
    vt = QLabel("Voces")
    vt.setStyleSheet(f"color: {TEXT}; font-size: 20px; font-weight: 700;")
    self.all_scroll = QScrollArea()
    self.all_scroll.setWidgetResizable(True)
    self.all_scroll.setFrameShape(QFrame.Shape.NoFrame)
    self.all_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    self.all_scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
    self.all_container = QWidget()
    self.all_container.setStyleSheet("background: transparent;")
    self.all_layout = QVBoxLayout(self.all_container)
    self.all_layout.setContentsMargins(0, 0, 6, 0)
    self.all_layout.setSpacing(8)
    self.all_scroll.setWidget(self.all_container)
    v2.addWidget(vt)
    v2.addWidget(self.all_scroll, 1)
    self.pages.addWidget(page2)

    page3 = QWidget()
    f3 = QVBoxLayout(page3)
    f3.setContentsMargins(20, 16, 20, 16)
    ft = QLabel("Favoritos")
    ft.setStyleSheet(f"color: {TEXT}; font-size: 20px; font-weight: 700;")
    self.fav_scroll = QScrollArea()
    self.fav_scroll.setWidgetResizable(True)
    self.fav_scroll.setFrameShape(QFrame.Shape.NoFrame)
    self.fav_scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
    self.fav_container = QWidget()
    self.fav_container.setStyleSheet("background: transparent;")
    self.fav_layout = QVBoxLayout(self.fav_container)
    self.fav_layout.setContentsMargins(0, 0, 6, 0)
    self.fav_layout.setSpacing(8)
    self.fav_scroll.setWidget(self.fav_container)
    f3.addWidget(ft)
    f3.addWidget(self.fav_scroll, 1)
    self.pages.addWidget(page3)

    page4 = QWidget()
    pr4 = QVBoxLayout(page4)
    pt4 = QLabel("Proyectos")
    pt4.setStyleSheet(f"color: {TEXT}; font-size: 20px; font-weight: 700;")
    ps4 = QLabel("Próximamente podrás guardar y organizar tus proyectos de voz.")
    ps4.setStyleSheet(f"color: {MUTED}; font-size: 13px;")
    pr4.addWidget(pt4)
    pr4.addWidget(ps4)
    pr4.addStretch()
    self.pages.addWidget(page4)

    page5 = QWidget()
    a5 = QVBoxLayout(page5)
    a5.setContentsMargins(20, 16, 20, 16)
    at5 = QLabel("Ajustes")
    at5.setStyleSheet(f"color: {TEXT}; font-size: 20px; font-weight: 700;")
    row5 = QHBoxLayout()
    row5.addWidget(QLabel("Límite de caracteres:"))
    self.limit_spin = QSpinBox()
    self.limit_spin.setRange(500, 20000)
    self.limit_spin.setSingleStep(500)
    self.limit_spin.setValue(int(self.settings.get("char_limit", 5000)))
    row5.addWidget(self.limit_spin)
    row5.addStretch()
    self.license_label = QLabel("")
    self.license_label.setStyleSheet(f"color: {MUTED};")
    a5.addWidget(at5)
    a5.addLayout(row5)
    a5.addWidget(self.license_label)
    a5.addStretch()
    self.pages.addWidget(page5)

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
    rt = QLabel("Voces recomendadas")
    rt.setStyleSheet(f"color: {TEXT}; font-size: 13px; font-weight: 700;")
    self.btn_ver_all = ToolButton("", "Ver todas")
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
    rp.addLayout(search_row)
    tabs = QHBoxLayout()
    tabs.setSpacing(4)
    self.rtab_all = TabButton("Todas")
    self.rtab_pro = TabButton("👑 Premium")
    self.rtab_fav = TabButton("❤ Favoritas")
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
    self.theme_button.clicked.connect(self._toggle_theme_msg)
    self.btn_clear.clicked.connect(lambda: self.text_edit.clear())
    self.btn_paste.clicked.connect(lambda: self.text_edit.paste())
    self.btn_clear_hist.clicked.connect(self.clear_history)
    self.text_edit.textChanged.connect(self.update_counter)
    self.voice_combo.currentIndexChanged.connect(lambda _i: self._on_combo_voice())
    self.search_edit.textChanged.connect(lambda _t: self._rebuild_cards())
    self.rtab_all.clicked.connect(lambda: self._set_rtab("todas"))
    self.rtab_pro.clicked.connect(lambda: self._set_rtab("premium"))
    self.rtab_fav.clicked.connect(lambda: self._set_rtab("favoritas"))
    self.btn_ver_all.clicked.connect(lambda: self._switch_page(2))
    self.adv_button.clicked.connect(self._toggle_adv)
    self.vol_slider.valueChanged.connect(lambda v: self.engine.set_volume(v))
    self.volume_slider.valueChanged.connect(lambda v: self.engine.set_volume(v))
    self.limit_spin.valueChanged.connect(
        lambda v: self.settings.__setitem__("char_limit", v))


def _switch_page(self, index):
    self.pages.setCurrentIndex(index)
    for i, (btn, _pg) in enumerate(self._nav):
        btn.set_active(i == index)
    self.right_panel.setVisible(index == 0)
    if index == 2 and not getattr(self, "_all_built", False):
        self._all_built = True
        self._rebuild_all_page()
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
    card = VoiceCard(self, name, premium,
                     name == getattr(self, "_selected_voice", ""), name in favs)
    card.clicked.connect(lambda n=name: self._select_voice(n))
    card.fav_toggled.connect(lambda n=name: self._toggle_fav(n))
    card.preview_toggled.connect(lambda n=name: self._toggle_preview(n))
    layout.addWidget(card)


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
    out = []
    for name in names:
        vl = self._voice_lang(name)
        if lang.startswith("Espa") and vl != "es":
            continue
        if lang.startswith("Ingl") and vl != "en":
            continue
        if lang.startswith("Multiling") and not self._is_premium(name):
            continue
        out.append(name)
    return out


def _refill_combo(self):
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


def _on_lang_changed(self):
    self._refill_combo()
    self._rebuild_cards()


def _rebuild_cards(self):
    self._clear_layout(self.voice_cards_layout)
    q = self.search_edit.text().strip().lower()
    self._rec_names = []
    for name in getattr(self, "_voices", []):
        premium = self._is_premium(name)
        if getattr(self, "_rtab", "todas") == "premium" and not premium:
            continue
        if getattr(self, "_rtab", "todas") == "favoritas" and name not in self._favorites():
            continue
        if q and q not in name.lower():
            continue
        vl = self._voice_lang(name)
        lang = self.lang_combo.currentText()
        if lang.startswith("Espa") and vl != "es":
            continue
        if lang.startswith("Ingl") and vl != "en":
            continue
        if lang.startswith("Multiling") and not premium:
            continue
        self._rec_names.append(name)
    self._rec_shown = 0
    self._rec_more_btn = None
    self._append_rec_cards()


def _append_rec_cards(self):
    btn = getattr(self, "_rec_more_btn", None)
    if btn is not None:
        self.voice_cards_layout.removeWidget(btn)
        btn.deleteLater()
        self._rec_more_btn = None
    chunk = self._rec_names[self._rec_shown:self._rec_shown + 30]
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
    self._all_names = list(getattr(self, "_voices", []))
    self._all_shown = 0
    self._all_more_btn = None
    self._append_all_cards()


def _append_all_cards(self):
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
    for name in getattr(self, "_voices", []):
        if name in self._favorites():
            self._make_card(name, self.fav_layout)
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
        self.statusBar().showMessage(f"Voz cambiada: {voz_texto}")
        self._last_synth_key = None
        if was_active:
            self.speak_text()
    except Exception as exc:
        self.statusBar().showMessage(f"Error al cambiar voz: {exc}")



def _select_voice(self, name):
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


def _toggle_adv(self):
    show = not self.adv_widget.isVisible()
    self.adv_widget.setVisible(show)
    self.adv_button.setText(
        "＞  Opciones avanzadas" if not show else "＜  Opciones avanzadas")


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
        if _time.time() - getattr(self, "_resume_at", 0.0) < 1.0:
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
        try:
            self.engine.stop()
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
        self.engine.set_rate(self.rate_slider.value())
        self.engine.set_volume(self.volume_slider.value())
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
        self.engine.speak_async(text)
        self.player_timer.start(100)
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
    menu = QMenu(self)
    wav = menu.addAction("Audio WAV  (.wav, sin compresion)")
    mp3 = menu.addAction("Audio MP3  (.mp3, comprimido)")
    action = menu.exec(self.export_button.mapToGlobal(
        QPoint(0, self.export_button.height())))
    if action == wav:
        self.export_wav()
    elif action == mp3:
        self.export_mp3()


def export_wav(self):
    text = self.text_edit.toPlainText().strip()
    if not text:
        self.statusBar().showMessage("Escribe un texto antes de exportar.")
        return
    path, _ = QFileDialog.getSaveFileName(self, "Guardar audio WAV",
                                          "willpovoice_audio.wav",
                                          "Archivos WAV (*.wav)")
    if not path:
        return
    self._run_export(text, path, False)


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
    self._run_export(text, tempfile.mktemp(suffix=".wav"), True)


def _run_export(self, text, path, is_mp3):
    voice = self.voice_combo.currentData(Qt.ItemDataRole.UserRole)
    self.statusBar().showMessage("Exportando audio...")
    self.export_worker = ExportWorker(
        exporter=self.exporter, text=text, path=path, voice=voice,
        rate=self.rate_slider.value(), volume=self.volume_slider.value())
    self.export_worker.export_ok.connect(self.on_export_ok)
    self.export_worker.export_error.connect(self.on_export_error)
    self.export_worker.start()


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
    self.statusBar().showMessage(f"Audio guardado en: {final_path}")
    QMessageBox.information(self, "Exportación exitosa",
                            f"El audio se guardó en: {final_path}")


def on_export_error(self, message):
    QMessageBox.warning(self, "Error",
                        f"No se pudo exportar el audio: {message}")


def _load_history(self):
    self._clear_layout(self.history_layout)
    self._history_full = []
    items = self.settings.get("history", [])
    for idx, it in enumerate(items):
        entry = it if isinstance(it, dict) else {
            "content": it, "label": "Texto manual"}
        self._history_full.append(entry)
        card = HistoryCard(self, entry)
        card.load_clicked.connect(lambda i=idx: self._load_entry(i))
        card.delete_clicked.connect(lambda i=idx: self._delete_entry(i))
        self.history_layout.addWidget(card)
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
    entry = {"content": text, "label": label}
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
    QMessageBox.information(
        self, "Ayuda de WillpoVoice",
        "1. Elige una voz en el panel derecho.\n"
        "2. Escribe o pega tu texto.\n"
        "3. Pulsa Reproducir para escucharlo.\n"
        "4. Usa Exportar para guardar WAV/MP3.\n"
        "5. Marca voces con el corazón para favoritas.")


def _check_license(self):
    state, days_left = license_manager.check_status()
    if state == "licensed":
        self.license_label.setText("Version licenciada.")
        self.statusBar().showMessage("Version licenciada.")
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
        self.license_label.setText("Version licenciada.")
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
    except Exception:
        self.logger.exception("Error al cerrar.")
    event.accept()


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
MainWindow._load_voices = _load_voices
MainWindow._on_combo_voice = _on_combo_voice
MainWindow._select_voice = _select_voice
MainWindow._toggle_fav = _toggle_fav
MainWindow.update_counter = update_counter
MainWindow._copy_text = _copy_text
MainWindow._open_document_dialog = _open_document_dialog
MainWindow._toggle_adv = _toggle_adv
MainWindow._toggle_theme_msg = _toggle_theme_msg
MainWindow._fmt_time = _fmt_time
MainWindow._tick_player = _tick_player
MainWindow.speak_text = speak_text
MainWindow.stop_speech = stop_speech
MainWindow._show_export_menu = _show_export_menu
MainWindow.export_wav = export_wav
MainWindow.export_mp3 = export_mp3
MainWindow._run_export = _run_export
MainWindow.on_export_ok = on_export_ok
MainWindow.on_export_error = on_export_error
MainWindow._load_history = _load_history
MainWindow.clear_history = clear_history
MainWindow._add_to_history = _add_to_history
MainWindow.open_support = open_support
MainWindow.show_help = show_help
MainWindow._check_license = _check_license
MainWindow.showEvent = showEvent
MainWindow.closeEvent = closeEvent
MainWindow._current_voice = _current_voice


def eventFilter(self, obj, event):
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
                    tok = None
                    for tk in sapi.GetVoices():
                        if tk.GetDescription() == item:
                            tok = tk
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
            self.player_timer.start(100)
            self._set_player_icon(True, loading=False)
            self.statusBar().showMessage("Reanudando reproduccion...")
        except Exception:
            pass


def _toggle_preview(self, name):
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
    self.statusBar().showMessage(f"Previsualizando: {name}")
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
            self.player_timer.start(100)
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
    except Exception:
        pass
    import time as _time
    self._resume_offset = off
    self._saw_running = False
    self._paused = False
    self._resume_at = _time.time()
    self._seconds = ratio * max(1.0, getattr(self, "_est_seconds", 1.0))
    self.engine.speak_async(sub)
    self.player_timer.start(100)
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
        self.statusBar().showMessage(f"Voz lista: {name}")


def _deferred_rebuilds(self):
    for w in self.findChildren(VoiceCard):
        sel = (w.voice_name == self._selected_voice)
        if getattr(w, "_is_sel", None) != sel:
            w._is_sel = sel
            w.set_selected(sel)


def _deferred_license(self):
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
MainWindow._toggle_preview = _toggle_preview
MainWindow._stop_preview = _stop_preview
MainWindow._check_preview_end = _check_preview_end
MainWindow._avatar_pixmap_cached = _avatar_pixmap_cached

MainWindow._get_preview_worker = _get_preview_worker

MainWindow._voice_lang = _voice_lang

MainWindow._lang_filtered = _lang_filtered

MainWindow._refill_combo = _refill_combo

MainWindow._on_lang_changed = _on_lang_changed

MainWindow._on_slider_pressed = _on_slider_pressed

MainWindow._on_slider_released = _on_slider_released
