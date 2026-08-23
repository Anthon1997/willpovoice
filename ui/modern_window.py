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
from app.version import APP_VERSION
from core import file_reader, license_manager
from core import trial_tokens
from core.audio_exporter import AudioExporter
from core.tts_engine import TTSEngine
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
        self.setFixedHeight(40)
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

    self.adv_button = AdvButton()
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
    t1 = QLabel("Configura tu API Key de Groq")
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
        ("shield", "100% Seguro",
         "Tu clave se almacena de forma segura y encriptada."),
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
    self._groq_key_input.setFixedHeight(40)
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
                  "(sin tarjeta de crédito)")
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
                  "tu clave nunca sale de tu equipo.")
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
    self._chat_input.setFixedHeight(40)
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

    self.pages.addWidget(page5)

    page6 = QWidget()
    a5 = QVBoxLayout(page6)
    a5.setContentsMargins(20, 16, 20, 16)
    at5 = QLabel("Ajustes")
    at5.setStyleSheet(f"color: {TEXT}; font-size: 20px; font-weight: 700;")
    row5 = QHBoxLayout()
    row5.addWidget(QLabel("Límite de caracteres:"))
    self.limit_spin = QSpinBox()
    self.limit_spin.setRange(500, 20000)
    self.limit_spin.setSingleStep(500)
    self.limit_spin.setValue(min(int(self.settings.get("char_limit", 5000)), self._plan_char_limit()))
    row5.addWidget(self.limit_spin)
    row5.addStretch()
    self.license_label = QLabel("")
    self.license_label.setStyleSheet(f"color: {MUTED};")
    a5.addWidget(at5)
    a5.addLayout(row5)
    a5.addWidget(self.license_label)
    a5.addStretch()
    self.pages.addWidget(page6)

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
    self._panel_title = QLabel("Solo Premium")
    rt = self._panel_title
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
    self.filter_btn.clicked.connect(self._open_filter_menu)
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
    self.text_edit.textChanged.connect(self._on_text_limited)
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
    self.pages.setCurrentIndex(index)
    if index == 5:
        self._layout_chat_bg()
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
    from PySide6.QtWidgets import QSizePolicy
    card.setSizePolicy(QSizePolicy.Policy.Expanding,
                       QSizePolicy.Policy.Fixed)
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
    extra = getattr(self, "_extra_filter", None)
    out = []
    for name in names:
        vl = self._voice_lang(name)
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
    for name in sorted(getattr(self, "_voices", []), key=self._sort_key):
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
    self._animate_text_height(78 if show else 120)
    try:
        self.adv_button.set_expanded(show)
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
            " font-size: 10px; font-weight: 700;")
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
    self._refresh_token_chip(state)

    try:
        from PySide6.QtWidgets import QMessageBox
        _st, _dl = license_manager.check_status()
        if _st == "trial" and _dl == 2:
            QTimer.singleShot(1200, lambda: QMessageBox.information(
                self, "Prueba gratuita",
                "Tu periodo de prueba termina en 2 dias.\n"
                f"Te quedan {trial_tokens.balance():,} tokens de prueba.\n\n"
                "Compra un plan para no perder el acceso."))
    except Exception:
        pass
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
        self._seg_queue = []  # seg-clear
    except Exception:
        self.logger.exception("Error al cerrar.")
    event.accept()


def _plan_char_limit(self):
    from core import license_manager
    details = license_manager.license_details()
    tier = details.get("tier", "")
    if "por vida" in tier.lower() or "lifetime" in tier.lower():
        return 999999
    if "mensual" in tier.lower():
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
MainWindow._load_voices = _load_voices
MainWindow._on_combo_voice = _on_combo_voice
MainWindow._select_voice = _select_voice
MainWindow._toggle_fav = _toggle_fav
MainWindow.update_counter = update_counter
MainWindow._copy_text = _copy_text
MainWindow._open_document_dialog = _open_document_dialog
MainWindow._toggle_adv = _toggle_adv
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
MainWindow.showEvent = showEvent
MainWindow.closeEvent = closeEvent
MainWindow._current_voice = _current_voice


def eventFilter(self, obj, event):
    try:
        from PySide6.QtCore import QEvent
        if obj is getattr(self, "_chat_page", None) and \
                event.type() == QEvent.Type.Resize:
            self._layout_chat_bg()
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
            self.player_timer.start(50)
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
    try:
        from PySide6.QtCore import QSettings
        _s = QSettings("WillpoVoice", "WillpoVoice")
        if str(_s.value("lic_dialog_ack", "0")) in ("1", "true", "True"):
            return
        _s.setValue("lic_dialog_ack", "1")
    except Exception:
        pass
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


def _sort_key(self, name):
    low = (name or "").lower()
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
    try:
        if not self._trial_active():
            return True
        if trial_tokens.balance() < trial_tokens.cost_for(text):
            self._show_no_tokens()
            return False
        return True
    except Exception:
        return True


def _trial_spend(self, text):
    try:
        state, _ = license_manager.check_status()
        if state != "trial":
            return
        ok, cost, bal = trial_tokens.spend(text)
        if ok:
            self._update_token_chip()
            self.statusBar().showMessage(
                f"Conversion: -{cost} tokens · saldo {bal:,}")
    except Exception:
        pass


def _update_token_chip(self):
    txt = getattr(self, "_token_chip_text", None)
    if txt is None:
        return
    txt.setText(f"{trial_tokens.balance():,} tokens")


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
        txt.setText(f"{trial_tokens.balance():,} tokens")
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
    d.setWindowTitle("Compra Tokens")
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
    sub = QLabel("M\u00e1s tokens, m\u00e1s posibilidades.\n"
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
        ("coins", "#f5b544", "Tokens", "20,000 por un mes", "app"),
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
    old_price = QLabel("S/ 10")
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
    b_dc.setFixedHeight(40)
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
DISCORD_URL = ""
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
        v.setContentsMargins(28, 24, 28, 22)
        v.setSpacing(12)
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


class PlansDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setModal(True)
        self.setFixedWidth(470)
        self.setWindowTitle("WillpoVoice Premium")
        self.setStyleSheet("PlansDialog { background: #0b0e14; }")
        self._bg = QLabel(self)
        self._bg.setStyleSheet("background: transparent;")
        self._bg.lower()
        v = QVBoxLayout(self)
        v.setContentsMargins(26, 22, 26, 20)
        v.setSpacing(12)
        hd = QLabel()
        hd.setPixmap(make_icon("crown", "#f5b544", 34))
        hd.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(hd)
        t1 = QLabel("Elige tu plan")
        t1.setStyleSheet(
            "color: #e6edf3; font-size: 20px; font-weight: 800;")
        t1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(t1)
        t2 = QLabel("Voces premium reales, sin limites artificiales.")
        t2.setStyleSheet("color: #8b949e; font-size: 11.5px;")
        t2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(t2)
        self._card(v, "flask", "#8b949e", "Gratis", "S/ 0",
                   ["7 dias de prueba", "5,000 tokens incluidos",
                    "Hasta 5,000 caracteres por conversión",
                    "Todas las voces premium"],
                   btn=("Iniciar prueba gratuita", False),
                   on_buy=self._start_trial)
        self._card(v, "coins", "#58a6ff", "Mensual", "S/ 10",
                   ["20,000 tokens al mes", "Hasta 20,000 caracteres",
                    "Todas las voces premium", "Soporte por Discord"],
                   btn=("Comprar", False),
                   on_buy=lambda: self._buy(
                       "Mensual", 10, YAPE_URL_MENSUAL))
        self._card(v, "sparkles", "#f5b544", "Lifetime", "S/ 30",
                   ["Uso ILIMITADO, sin tokens", "Caracteres ILIMITADOS",
                    "Voces nuevas para siempre", "Soporte prioritario de por vida"],
                   btn=("Comprar", True), badge="Recomendado",
                   on_buy=lambda: self._buy(
                       "Lifetime", 30, YAPE_URL_LIFETIME))

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
        out.fill(QColor("#0b0e14"))
        p = QPainter(out)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        scaled = QPixmap(str(src)).scaled(
            w, h, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation)
        p.drawPixmap((w - scaled.width()) // 2,
                     (h - scaled.height()) // 2, scaled)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(11, 14, 19, 205))
        p.drawRect(0, 0, w, h)
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

    def _card(self, v, icon, color, name, price, feats, btn=None,
              badge=None, on_buy=None):
        card = QFrame()
        card.setObjectName("plancard_" + name)
        border = "#7c5cff" if badge else "#30363d"
        card.setStyleSheet(
            "#plancard_" + name + " { background: #161b22; border: 1px solid "
            + border + "; border-radius: 12px; }")
        cv = QVBoxLayout(card)
        cv.setContentsMargins(14, 12, 14, 12)
        cv.setSpacing(8)
        top = QHBoxLayout()
        icl = QLabel()
        icl.setPixmap(make_icon(icon, color, 18))
        top.addWidget(icl)
        nm = QLabel(name + ("  ★ " + badge if badge else ""))
        nm.setStyleSheet(
            "color: #e6edf3; font-size: 13px; font-weight: 800;")
        top.addWidget(nm)
        top.addStretch(1)
        pr = QLabel(price)
        pr.setStyleSheet(
            "color: " + color + "; font-size: 13px; font-weight: 800;")
        top.addWidget(pr)
        cv.addLayout(top)
        for f in feats:
            fr = QHBoxLayout()
            fr.setSpacing(8)
            ck = QLabel()
            ck.setPixmap(make_icon("check", "#2ea043", 12))
            fr.addWidget(ck)
            fl = QLabel(f)
            fl.setStyleSheet("color: #c9d1d9; font-size: 11px;")
            fr.addWidget(fl)
            fr.addStretch(1)
            cv.addLayout(fr)
        if btn:
            b = QPushButton(btn[0])
            b.setFixedHeight(36)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            if btn[1]:
                b.setStyleSheet(
                    "QPushButton { background: qlineargradient(x1:0,y1:0,"
                    "x2:1,y2:0, stop:0 #6d5df0, stop:0.5 #7c5cff,"
                    " stop:1 #6d5df0); color: white; border: none;"
                    " border-radius: 9px; font-weight: 700; }"
                    " QPushButton:hover { background: #8d75ff; }")
            else:
                b.setStyleSheet(
                    "QPushButton { background: transparent;"
                    " color: #58a6ff; border: 1px solid #58a6ff;"
                    " border-radius: 9px; font-weight: 600; }"
                    " QPushButton:hover { background: rgba(88,166,255,35); }")
            if on_buy:
                b.clicked.connect(on_buy)
            cv.addWidget(b)
        v.addWidget(card)

    def _buy(self, plan, price, yape_url):
        d = PaymentDialog(self, plan, price, yape_url)
        d.exec()


def _open_plans(self):
    dlg = PlansDialog(self)
    dlg.exec()




def _configure_groq_key(self):
    self._switch_page(5)
    vis = self._chat_banner.isVisible()
    self._chat_banner.setVisible(not vis)
    if not vis:
        try:
            self._groq_key_input.setFocus()
        except Exception:
            pass


from PySide6.QtCore import QThread as _QThread, Signal as _ChatSignal


class _ChatWorker(_QThread):
    resultado = _ChatSignal(str)

    def __init__(self, texto, historial=None, modo=None):
        super().__init__()
        self._texto = texto
        self._historial = historial or []
        self._modo = modo

    def run(self):
        try:
            from core import brain
            resp = brain.pensar(self._texto, self._historial, self._modo)
        except Exception as exc:
            resp = f"Error de conexion con la IA: {exc}"
        self.resultado.emit(resp)


def _send_chat_message(self):
    import traceback
    try:
        text = self._chat_input.text().strip()
        if not text:
            return
        from PySide6.QtCore import QSettings
        settings = QSettings("WillpoVoice", "WillpoVoice")
        api_key = settings.value("groq_api_key", "")
        if not api_key:
            self._chat_banner.setVisible(True)
            return
        from core import brain
        brain.GROQ_API_KEY = api_key
        self._add_chat_bubble(text, is_user=True)
        self._chat_input.clear()
        if not hasattr(self, "_chat_history"):
            self._chat_history = []
        hist = list(self._chat_history)
        self._chat_history.append({"role": "user", "content": text})
        thinking = self._add_chat_bubble(
            "Pensando...", is_user=False, temp=True)
        worker = _ChatWorker(text, hist, getattr(self, "_chat_mode", None))
        self._chat_worker = worker
        worker.resultado.connect(
            lambda r: self._on_chat_response(r, thinking))
        worker.start()
    except Exception as exc:
        traceback.print_exc()
        try:
            self._add_chat_bubble(f"Error al enviar: {exc}", is_user=False)
        except Exception:
            pass


_EYE_ON = ("M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27"
           "-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24"
           "-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3"
           " 3-1.34 3-3-1.34-3-3-3z")
_EYE_OFF = ("M12 7c2.76 0 5 2.24 5 5 0 .65-.13 1.26-.36 1.83l2.92 2.92c1.51"
            "-1.26 2.7-2.89 3.43-4.75-1.73-4.39-6-7.5-11-7.5-1.4 0-2.74.25"
            "-3.98.7l2.16 2.16C10.74 7.13 11.35 7 12 7zM2 4.27l2.28 2.28.46"
            ".46C3.08 8.3 1.78 10.02 1 12c1.73 4.39 6 7.5 11 7.5 1.55 0 3.03"
            "-.3 4.38-.84l.42.42L19.73 22 21 20.73 3.27 3 2 4.27zM7.53 9.8l1.55"
            " 1.55c-.05.21-.08.43-.08.65 0 1.66 1.34 3 3 3 .22 0 .44-.03.65-.08"
            "l1.55 1.55c-.67.37-1.43.58-2.2.58-2.76 0-5-2.24-5-5 0-.77.21-1.53"
            ".58-2.2z")


def _chat_svg(path_data, color, size):
    from PySide6.QtSvg import QSvgRenderer
    from PySide6.QtCore import QByteArray
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
           f'<path fill="{color}" d="{path_data}"/></svg>')
    r = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    r.render(p)
    p.end()
    return pm


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
                                   QLinearGradient, QColor)
        from PySide6.QtCore import QRectF
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect().adjusted(0, 0, 0, -7))
        path = QPainterPath()
        path.addRoundedRect(r, 14, 14)
        if self.is_user:
            x = r.right() - 22
            path.moveTo(x, r.bottom() - 4)
            path.lineTo(x + 16, r.bottom() - 6)
            path.lineTo(x + 10, self.height() - 1)
            path.closeSubpath()
            g = QLinearGradient(0, 0, self.width(), self.height())
            g.setColorAt(0, "#8d75ff")
            g.setColorAt(1, "#6d5df0")
            p.fillPath(path, g)
        else:
            x = r.left() + 8
            path.moveTo(x, r.bottom() - 4)
            path.lineTo(x + 14, r.bottom() - 6)
            path.lineTo(x - 4, self.height() - 1)
            path.closeSubpath()
            p.fillPath(path, QColor("#10162a"))
            p.setPen(QColor("#263050"))
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
            b_copy = QPushButton("Copiar")
            b_copy.setIcon(QIcon(make_icon("copy", "#8b949e", 12)))
            b_copy.setStyleSheet(ghost)
            b_copy.setCursor(Qt.CursorShape.PointingHandCursor)
            b_copy.clicked.connect(
                lambda _=False, txt=text: self._copy_chat_text(txt))
            acts.addWidget(b_copy)
            b_add = QPushButton("Agregar a conversi\u00f3n")
            b_add.setIcon(QIcon(make_icon("paste", "#8b949e", 12)))
            b_add.setStyleSheet(ghost)
            b_add.setCursor(Qt.CursorShape.PointingHandCursor)
            b_add.clicked.connect(
                lambda _=False, txt=text: self._add_to_conversion(txt))
            acts.addWidget(b_add)
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
    ad = getattr(self, "adapter", None) or getattr(self, "sapi_adapter", None)
    if ad is not None and len(response or "") <= 500:
        try:
            ad.speak(response)
        except Exception as exc:
            print(f"TTS fallo: {exc}")
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
            sp_png = base / "assets" / "icons" / "chat_bg.png"
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
                cur = target.toPlainText()
                target.setPlainText(
                    (cur.rstrip() + "\n\n" + txt) if cur.strip() else txt)
            else:
                cur = target.text()
                target.setText((cur + " " + txt) if cur.strip() else txt)
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
MainWindow._configure_groq_key = _configure_groq_key
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




def _tts_text(self, text):
    voz = ""
    try:
        voz = self.voice_combo.currentText()
    except Exception:
        pass
    if "multilingual" not in voz.lower():
        return text
    repl = {
        "ña": "nia", "ñe": "nie", "ñi": "niie", "ño": "nio", "ñu": "niu",
        "Ña": "Nia", "Ñe": "Nie", "Ñi": "Niie", "Ño": "Nio", "Ñu": "Niu",
        "ÑA": "NIA", "ÑE": "NIE", "ÑI": "NIIE", "ÑO": "NIO", "ÑU": "NIU",
    }
    out = text
    for k, v in repl.items():
        out = out.replace(k, v)
    import re as _re
    out = _re.sub(r"!+", "!!", out)
    out = _re.sub(r"\?+", "??", out)
    return out


MainWindow._tts_text = _tts_text


def _express_segments(self, text):
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
        if "!" in s or "¡" in s:
            segs.append((a, b, 2))
        elif "?" in s or "¿" in s:
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
        for i in range(self.lang_combo.count()):
            if self.lang_combo.itemText(i).startswith("Todos"):
                self.lang_combo.setCurrentIndex(i)
                break
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

