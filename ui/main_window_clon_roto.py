from __future__ import annotations

import logging
import sys
from pathlib import Path
from urllib.parse import quote

from PySide6.QtCore import Qt, QThread, QTimer, QUrl, Signal, QSize
from PySide6.QtGui import (
    QColor, QDesktopServices, QIcon, QFont, QPainter, QPainterPath,
    QPen, QPixmap, QPolygon,
)
from PySide6.QtWidgets import (
    QSizePolicy,
    QComboBox, QFileDialog, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QMainWindow, QMenu, QMessageBox, QPlainTextEdit,
    QPushButton, QScrollArea, QSlider, QSpinBox, QStackedWidget,
    QVBoxLayout, QWidget,
)

from app.config import load_settings, save_settings
from core import file_reader, license_manager
from core.audio_exporter import AudioExporter
from core.tts_engine import TTSEngine

BG = "#0b0f1a"
SIDE_BG = "#0d1220"
PANEL = "#10162a"
CARD = "#141b30"
CARD2 = "#1a2138"
BORDER = "#232a45"
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

SUBTITLES = [
    "Acento neutro · Profesional",
    "Acento suave · Natural",
    "Acento cálido · Amigable",
    "Acento claro · Formal",
]


def _mdls(char_size):
    return QFont("Segoe MDL2 Assets", char_size)



GLYPH_MAP = {
    "\uE700": "menu", "\uE80F": "home", "\uE81C": "history",
    "\uE720": "mic", "\uEB51": "heart", "\uEB52": "heart_fill",
    "\uE8B7": "folder", "\uE713": "gear", "\uE897": "help",
    "\uE95B": "headset", "\uE768": "play", "\uE71A": "stop",
    "\uE896": "download", "\uE8C8": "copy", "\uE708": "moon",
    "\uE74D": "trash", "\uE77F": "paste", "\uE774": "globe",
    "\uE995": "wave", "\uE71C": "filter", "\uE767": "volume",
}


def make_icon(kind, color, size=20):
    import math
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
    elif kind == "moon":
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(color))
        p.drawEllipse(int(s * 0.18), int(s * 0.18), int(s * 0.64), int(s * 0.64))
        p.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        p.drawEllipse(int(s * 0.38), int(s * 0.1), int(s * 0.55), int(s * 0.55))
    elif kind == "trash":
        p.drawLine(pt(0.25, 0.28), pt(0.75, 0.28))
        p.drawLine(pt(0.42, 0.18), pt(0.58, 0.18))
        p.drawRoundedRect(int(s * 0.3), int(s * 0.28), int(s * 0.4), int(s * 0.55), 3, 3)
    elif kind == "paste":
        p.drawRoundedRect(int(s * 0.24), int(s * 0.2), int(s * 0.52), int(s * 0.65), 3, 3)
        p.drawRect(int(s * 0.4), int(s * 0.12), int(s * 0.2), int(s * 0.14))
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
    else:
        p.setBrush(QColor(color))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(int(s * 0.3), int(s * 0.3), int(s * 0.4), int(s * 0.4))
    p.end()
    return pix


class IconLabel(QLabel):
    def __init__(self, glyph, size=16, color=MUTED, parent=None):
        super().__init__(parent)
        kind = GLYPH_MAP.get(glyph, "dot")
        self.setPixmap(make_icon(kind, color, size + 4))
        self.setStyleSheet("background: transparent;")


class NavButton(QFrame):
    clicked = Signal()

    def __init__(self, glyph, text, parent=None):
        super().__init__(parent)
        self.setFixedHeight(46)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 0, 12, 0)
        lay.setSpacing(12)
        self.icon = IconLabel(glyph, 15, MUTED)
        self.label = QLabel(text)
        lay.addWidget(self.icon)
        lay.addWidget(self.label)
        lay.addStretch()
        self.set_active(False)

    def mouseReleaseEvent(self, event):
        self.clicked.emit()

    def set_active(self, active):
        if active:
            self.setStyleSheet(
                "NavButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                " stop:0 rgba(45,212,191,26), stop:1 rgba(139,92,246,26));"
                f" border: 1px solid {BORDER}; border-radius: 10px; }}"
            )
            self.icon.setStyleSheet(f"color: {TEAL}; background: transparent;")
            self.label.setStyleSheet(
                f"color: {TEXT}; font-size: 13px; font-weight: 600;"
                " background: transparent;"
            )
        else:
            self.setStyleSheet(
                "NavButton { background: transparent; border: 1px solid"
                " transparent; border-radius: 10px; }"
                f"NavButton:hover {{ background: {CARD}; }}"
            )
            self.icon.setStyleSheet(f"color: {MUTED}; background: transparent;")
            self.label.setStyleSheet(
                f"color: {MUTED}; font-size: 13px; background: transparent;"
            )


    def set_collapsed(self, collapsed):
        self.label.setVisible(not collapsed)
        lay = self.layout()
        if collapsed:
            lay.setContentsMargins(24, 0, 24, 0)
        else:
            lay.setContentsMargins(16, 0, 12, 0)


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
            " border-radius: 10px; }"
            f"SquareButton:hover {{ background: {CARD2}; }}"
        )

    def mouseReleaseEvent(self, event):
        self.clicked.emit()


class ActionButton(QFrame):
    clicked = Signal()

    def __init__(self, glyph, text, c1, c2, parent=None):
        super().__init__(parent)
        self.setFixedHeight(48)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(24, 0, 24, 0)
        lay.setSpacing(10)
        self.icon = IconLabel(glyph, 15, "#ffffff")
        self.label = QLabel(text)
        self.label.setStyleSheet(
            "color: white; font-size: 14px; font-weight: 600;"
            " background: transparent;"
        )
        lay.addWidget(self.icon)
        lay.addWidget(self.label)
        self.setStyleSheet(
            "ActionButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f" stop:0 {c1}, stop:1 {c2}); border-radius: 12px; }}"
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
                f" border-bottom: 2px solid {PURPLE}; padding: 8px 14px; }}"
            )
        else:
            self.setStyleSheet(
                f"QPushButton {{ background: transparent; color: {MUTED};"
                " font-size: 13px; border: none; border-bottom: 2px solid"
                " transparent; padding: 8px 14px; }"
                f"QPushButton:hover {{ color: {TEXT}; }}"
            )


class StatsCard(QFrame):
    def __init__(self, glyph, color, title, value, parent=None):
        super().__init__(parent)
        self.setFixedHeight(96)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(18, 0, 18, 0)
        lay.setSpacing(14)
        icon_box = QFrame()
        icon_box.setFixedSize(44, 44)
        icon_box.setStyleSheet(
            "QFrame { background: rgba(45,212,191,18); border-radius: 12px; }"
        )
        ib = QVBoxLayout(icon_box)
        ib.setContentsMargins(0, 0, 0, 0)
        ic = IconLabel(glyph, 17, color)
        ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ib.addWidget(ic)
        texts = QVBoxLayout()
        texts.setSpacing(3)
        t1 = QLabel(title)
        t1.setStyleSheet(
            f"color: {MUTED}; font-size: 12px; background: transparent;"
        )
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(
            f"color: {TEXT}; font-size: 20px; font-weight: 700;"
            " background: transparent;"
        )
        texts.addWidget(t1)
        texts.addWidget(self.value_label)
        lay.addWidget(icon_box)
        lay.addLayout(texts)
        lay.addStretch()
        self.setStyleSheet(
            f"StatsCard {{ background: {CARD}; border: 1px solid {BORDER};"
            " border-radius: 14px; }}"
        )


class VoiceCard(QFrame):
    clicked = Signal()
    fav_toggled = Signal()

    def __init__(self, window, name, premium, selected, favorite, parent=None):
        super().__init__(parent)
        self.window = window
        self.voice_name = name
        self.setFixedHeight(86)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 0, 12, 0)
        lay.setSpacing(12)
        photo = QLabel()
        photo.setFixedSize(48, 48)
        photo.setPixmap(window._avatar_pixmap(name))
        photo.setScaledContents(True)
        photo.setStyleSheet("background: transparent;")
        lay.addWidget(photo)
        texts = QVBoxLayout()
        texts.setSpacing(3)
        n = QLabel(window._display_voice_name(name))
        n.setStyleSheet(
            f"color: {TEXT}; font-size: 13px; font-weight: 600;"
            " background: transparent;"
        )
        s = QLabel(window._voice_subtitle(name, premium))
        s.setStyleSheet(
            f"color: {MUTED}; font-size: 11px; background: transparent;"
        )
        texts.addWidget(n)
        texts.addWidget(s)
        lay.addLayout(texts, 1)
        if premium:
            badge = QLabel("Pro")
            badge.setStyleSheet(
                f"background: {PURPLE}; color: white; border-radius: 6px;"
                " font-size: 10px; font-weight: 700; padding: 3px 7px;"
            )
            lay.addWidget(badge)
        self.heart = QPushButton()
        self.heart.setFixedSize(38, 38)
        self.heart.setIcon(QIcon(make_icon(
            "heart_fill" if favorite else "heart",
            RED if favorite else MUTED, 18)))
        self.heart.setIconSize(QSize(18, 18))
        self.heart.setStyleSheet(
            "QPushButton { background: transparent; border: none;"
            f" color: {RED if favorite else MUTED}; border-radius: 10px; }}"
            "QPushButton:hover { background: #1a2138; }"
        )
        self.heart.clicked.connect(self.fav_toggled.emit)
        lay.addWidget(self.heart)
        self.set_selected(selected)

    def set_selected(self, selected):
        if selected:
            self.setStyleSheet(
                f"VoiceCard {{ background: {CARD2}; border: 1px solid"
                f" {PURPLE}; border-radius: 14px; }}"
            )
        else:
            self.setStyleSheet(
                f"VoiceCard {{ background: {CARD}; border: 1px solid"
                f" {BORDER}; border-radius: 14px; }}"
                f"VoiceCard:hover {{ background: {CARD2}; }}"
            )

    def mouseReleaseEvent(self, event):
        self.clicked.emit()


class ExportWorker(QThread):
    export_ok = Signal(str)
    export_error = Signal(str)
    export_progress = Signal(int)
    MAX_WORKERS = 4

    def __init__(self, exporter, text, path, voice, rate, volume):
        super().__init__()
        self.exporter = exporter
        self.text = text
        self.path = path
        self.voice = voice
        self.rate = rate
        self.volume = volume

    @staticmethod
    def _split_chunks(text, limit=600):
        import re
        sentences = re.split(r"(?<=[.!?])\s+", text)
        chunks = []
        current = ""
        for sentence in sentences:
            if len(sentence) > limit:
                if current:
                    chunks.append(current)
                    current = ""
                for i in range(0, len(sentence), limit):
                    chunks.append(sentence[i:i + limit])
                continue
            if len(current) + len(sentence) + 1 > limit and current:
                chunks.append(current)
                current = sentence
            else:
                current = f"{current} {sentence}".strip()
        if current:
            chunks.append(current)
        return chunks or [text]

    def _synth_chunk(self, chunk, tmp_path):
        import pythoncom
        import win32com.client
        pythoncom.CoInitialize()
        try:
            sapi = win32com.client.Dispatch("SAPI.SpVoice")
            if self.exporter.adapter is not None:
                if self.voice:
                    self.exporter.adapter.set_voice(self.voice)
                try:
                    sapi.Voice = self.exporter.adapter.sapi.Voice
                except Exception:
                    pass
            sapi.Rate = max(-10, min(10, int(self.rate)))
            sapi.Volume = max(0, min(100, int(self.volume)))
            stream = win32com.client.Dispatch("SAPI.SpFileStream")
            stream.Open(tmp_path, 3, False)
            sapi.AudioOutputStream = stream
            sapi.Speak(chunk)
            stream.Close()
            sapi.AudioOutputStream = None
        finally:
            pythoncom.CoUninitialize()

    def run(self):
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import tempfile
        import wave
        try:
            chunks = self._split_chunks(self.text)
            total = len(chunks)
            tmp_paths = []
            futures_idx = {}
            workers = min(self.MAX_WORKERS, total)
            with ThreadPoolExecutor(max_workers=workers) as pool:
                for index, chunk in enumerate(chunks):
                    tmp = tempfile.mktemp(suffix=f"_{index}.wav")
                    tmp_paths.append((index, tmp))
                    fut = pool.submit(self._synth_chunk, chunk, tmp)
                    futures_idx[fut] = (index, tmp)
            done = 0
            for fut in as_completed(futures_idx):
                fut.result()
                done += 1
                self.export_progress.emit(int(done * 100 / total))
            ordered = sorted(tmp_paths, key=lambda x: x[0])
            first = True
            with wave.open(self.path, "wb") as out:
                for _, tmp in ordered:
                    with wave.open(tmp, "rb") as wav_in:
                        if first:
                            out.setnchannels(wav_in.getnchannels())
                            out.setsampwidth(wav_in.getsampwidth())
                            out.setframerate(wav_in.getframerate())
                            first = False
                        out.writeframes(wav_in.readframes(wav_in.getnframes()))
                    Path(tmp).unlink(missing_ok=True)
            self.export_ok.emit(self.path)
        except Exception as exc:
            self.export_error.emit(str(exc))
from PySide6.QtWidgets import QDialog, QProgressDialog
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QRect, QPoint


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
            " transparent; border-radius: 8px; }"
            f"ToolButton:hover {{ background: {CARD2}; }}"
        )

    def mouseReleaseEvent(self, event):
        self.clicked.emit()


class LicenseDialog(QDialog):
    def __init__(self, parent, machine_id, days_left):
        super().__init__(parent)
        self.activated_key = ""
        self.trial_accepted = False
        self.machine_id = machine_id
        self.setWindowTitle("WillpoVoice - Licencia")
        self.setModal(True)
        self.setFixedWidth(430)
        layout = QVBoxLayout(self)
        title = QLabel("WillpoVoice")
        title.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {TEXT};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        info = QLabel(f"ID de esta maquina: {machine_id}")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)
        if days_left >= 0:
            trial = QLabel(f"Prueba gratuita: {days_left} dia(s) restante(s)")
        else:
            trial = QLabel("El periodo de prueba ha terminado.")
        trial.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(trial)
        self.key_edit = QLineEdit()
        self.key_edit.setPlaceholderText("WVP-XXXX-XXXX-XXXX-XXXX")
        layout.addWidget(self.key_edit)
        row = QHBoxLayout()
        activate = QPushButton("Activar")
        activate.clicked.connect(self.try_activate)
        row.addWidget(activate)
        buy = QPushButton("Comprar por WhatsApp")
        buy.clicked.connect(self.open_whatsapp)
        row.addWidget(buy)
        if days_left >= 0:
            trial_btn = QPushButton("Continuar en prueba")
            trial_btn.clicked.connect(self.accept_trial)
            row.addWidget(trial_btn)
        layout.addLayout(row)

    def try_activate(self):
        key = self.key_edit.text()
        if license_manager.validate_key(key, self.machine_id):
            self.activated_key = "".join(key.strip().upper().split())
            self.accept()

    def open_whatsapp(self):
        msg = quote(
            f"Hola, quiero una licencia de WillpoVoice. "
            f"Mi ID de maquina: {self.machine_id}"
        )
        QDesktopServices.openUrl(QUrl(f"https://wa.me/51923073560?text={msg}"))

    def accept_trial(self):
        self.trial_accepted = True
        self.accept()


class MainWindow(QMainWindow):
    MAX_HISTORY = 10

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("naturalvoice_tts.ui")
        self.settings = load_settings()
        self.setWindowTitle("WillpoVoice v1.2.1")
        self.resize(1280, 800)
        self.setMinimumSize(980, 640)
        icon_path = self._resource_path(Path("assets") / "icons" / "icon.ico")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        self.engine = TTSEngine(logger=self.logger)
        self.exporter = AudioExporter(adapter=self.engine.adapter, logger=self.logger)
        self.export_worker = None
        self._voices = []
        self._selected_voice = ""
        self._rtab = "todas"
        self._seconds = 0
        self._build_ui()
        self.setStyleSheet(self._global_qss())
        self._connect_signals()
        self._load_voices()
        self._load_history()

    @staticmethod
    def _resource_path(rel):
        base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
        return base / rel

    def _global_qss(self):
        return f"""
QMainWindow, QWidget {{ background: {BG}; color: {TEXT};
font-family: "Segoe UI"; font-size: 13px; }}
QPlainTextEdit {{ background: #0d1424; color: {TEXT}; border: 1px solid {BORDER};
border-radius: 12px; padding: 12px; font-size: 14px; }}
QComboBox {{ background: {CARD}; color: {TEXT}; border: 1px solid {BORDER};
border-radius: 10px; padding: 8px 12px; min-height: 30px; }}
QComboBox QAbstractItemView {{ background: {CARD}; color: {TEXT};
selection-background-color: {CARD2}; border: 1px solid {BORDER}; }}
QSlider::groove:horizontal {{ background: #1a2138; height: 6px; border-radius: 3px; }}
QSlider::sub-page:horizontal {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
stop:0 {BLUE}, stop:1 {TEAL}); border-radius: 3px; }}
QSlider::handle:horizontal {{ background: {BLUE}; width: 14px; height: 14px;
margin: -4px 0; border-radius: 7px; }}
QListWidget {{ background: transparent; border: none; outline: none; }}
QListWidget::item {{ background: {CARD}; border: 1px solid {BORDER};
border-radius: 10px; padding: 10px; margin: 4px; }}
QListWidget::item:selected {{ background: {CARD2}; border: 1px solid {PURPLE}; }}
QSpinBox {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 8px;
padding: 6px; color: {TEXT}; }}
QMenu {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 10px; padding: 6px; }}
QMenu::item {{ padding: 8px 20px; border-radius: 8px; }}
QMenu::item:selected {{ background: {CARD2}; }}
QScrollBar:vertical {{ background: transparent; width: 8px; }}
QScrollBar::handle:vertical {{ background: {BORDER}; border-radius: 4px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QStatusBar {{ background: {BG}; color: {MUTED}; }}
"""

    def _avatar_pixmap(self, name):
        low = name.lower()
        fname = None
        for key, f in PREMIUM_PHOTOS.items():
            if key in low:
                fname = f
                break
        size = 48
        if fname is None:
            first = name.replace("Microsoft ", "").split(" ")[0].strip().lower()
            female_extra = {"carmen", "belen", "mercedes", "flor", "noor", "mar",
                            "soledad", "paz", "nieves"}
            male_extra = {"joshua", "luca", "elias", "noah", "jonah"}
            if first in female_extra:
                female = True
            elif first in male_extra:
                female = False
            else:
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
                sc = src.scaled(size, size,
                                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                Qt.TransformationMode.SmoothTransformation)
                x = (sc.width() - size) // 2
                y = (sc.height() - size) // 2
                p.drawPixmap(0, 0, sc, x, y, size, size)
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
        p.drawText(QRect(0, 0, size, size), Qt.AlignmentFlag.AlignCenter,
                   name[:1].upper())
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
        if premium:
            return SUBTITLES[len(name) % len(SUBTITLES)]
        return "Voz estándar"

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ---------- SIDEBAR ----------
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(232)
        self.sidebar.setStyleSheet(
            f"QFrame {{ background: {SIDE_BG}; border: none; }}"
        )
        sb = QVBoxLayout(self.sidebar)
        sb.setContentsMargins(14, 14, 14, 14)
        sb.setSpacing(4)
        self.hamburger = SquareButton("\uE700", "Menu")
        sb.addWidget(self.hamburger, 0, Qt.AlignmentFlag.AlignLeft)
        sb.addSpacing(10)
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
            f"color: {TEXT}; font-size: 15px; font-weight: 700;"
            " background: transparent;"
        )
        self._logo_ver = QLabel("v1.2.1")
        self._logo_ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._logo_ver.setStyleSheet(
            f"color: {MUTED}; font-size: 10px; background: transparent;"
        )
        sb.addWidget(logo)
        sb.addWidget(self._logo_name)
        sb.addWidget(self._logo_ver)
        sb.addSpacing(16)
        self._nav = []
        for glyph, text, page in (
            ("\uE80F", "Inicio", 0), ("\uE81C", "Historial", 1),
            ("\uE720", "Voces", 2), ("\uEB51", "Favoritos", 3),
            ("\uE8B7", "Proyectos", 4), ("\uE713", "Ajustes", 5),
        ):
            btn = NavButton(glyph, text)
            btn.clicked.connect(lambda _=False, p=page: self._switch_page(p))
            sb.addWidget(btn)
            self._nav.append((btn, page))
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {BORDER};")
        sb.addWidget(sep)
        sb.addSpacing(4)
        for glyph, text, fn in (
            ("\uE897", "Ayuda", self.show_help),
            ("\uE95B", "Soporte", self.open_support),
        ):
            btn = NavButton(glyph, text)
            btn.clicked.connect(lambda _=False, f=fn: f())
            sb.addWidget(btn)
        sb.addStretch()
        prem = QFrame()
        prem.setStyleSheet(
            "QFrame { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            " stop:0 #241a3d, stop:1 #3b2a63); border-radius: 14px; }"
        )
        pl = QVBoxLayout(prem)
        pl.setContentsMargins(14, 14, 14, 14)
        pt = QLabel("👑  WillpoVoice Premium")
        pt.setStyleSheet(
            f"color: {TEXT}; font-size: 12px; font-weight: 700;"
            " background: transparent;"
        )
        pd = QLabel("Desbloquea todas las voces y funciones premium.")
        pd.setWordWrap(True)
        pd.setStyleSheet(
            f"color: {MUTED}; font-size: 10px; background: transparent;"
        )
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
        self._prem_card = prem
        sb.addWidget(prem)
        root.addWidget(self.sidebar)

        # ---------- CENTRO + DERECHA ----------
        self.pages = QStackedWidget()
        root.addWidget(self.pages, 1)

        # ----- Pagina Inicio -----
        page0 = QWidget()
        p0 = QVBoxLayout(page0)
        p0.setContentsMargins(20, 16, 20, 16)
        p0.setSpacing(14)

        header = QFrame()
        header.setFixedHeight(190)
        header.setStyleSheet(f"QFrame {{ background: {CARD}; border-radius: 16px; }}")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(0, 0, 0, 0)
        cover = QLabel()
        cp = self._resource_path(Path("assets") / "icons" / "portada.png")
        if not cp.exists():
            frames_dir = self._resource_path(
                Path("assets") / "icons" / "portada_frames")
            if frames_dir.exists():
                files = sorted(frames_dir.glob("*.jpg")) or sorted(
                    frames_dir.glob("*.png"))
                if files:
                    cp = files[len(files) // 2]
        if cp.exists():
            pm = QPixmap(str(cp)).scaled(
                900, 190, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation)
            cover.setPixmap(pm)
        cover.setStyleSheet("background: transparent; border-radius: 16px;")
        cover.setScaledContents(True)
        cover.setMinimumWidth(0)
        cover.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        hl.addWidget(cover)
        titles = QVBoxLayout()
        titles.setContentsMargins(24, 0, 0, 0)
        t1 = QLabel("WillpoVoice")
        t1.setStyleSheet(f"color: white; font-size: 26px; font-weight: 700; background: transparent;")
        t2 = QLabel("Convierte texto en voz con voces naturales")
        t2.setStyleSheet(f"color: #cdd5ea; font-size: 12px; background: transparent;")
        titles.addWidget(t1)
        titles.addWidget(t2)
        titles.addStretch()
        hl.addLayout(titles, 1)
        p0.addWidget(header)

        stats = QHBoxLayout()
        stats.setSpacing(14)
        self.stat_voices = StatsCard("\uE720", TEAL, "Voces disponibles", "0")
        self.stat_langs = StatsCard("\uE774", BLUE, "Idiomas", "29")
        self.stat_conv = StatsCard("\uE995", TEAL, "Conversiones hoy",
                                   str(self.settings.get("conv_today", 0)))
        for s in (self.stat_voices, self.stat_langs, self.stat_conv):
            stats.addWidget(s)
        p0.addLayout(stats)

        card = QFrame()
        card.setStyleSheet(f"QFrame {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 16px; }}")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(18, 14, 18, 16)
        cl.setSpacing(12)
        top = QHBoxLayout()
        self.tab_text = TabButton("Texto manual")
        self.tab_file = TabButton("Importar archivo")
        self.tab_text.set_active(True)
        top.addWidget(self.tab_text)
        top.addWidget(self.tab_file)
        top.addStretch()
        self.btn_clear = ToolButton("\uE74D", "Limpiar")
        self.btn_paste = ToolButton("\uE77F", "Pegar")
        top.addWidget(self.btn_clear)
        top.addWidget(self.btn_paste)
        cl.addLayout(top)

        self.text_edit = QPlainTextEdit()
        self.text_edit.setPlaceholderText(
            "Escribe aquí el texto que quieres convertir a voz...")
        self.text_edit.setFixedHeight(150)
        self.text_edit.setMinimumWidth(150)
        cl.addWidget(self.text_edit)
        self.counter_label = QLabel("0 / 5000")
        self.counter_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.counter_label.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
        cl.addWidget(self.counter_label)

        sel = QHBoxLayout()
        sel.setSpacing(14)
        l1 = QLabel("Idioma")
        l1.setStyleSheet(f"color: {MUTED}; font-size: 12px;")
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["Español (España)", "Inglés (EEUU)", "Todos"])
        self.lang_combo.setMinimumWidth(120)
        self.voice_combo.setMinimumWidth(160)
        self.lang_combo.setItemIcon(0, QIcon(self._flag_pixmap("es")))
        self.lang_combo.setItemIcon(1, QIcon(self._flag_pixmap("us")))
        self.lang_combo.setItemIcon(2, QIcon(self._flag_pixmap("world")))
        l2 = QLabel("Voz seleccionada")
        l2.setStyleSheet(f"color: {MUTED}; font-size: 12px;")
        self.voice_combo = QComboBox()
        sel.addWidget(l1)
        sel.addWidget(self.lang_combo, 1)
        sel.addSpacing(10)
        sel.addWidget(l2)
        sel.addWidget(self.voice_combo, 1)
        cl.addLayout(sel)

        self.adv_button = QPushButton("＞  Opciones avanzadas")
        self.adv_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.adv_button.setStyleSheet(
            f"QPushButton {{ background: {CARD2}; color: {TEXT}; border: 1px solid"
            f" {BORDER}; border-radius: 10px; padding: 8px 14px; text-align: left; }}"
        )
        cl.addWidget(self.adv_button)
        self.adv_widget = QWidget()
        al = QHBoxLayout(self.adv_widget)
        al.setContentsMargins(0, 4, 0, 4)
        al.addWidget(QLabel("Velocidad"))
        self.rate_slider = QSlider(Qt.Orientation.Horizontal)
        self.rate_slider.setRange(-10, 10)
        al.addWidget(self.rate_slider, 1)
        al.addSpacing(16)
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
        self.speak_button = ActionButton("\uE768", "Reproducir", BLUE, "#1d4ed8")
        self.stop_button = ActionButton("\uE71A", "Detener", MAGENTA, PURPLE)
        self.export_button = ActionButton("\uE896", "Exportar", TEAL, "#0d9488")
        self.copy_button = SquareButton("\uE8C8", "Copiar texto")
        self.open_button = SquareButton("\uE8B7", "Abrir archivo")
        self.theme_button = SquareButton("\uE708", "Tema")
        acts.addWidget(self.speak_button)
        acts.addWidget(self.stop_button)
        acts.addWidget(self.export_button)
        acts.addStretch()
        acts.addWidget(self.copy_button)
        acts.addWidget(self.open_button)
        acts.addWidget(self.theme_button)
        p0.addLayout(acts)
        self._add_neon(self.speak_button, BLUE)
        self._add_neon(self.stop_button, MAGENTA)
        self._add_neon(self.export_button, TEAL)

        player = QFrame()
        player.setFixedHeight(64)
        player.setStyleSheet(f"QFrame {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 14px; }}")
        yl = QHBoxLayout(player)
        yl.setContentsMargins(12, 0, 14, 0)
        yl.setSpacing(10)
        self.player_play = SquareButton("\uE768", "Reproducir")
        self.player_play.setFixedSize(40, 40)
        self.time_cur = QLabel("0:00")
        self.time_cur.setStyleSheet(f"color: {MUTED};")
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setRange(0, 100)
        self.time_tot = QLabel("0:00")
        self.time_tot.setStyleSheet(f"color: {MUTED};")
        vol_icon = IconLabel("\uE767", 14, MUTED)
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

        # ----- Pagina Historial -----
        page1 = QWidget()
        h1 = QVBoxLayout(page1)
        h1.setContentsMargins(20, 16, 20, 16)
        ht = QLabel("Historial")
        ht.setStyleSheet(f"color: {TEXT}; font-size: 20px; font-weight: 700;")
        self.history_list = QListWidget()
        self.btn_clear_hist = QPushButton("Limpiar historial")
        self.btn_clear_hist.setStyleSheet(
            f"QPushButton {{ background: {CARD}; color: {TEXT}; border: 1px solid"
            f" {BORDER}; border-radius: 10px; padding: 8px 16px; }}"
        )
        h1.addWidget(ht)
        h1.addWidget(self.history_list, 1)
        h1.addWidget(self.btn_clear_hist, 0, Qt.AlignmentFlag.AlignLeft)
        self.pages.addWidget(page1)

        # ----- Pagina Voces -----
        page2 = QWidget()
        v2 = QVBoxLayout(page2)
        v2.setContentsMargins(20, 16, 20, 16)
        vt = QLabel("Voces")
        vt.setStyleSheet(f"color: {TEXT}; font-size: 20px; font-weight: 700;")
        self.all_scroll = QScrollArea()
        self.all_scroll.setWidgetResizable(True)
        self.all_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.all_container = QWidget()
        self.all_layout = QVBoxLayout(self.all_container)
        self.all_layout.setContentsMargins(0, 0, 8, 0)
        self.all_layout.setSpacing(10)
        self.all_scroll.setWidget(self.all_container)
        v2.addWidget(vt)
        v2.addWidget(self.all_scroll, 1)
        self.pages.addWidget(page2)

        # ----- Pagina Favoritos -----
        page3 = QWidget()
        f3 = QVBoxLayout(page3)
        f3.setContentsMargins(20, 16, 20, 16)
        ft = QLabel("Favoritos")
        ft.setStyleSheet(f"color: {TEXT}; font-size: 20px; font-weight: 700;")
        self.fav_scroll = QScrollArea()
        self.fav_scroll.setWidgetResizable(True)
        self.fav_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.fav_container = QWidget()
        self.fav_layout = QVBoxLayout(self.fav_container)
        self.fav_layout.setContentsMargins(0, 0, 8, 0)
        self.fav_layout.setSpacing(10)
        self.fav_scroll.setWidget(self.fav_container)
        f3.addWidget(ft)
        f3.addWidget(self.fav_scroll, 1)
        self.pages.addWidget(page3)

        # ----- Pagina Proyectos -----
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

        # ----- Pagina Ajustes -----
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
        self.right_panel.setStyleSheet(
            f"QFrame {{ background: {BG}; border-left: 1px solid {BORDER}; }}"
        )
        self.right_panel.setMinimumWidth(240)
        self.right_panel.setMaximumWidth(340)
        rp = QVBoxLayout(self.right_panel)
        rp.setContentsMargins(14, 14, 14, 14)
        rp.setSpacing(10)
        rh = QHBoxLayout()
        rt = QLabel("Voces recomendadas")
        rt.setStyleSheet(
            f"color: {TEXT}; font-size: 14px; font-weight: 700;"
        )
        self.btn_ver_all = ToolButton("", "Ver todas")
        rh.addWidget(rt)
        rh.addStretch()
        rh.addWidget(self.btn_ver_all)
        rp.addLayout(rh)
        search_row = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Buscar voces...")
        self.search_edit.setStyleSheet(
            f"QLineEdit {{ background: {CARD}; border: 1px solid {BORDER};"
            " border-radius: 10px; padding: 8px 12px; }"
        )
        self.filter_btn = SquareButton("\uE71C", "Filtro")
        search_row.addWidget(self.search_edit, 1)
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
        self.cards_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.cards_scroll.setStyleSheet(
            "QScrollArea { background: transparent; border: none; }"
        )
        self.cards_container = QWidget()
        self.cards_container.setStyleSheet("background: transparent;")
        self.voice_cards_layout = QVBoxLayout(self.cards_container)
        self.voice_cards_layout.setContentsMargins(0, 0, 4, 0)
        self.voice_cards_layout.setSpacing(8)
        self.cards_scroll.setWidget(self.cards_container)
        rp.addWidget(self.cards_scroll, 1)
        root.addWidget(self.right_panel)

        self.player_timer = QTimer(self)
        self.player_timer.timeout.connect(self._tick_player)
        self._switch_page(0)

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

    def _add_neon(self, widget, color):
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
        eff = QGraphicsDropShadowEffect(widget)
        eff.setBlurRadius(18)
        eff.setOffset(0, 0)
        eff.setColor(QColor(color))
        widget.setGraphicsEffect(eff)

    def _connect_signals(self):
        self.speak_button.clicked.connect(self.speak_text)
        self.player_play.clicked.connect(self.speak_text)
        self.stop_button.clicked.connect(self.stop_speech)
        self.export_button.clicked.connect(self._show_export_menu)
        self.copy_button.clicked.connect(self._copy_text)
        self.open_button.clicked.connect(self._open_document_dialog)
        self.theme_button.clicked.connect(self._toggle_theme_msg)
        self.btn_clear.clicked.connect(lambda: self.text_edit.clear())
        self.btn_paste.clicked.connect(
            lambda: self.text_edit.paste())
        self.btn_clear_hist.clicked.connect(self.clear_history)
        self.text_edit.textChanged.connect(self.update_counter)
        self.voice_combo.currentTextChanged.connect(self._on_combo_voice)
        self.search_edit.textChanged.connect(lambda _t: self._rebuild_cards())
        self.rtab_all.clicked.connect(lambda: self._set_rtab("todas"))
        self.rtab_pro.clicked.connect(lambda: self._set_rtab("premium"))
        self.rtab_fav.clicked.connect(lambda: self._set_rtab("favoritas"))
        self.btn_ver_all.clicked.connect(lambda: self._switch_page(2))
        self.adv_button.clicked.connect(self._toggle_adv)
        self.hamburger.clicked.connect(self._toggle_sidebar)
        self.history_list.itemClicked.connect(self._on_history_click)
        self.limit_spin.valueChanged.connect(
            lambda v: self.settings.__setitem__("char_limit", v))
        self.vol_slider.valueChanged.connect(
            lambda v: self.engine.set_volume(v))
        self.volume_slider.valueChanged.connect(
            lambda v: self.engine.set_volume(v))

    def _toggle_sidebar(self):
        collapsed = self.sidebar.width() > 100
        self.sidebar.setFixedWidth(68 if collapsed else 232)
        for btn, _page in self._nav:
            btn.set_collapsed(collapsed)
        self._logo_name.setVisible(not collapsed)
        self._logo_ver.setVisible(not collapsed)
        self._prem_card.setVisible(not collapsed)

    def _switch_page(self, index):
        self.pages.setCurrentIndex(index)
        for i, (btn, _page) in enumerate(self._nav):
            btn.set_active(i == index)
        self.right_panel.setVisible(index == 0)

    def _set_rtab(self, tab):
        self._rtab = tab
        self.rtab_all.set_active(tab == "todas")
        self.rtab_pro.set_active(tab == "premium")
        self.rtab_fav.set_active(tab == "favoritas")
        self._rebuild_cards()

    def _toggle_adv(self):
        show = not self.adv_widget.isVisible()
        self.adv_widget.setVisible(show)
        self.adv_button.setText(
            "＞  Opciones avanzadas" if not show else "＜  Opciones avanzadas")

    def _load_voices(self):
        try:
            self.engine.refresh_voices()
            voices = self.engine.get_available_voices()
            voices.sort(key=lambda n: (not self._is_premium(n), n.lower()))
            self._voices = voices
            self.voice_combo.clear()
            for v in voices:
                self.voice_combo.addItem(self._display_voice_name(v))
                idx = self.voice_combo.count() - 1
                self.voice_combo.setItemData(
                    idx, v, Qt.ItemDataRole.UserRole)
                self.voice_combo.setItemIcon(
                    idx, QIcon(self._avatar_pixmap(v)))
            last = self.settings.get("last_voice", "")
            if last in voices:
                self._select_voice(last)
            elif voices:
                pref = next((v for v in voices if "SeraphinaMultilingual" in v),
                            voices[0])
                self._select_voice(pref)
            self.stat_voices.value_label.setText(f"{len(voices)}+")
            self._rebuild_cards()
            self._rebuild_all_page()
            self._rebuild_fav_page()
        except Exception as exc:
            self.logger.exception("Error cargando voces.")
            QMessageBox.critical(self, "Error",
                                 f"No se pudieron cargar las voces: {exc}")

    def _favorites(self):
        return set(self.settings.get("favorites", []))

    def _rebuild_cards(self):
        layout = self.voice_cards_layout
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget() if item else None
            if w is not None:
                w.deleteLater()
        q = self.search_edit.text().strip().lower()
        favs = self._favorites()
        for name in self._voices:
            premium = self._is_premium(name)
            if self._rtab == "premium" and not premium:
                continue
            if self._rtab == "favoritas" and name not in favs:
                continue
            if q and q not in name.lower():
                continue
            card = VoiceCard(self, name, premium,
                             name == self._selected_voice, name in favs)
            card.clicked.connect(lambda n=name: self._select_voice(n))
            card.fav_toggled.connect(lambda n=name: self._toggle_fav(n))
            layout.addWidget(card)
        layout.addStretch()

    def _rebuild_all_page(self):
        layout = self.all_layout
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget() if item else None
            if w is not None:
                w.deleteLater()
        favs = self._favorites()
        for name in self._voices:
            premium = self._is_premium(name)
            card = VoiceCard(self, name, premium,
                             name == self._selected_voice, name in favs)
            card.clicked.connect(lambda n=name: self._select_voice(n))
            card.fav_toggled.connect(lambda n=name: self._toggle_fav(n))
            layout.addWidget(card)
        layout.addStretch()

    def _rebuild_fav_page(self):
        layout = self.fav_layout
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget() if item else None
            if w is not None:
                w.deleteLater()
        favs = self._favorites()
        for name in self._voices:
            if name not in favs:
                continue
            card = VoiceCard(self, name, self._is_premium(name), True, True)
            card.clicked.connect(lambda n=name: self._select_voice(n))
            card.fav_toggled.connect(lambda n=name: self._toggle_fav(n))
            layout.addWidget(card)
        layout.addStretch()

    def _current_voice(self):
        data = self.voice_combo.currentData(Qt.ItemDataRole.UserRole)
        return data or self.voice_combo.currentText()

    def _select_voice(self, name):
        self._selected_voice = name
        for i in range(self.voice_combo.count()):
            if self.voice_combo.itemData(
                    i, Qt.ItemDataRole.UserRole) == name:
                self.voice_combo.blockSignals(True)
                self.voice_combo.setCurrentIndex(i)
                self.voice_combo.blockSignals(False)
                break
        try:
            self.engine.select_voice(name)
        except Exception:
            pass
        self._rebuild_cards()
        self._rebuild_all_page()
        self._rebuild_fav_page()
        self.statusBar().showMessage(f"Voz seleccionada: {name}")

    def _on_combo_voice(self, name):
        voice = self._current_voice()
        if voice:
            self._select_voice(voice)

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
        QGuiApplication.clipboard().setText(self.text_edit.toPlainText())
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

    def _toggle_theme_msg(self):
        self.statusBar().showMessage("Tema claro: próximamente.")

    def _fmt_time(self, s):
        m = int(s // 60)
        ss = int(s % 60)
        return f"{m}:{ss:02d}"

    def _tick_player(self):
        self._seconds += 0.5
        self.time_cur.setText(self._fmt_time(self._seconds))
        self.progress_slider.setValue(int(self._seconds * 4) % 100)
        try:
            state = self.engine.adapter.sapi.Status.RunningState
        except Exception:
            state = 1
        if state != 2 and self._seconds > 2:
            self.player_timer.stop()
            self._seconds = 0
            self.time_cur.setText("0:00")
            self.progress_slider.setValue(0)

    def speak_text(self):
        try:
            text = self.text_edit.toPlainText().strip()
            if not text:
                self.statusBar().showMessage("Escribe un texto antes de reproducir.")
                return
            voice = self._current_voice()
            if voice:
                self.engine.select_voice(voice)
            self.engine.set_rate(self.rate_slider.value())
            self.engine.set_volume(self.volume_slider.value())
            self.engine.speak_async(text)
            self._add_to_history(text)
            self.settings["conv_today"] = int(self.settings.get("conv_today", 0)) + 1
            self.stat_conv.value_label.setText(str(self.settings["conv_today"]))
            self._seconds = 0
            self.player_timer.start(500)
            self.statusBar().showMessage("Reproduciendo...")
        except Exception as exc:
            self.logger.exception("Error al reproducir.")
            QMessageBox.warning(self, "Error", f"No se pudo reproducir: {exc}")

    def stop_speech(self):
        try:
            self.engine.stop()
            self.player_timer.stop()
            self._seconds = 0
            self.time_cur.setText("0:00")
            self.progress_slider.setValue(0)
            self.statusBar().showMessage("Reproducción detenida.")
        except Exception as exc:
            QMessageBox.warning(self, "Error", f"No se pudo detener: {exc}")

    def _show_export_menu(self):
        menu = QMenu(self)
        wav = menu.addAction("Audio WAV  (.wav, sin compresion)")
        mp3 = menu.addAction("Audio MP3  (.mp3, comprimido)")
        action = menu.exec(QGuiApplication.cursorPos())
        if action == wav:
            self.export_wav()
        elif action == mp3:
            self.export_mp3()

    def _start_export_progress(self):
        dialog = QProgressDialog("Exportando audio...", None, 0, 100, self)
        dialog.setWindowTitle("Exportando")
        dialog.setModal(True)
        dialog.setCancelButton(None)
        dialog.show()
        self.export_progress = dialog

    def _on_export_progress(self, value):
        prog = getattr(self, "export_progress", None)
        if prog is not None:
            prog.setValue(value)

    def _finish_export_progress(self):
        prog = getattr(self, "export_progress", None)
        if prog is not None:
            prog.close()
        self.export_progress = None

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
        voice = self._current_voice()
        self.statusBar().showMessage("Exportando audio...")
        self._start_export_progress()
        self.export_worker = ExportWorker(
            exporter=self.exporter, text=text, path=path, voice=voice,
            rate=self.rate_slider.value(), volume=self.volume_slider.value())
        self.export_worker.export_ok.connect(self.on_export_ok)
        self.export_worker.export_progress.connect(self._on_export_progress)
        self.export_worker.export_error.connect(self.on_export_error)
        self.export_worker.start()

    def on_export_ok(self, path):
        self._finish_export_progress()
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
                QMessageBox.warning(self, "Error", f"No se pudo convertir a MP3: {exc}")
                return
        self.statusBar().showMessage(f"Audio guardado en: {final_path}")
        QMessageBox.information(self, "Exportación exitosa",
                                f"El audio se guardó en: {final_path}")

    def on_export_error(self, message):
        self._finish_export_progress()
        QMessageBox.warning(self, "Error", f"No se pudo exportar el audio: {message}")

    def _load_history(self):
        self.history_list.clear()
        self._history_full = []
        for it in self.settings.get("history", []):
            entry = it if isinstance(it, dict) else {
                "content": it, "label": "Texto manual"}
            self._history_full.append(entry)
            self.history_list.addItem(entry.get("label", "Sin titulo"))

    def _on_history_click(self, item):
        idx = self.history_list.row(item)
        if 0 <= idx < len(self._history_full):
            self.text_edit.setPlainText(
                self._history_full[idx].get("content", ""))
            self._switch_page(0)

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

    def clear_history(self):
        self.settings["history"] = []
        self._load_history()
        self.statusBar().showMessage("Historial limpiado.")

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
        dialog = LicenseDialog(self, license_manager.get_machine_id(),
                               days_left if state == "trial" else -1)
        dialog.exec()
        if dialog.activated_key:
            data = license_manager.load_data()
            data["license_key"] = dialog.activated_key
            license_manager.save_data(data)
            self.license_label.setText("Version licenciada.")
            return True
        return dialog.trial_accepted

    def showEvent(self, event):
        super().showEvent(event)
        if not getattr(self, "_license_checked", False):
            self._license_checked = True
            if not self._check_license():
                self.close()

    def closeEvent(self, event):
        try:
            self.settings["last_voice"] = self._current_voice()
            save_settings(self.settings)
            self.engine.stop()
        except Exception:
            self.logger.exception("Error al cerrar.")
        event.accept()
