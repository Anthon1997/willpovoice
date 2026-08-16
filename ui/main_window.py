from __future__ import annotations

import logging
import sys
from urllib.parse import quote
from pathlib import Path

from PySide6.QtCore import QEvent, Qt, QThread, QTimer, QUrl, Signal, QSize
from PySide6.QtGui import QBrush, QColor, QCursor, QDesktopServices, QIcon, QFont, QLinearGradient, QMovie, QImageReader, QPainter, QPainterPath, QPen, QPixmap, QPolygon, QTransform
from PySide6.QtCore import QPoint, QRect, QRectF, QSize
from PySide6.QtWidgets import (
    QComboBox,
    QColorDialog,
    QDialog,
QDockWidget,
    QFileDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
QScrollArea,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QProgressDialog,
    QPushButton,
    QGraphicsDropShadowEffect,
    QSlider,
QSizePolicy,
    QStyledItemDelegate,
    QToolButton,
    QVBoxLayout,
    QWidgetAction,
    QWidget,
)

from app.config import load_settings, save_settings
from core.audio_exporter import AudioExporter
from core.tts_engine import TTSEngine
from ui.theme import PRESET_COLORS, build_qss


class ShineProgressBar(QProgressBar):
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
        painter.fillPath(bg, QColor("#1a2236"))

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
            grad.setColorAt(0, QColor("#4a7dff"))
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

        sentences = re.split(r"(?<=[.!?...])\s+", text)
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
            from core.text_normalizer import normalize_for_tts
            chunks = self._split_chunks(normalize_for_tts(self.text))
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


class SpeakingDialog(QDialog):
    def __init__(self, parent, engine):
        super().__init__(parent)
        self.engine = engine
        self.setWindowTitle("Reproduciendo")
        self.setModal(False)
        self.setFixedWidth(260)
        self.has_started = False
        self.ticks_without_speech = 0

        layout = QVBoxLayout(self)

        self.gif_label = QLabel()
        gif_path = MainWindow._resource_path(Path("assets") / "icons" / "spectrum.gif")

        if not gif_path.exists():
            gif_path = MainWindow._resource_path(Path("assets") / "icons" / "palette.gif")

        if gif_path.exists():
            self.movie = QMovie(str(gif_path))
            self.movie.setScaledSize(QSize(132, 64))
            self.gif_label.setMovie(self.movie)
            self.movie.start()

        self.gif_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.gif_label)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(8)
        layout.addWidget(self.progress)

        self.info_label = QLabel("Preparando voz...")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)

        self.stop_button = QPushButton("Detener")
        self.stop_button.clicked.connect(self.stop_and_close)
        layout.addWidget(self.stop_button)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_state)
        self.timer.start(300)

    def check_state(self):
        try:
            state = self.engine.adapter.sapi.Status.RunningState
        except Exception:
            state = 1

        if state == 2:
            if not self.has_started:
                self.has_started = True
                self.info_label.setText("Reproduciendo texto...")
                self.progress.hide()
        elif state == 1 and self.has_started:
            self.timer.stop()
            self.close()
        else:
            if not self.has_started:
                self.ticks_without_speech += 1
                self.progress.setValue(
                    min(95, self.ticks_without_speech * 4)
                )

                if self.ticks_without_speech >= 50:
                    self.info_label.setText("No se pudo iniciar la voz.")
                    self.progress.hide()
                    self.timer.stop()
                    QTimer.singleShot(1500, self.close)

    def stop_and_close(self):
        try:
            self.engine.stop()
        except Exception:
            pass

        self.timer.stop()
        self.close()


class SpotlightOverlay(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.target_rect = None

    def set_target(self, widget):
        if widget is None:
            self.target_rect = None
        else:
            top_left = widget.mapToGlobal(QPoint(0, 0))
            overlay_top_left = self.mapToGlobal(QPoint(0, 0))
            x = top_left.x() - overlay_top_left.x()
            y = top_left.y() - overlay_top_left.y()
            self.target_rect = QRect(
                x - 6, y - 6, widget.width() + 12, widget.height() + 12
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


class HelpWizard(QDialog):
    STEPS = [
        ("Bienvenido a WillpoVoice", "Esta guia te enseña paso a paso como convertir texto en voz con las voces disponibles."),
        ("1. Elige una voz", "En el desplegable superior selecciona la voz que quieras: las MULTILINGUAL hablan cualquier idioma de manera fluida."),
        ("2. Escribe tu texto", "En el cuadro central escribe o pega el texto que quieres escuchar. Tambien puedes pulsar 'Abrir TXT' para cargar un archivo de texto completo."),
        ("3. Ajusta velocidad y volumen", "Con las barras inferiores controlas que tan rapido habla la voz y que tan fuerte suena."),
        ("4. Pulsa Reproducir", "Se reproducira de manera secuencial el resultado."),
        ("5. Detener", "Si quieres interrumpir la reproduccion, pulsa el boton Detener de la barra inferior o el de la ventana emergente."),
        ("6. Exportar", "Pulsa 'Exportar' para guardar el audio de tu texto en un archivo WAV y usarlo donde quieras."),
        ("7. Historial y personalizacion", "Tus ultimos textos quedan guardados en el Historial. Con la paleta de colores y 'Modo claro' personalizas la apariencia a tu gusto."),
        ("8. Soporte y ayuda", "El boton verde Soporte te conecta por WhatsApp. Y este boton '? Ayuda' te vuelve a mostrar esta guia cuando lo necesites."),
    ]

    def __init__(self, parent=None, targets=None, overlay=None):
        super().__init__(parent)
        self.step = 0
        self.targets = targets or []
        self.overlay = overlay
        self.setWindowTitle("Ayuda de WillpoVoice")
        self.setModal(True)
        self.setFixedWidth(380)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)

        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 15px; font-weight: 700;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        self.text_label = QLabel()
        self.text_label.setWordWrap(True)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.text_label)

        self.progress_label = QLabel()
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.progress_label)

        row = QHBoxLayout()
        self.prev_button = QPushButton("<- Anterior")
        self.prev_button.clicked.connect(self.prev_step)
        row.addWidget(self.prev_button)

        self.next_button = QPushButton("Siguiente ->")
        self.next_button.clicked.connect(self.next_step)
        row.addWidget(self.next_button)
        layout.addLayout(row)

        self.show_step()

    def show_step(self):
        title, body = self.STEPS[self.step]
        self.title_label.setText(title)
        self.text_label.setText(body)
        self.progress_label.setText(
            f"Paso {self.step + 1} de {len(self.STEPS)}"
        )
        self.prev_button.setEnabled(self.step > 0)

        if self.step == len(self.STEPS) - 1:
            self.next_button.setText("Finalizar")
        else:
            self.next_button.setText("Siguiente ->")

        self._position_near_target()

    def _position_near_target(self):
        parent = self.parent()

        if parent is None:
            return

        attr = None

        if self.targets and self.step < len(self.targets):
            attr = self.targets[self.step]

        if self.overlay:
            self.overlay.set_target(
                None if attr is None else getattr(parent, attr, None)
            )

        if attr is None:
            frame = parent.frameGeometry()
            self.move(
                frame.center().x() - self.width() // 2,
                frame.center().y() - self.height() // 2,
            )
            return

        target = getattr(parent, attr, None)

        if target is None:
            return

        pg = parent.frameGeometry()
        top_left = target.mapToGlobal(QPoint(0, 0))

        center_x = top_left.x() + target.width() // 2
        x = center_x - self.width() // 2
        x = min(max(x, pg.x() + 4), pg.right() - self.width() - 4)

        window_mid = pg.y() + pg.height() // 2

        if top_left.y() > window_mid:
            y = top_left.y() - self.height() - 45
        else:
            y = top_left.y() + target.height() + 12

        self.move(x, y)


    def prev_step(self):
        if self.step > 0:
            self.step -= 1
            self.show_step()

    def next_step(self):
        if self.step < len(self.STEPS) - 1:
            self.step += 1
            self.show_step()
        else:
            self.accept()


class BannerDelegate(QStyledItemDelegate):
    def __init__(self, window, parent=None):
        super().__init__(parent)
        self.window = window

    def paint(self, painter, option, index):
        es_row = getattr(self.window, "_es_header_index", None)

        if es_row is not None and index.row() == es_row:
            canvas = getattr(self.window, "_spain_canvas", None)

            if canvas is not None:
                painter.drawPixmap(option.rect, canvas, canvas.rect())

        super().paint(painter, option, index)




from core import file_reader, trial_tokens
from core import license_manager


def _lic_svg(kind, color, s=18):
    from PySide6.QtSvg import QSvgRenderer
    from PySide6.QtCore import QByteArray
    import sys
    base = Path(getattr(sys, "_MEIPASS",
                        Path(__file__).resolve().parents[1]))
    fp = base / "assets" / "icons" / "svg" / (kind + ".svg")
    pix = QPixmap(s, s)
    pix.fill(Qt.GlobalColor.transparent)
    if fp.exists():
        try:
            txt = fp.read_text(encoding="utf-8").replace(
                "currentColor", color)
            r = QSvgRenderer(QByteArray(txt.encode("utf-8")))
            if r.isValid():
                q = QPainter(pix)
                r.render(q)
                q.end()
                return pix
        except Exception:
            pass
    return _lic_pix(kind, color, s)


def _lic_pix(kind, color, s=18):
    from PySide6.QtCore import QPointF, QRectF
    from PySide6.QtGui import QPolygonF, QBrush
    import math
    pix = QPixmap(s, s)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    c = QColor(color)
    p.setPen(QPen(c, 1.5))
    m = s / 18.0
    if kind == "monitor":
        p.drawRoundedRect(QRectF(2*m, 3*m, 14*m, 10*m), 2, 2)
        p.drawLine(QPointF(9*m, 13*m), QPointF(9*m, 15*m))
        p.drawLine(QPointF(5*m, 15.5*m), QPointF(13*m, 15.5*m))
    elif kind == "copy":
        p.drawRoundedRect(QRectF(6*m, 6*m, 10*m, 10*m), 2, 2)
        p.drawRoundedRect(QRectF(3*m, 3*m, 10*m, 10*m), 2, 2)
    elif kind == "crown":
        pts = [QPointF(3*m, 12.5*m), QPointF(3*m, 6.5*m), QPointF(6.5*m, 9.5*m),
               QPointF(9*m, 4.5*m), QPointF(11.5*m, 9.5*m), QPointF(15*m, 6.5*m),
               QPointF(15*m, 12.5*m), QPointF(3*m, 12.5*m)]
        p.drawPolyline(QPolygonF(pts))
        p.drawLine(QPointF(3*m, 15*m), QPointF(15*m, 15*m))
    elif kind == "key":
        p.drawEllipse(QRectF(3*m, 10*m, 6*m, 6*m))
        p.drawLine(QPointF(8*m, 11*m), QPointF(15*m, 4*m))
        p.drawLine(QPointF(12*m, 7*m), QPointF(14*m, 9*m))
    elif kind == "info":
        p.drawEllipse(QRectF(2*m, 2*m, 14*m, 14*m))
        p.setBrush(QBrush(c))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(9*m, 5.5*m), 1.1*m, 1.1*m)
        p.setPen(QPen(c, 1.5))
        p.drawLine(QPointF(9*m, 8*m), QPointF(9*m, 13*m))
    elif kind == "shield":
        path = QPainterPath()
        path.moveTo(9*m, 2*m)
        path.lineTo(14.5*m, 4.2*m)
        path.lineTo(14.5*m, 8.5*m)
        path.quadTo(14.5*m, 13.5*m, 9*m, 16*m)
        path.quadTo(3.5*m, 13.5*m, 3.5*m, 8.5*m)
        path.lineTo(3.5*m, 4.2*m)
        path.closeSubpath()
        p.drawPath(path)
        p.drawLine(QPointF(6.3*m, 9*m), QPointF(8.3*m, 11*m))
        p.drawLine(QPointF(8.3*m, 11*m), QPointF(11.8*m, 6.8*m))
    elif kind == "wa":
        p.drawEllipse(QRectF(2.5*m, 2*m, 13*m, 13*m))
        p.setBrush(QBrush(c))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPolygon(QPolygonF([
            QPointF(4.5*m, 13.5*m), QPointF(3*m, 16.5*m), QPointF(8*m, 14.8*m)]))
        p.setPen(QPen(c, 1.5))
        p.drawArc(QRectF(6*m, 6*m, 6*m, 6*m), 200*16, 140*16)
    elif kind == "flask":
        p.drawLine(QPointF(6*m, 2*m), QPointF(12*m, 2*m))
        p.drawLine(QPointF(7*m, 2*m), QPointF(7*m, 7*m))
        p.drawLine(QPointF(11*m, 2*m), QPointF(11*m, 7*m))
        p.drawLine(QPointF(7*m, 7*m), QPointF(4*m, 13.5*m))
        p.drawLine(QPointF(11*m, 7*m), QPointF(14*m, 13.5*m))
        p.drawLine(QPointF(4*m, 13.5*m), QPointF(14*m, 13.5*m))
        p.drawLine(QPointF(5.6*m, 10.5*m), QPointF(12.4*m, 10.5*m))
    elif kind == "lock":
        p.drawRoundedRect(QRectF(4*m, 8*m, 10*m, 8*m), 2, 2)
        p.drawArc(QRectF(6*m, 3*m, 6*m, 8*m), 0, 180*16)
    elif kind == "help":
        p.drawEllipse(QRectF(2*m, 2*m, 14*m, 14*m))
        p.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        p.drawText(QRectF(2*m, 1*m, 14*m, 15*m), Qt.AlignmentFlag.AlignCenter, "?")
    elif kind == "wave":
        for i, h in enumerate([4, 8, 12, 8, 4]):
            x = (3 + i * 3) * m
            p.drawLine(QPointF(x, (9 - h / 2)*m), QPointF(x, (9 + h / 2)*m))
    elif kind == "bolt":
        poly = QPolygonF([QPointF(10*m, 2*m), QPointF(5*m, 10*m), QPointF(9*m, 10*m),
                          QPointF(8*m, 16*m), QPointF(13*m, 8*m), QPointF(9*m, 8*m),
                          QPointF(10*m, 2*m)])
        p.drawPolyline(poly)
    elif kind == "star":
        pts = []
        for i in range(10):
            ang = math.radians(-90 + i * 36)
            r = 7*m if i % 2 == 0 else 3*m
            pts.append(QPointF(9*m + r*math.cos(ang), 9*m + r*math.sin(ang)))
        p.drawPolyline(QPolygonF(pts))
    elif kind == "x":
        p.drawLine(QPointF(5*m, 5*m), QPointF(13*m, 13*m))
        p.drawLine(QPointF(13*m, 5*m), QPointF(5*m, 13*m))
    p.end()
    return pix


# -- constantes fallback licencia --
for _c, _v in (("BG", "#0b0e14"), ("TEXT", "#e6edf3"), ("MUTED", "#8b949e"), ("CARD", "#161b22"), ("BORDER", "#30363d"), ("GOLD", "#f5b544"), ("PURPLE", "#7c5cff"), ("BLUE", "#58a6ff"), ("GREEN", "#2ea043"), ("RED", "#ef4444")):
    if _c not in globals():
        globals()[_c] = _v


def _rounded_pixmap(path, size, radius):
    from PySide6.QtGui import QPainterPath
    src = QPixmap(str(path))
    out = QPixmap(size, size)
    out.fill(Qt.GlobalColor.transparent)
    p = QPainter(out)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    pp = QPainterPath()
    pp.addRoundedRect(0, 0, size, size, radius, radius)
    p.setClipPath(pp)
    p.drawPixmap(0, 0, src.scaled(
        size, size,
        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
        Qt.TransformationMode.SmoothTransformation))
    p.end()
    return out


class _StopwatchWidget(QWidget):
    """Cronometro animado con microfono difuminado dentro del dial."""

    def __init__(self, size=190):
        super().__init__()
        self.setFixedSize(size, size)
        self._angle = 0.0
        self._pulse = 0.0
        self._face = self._make_face(int(size * 0.62))
        from PySide6.QtCore import QTimer
        self._t = QTimer(self)
        self._t.timeout.connect(self._tick)
        self._t.start(40)

    def _make_face(self, size):
        from PySide6.QtGui import QPainterPath
        lp = MainWindow._resource_path(
            Path("assets") / "icons" / "licencia_left.png")
        if not lp.exists():
            lp = MainWindow._resource_path(
                Path("assets") / "icons" / "portada.png")
        out = QPixmap(size, size)
        out.fill(Qt.GlobalColor.transparent)
        if not lp.exists():
            return out
        src = QPixmap(str(lp))
        side = min(src.width(), src.height())
        src = src.copy((src.width() - side) // 2,
                       (src.height() - side) // 2, side, side)
        small = src.scaledToWidth(
            28, Qt.TransformationMode.SmoothTransformation)
        blurred = small.scaled(
            side, side, Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
        p = QPainter(out)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        p.setClipPath(path)
        p.drawPixmap(0, 0, blurred.scaled(
            size, size, Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(13, 17, 26, 165))
        p.drawEllipse(0, 0, size, size)
        p.end()
        return out

    def _tick(self):
        self._angle = (self._angle + 4) % 360
        self._pulse += 0.08
        self.update()

    def paintEvent(self, ev):
        import math
        from PySide6.QtGui import QPen
        from PySide6.QtCore import QPointF
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        s = w / 150.0
        cx = w / 2.0
        cy = w / 2.0
        glow = 0.6 + 0.4 * math.sin(self._pulse)
        p.setPen(Qt.PenStyle.NoPen)
        for r, a in ((72, 26 * glow), (60, 40 * glow)):
            p.setBrush(QColor(124, 92, 255, int(a)))
            p.drawEllipse(QPointF(cx, cy), r * s, r * s)
        d = 88 * s
        if not self._face.isNull():
            p.drawPixmap(QPointF(cx - d / 2, cy - d / 2),
                         self._face.scaled(
                             int(d), int(d),
                             Qt.AspectRatioMode.IgnoreAspectRatio,
                             Qt.TransformationMode.SmoothTransformation))
        p.setPen(QPen(QColor("#f5b544"), 4 * s))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QPointF(cx, cy), 45 * s, 45 * s)
        p.setPen(QPen(QColor("#f5b544"), 4 * s))
        p.drawLine(QPointF(cx, cy - 45 * s), QPointF(cx, cy - 56 * s))
        p.drawLine(QPointF(cx - 8 * s, cy - 58 * s),
                   QPointF(cx + 8 * s, cy - 58 * s))
        p.setPen(QPen(QColor("#c9d1d9"), 2 * s))
        for i in range(12):
            a = math.radians(i * 30)
            p.drawLine(
                QPointF(cx + 37 * s * math.sin(a),
                        cy - 37 * s * math.cos(a)),
                QPointF(cx + 42 * s * math.sin(a),
                        cy - 42 * s * math.cos(a)))
        a = math.radians(self._angle)
        p.setPen(QPen(QColor("#7c5cff"), 3.5 * s))
        p.drawLine(QPointF(cx, cy),
                   QPointF(cx + 33 * s * math.sin(a),
                           cy - 33 * s * math.cos(a)))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#7c5cff"))
        p.drawEllipse(QPointF(cx, cy), 4 * s, 4 * s)
        p.end()


class TrialActivatedDialog(QDialog):
    """Ventana de prueba gratuita activada (misma estetica)."""

    def __init__(self, parent, days_left):
        super().__init__(parent)
        self.setModal(True)
        self.setFixedWidth(480)
        self.setWindowTitle("Prueba gratuita")
        self.setStyleSheet(
            f"TrialActivatedDialog {{ background: {BG}; }}")
        root = QVBoxLayout(self)
        root.setContentsMargins(30, 26, 30, 24)
        root.setSpacing(12)
        root.addWidget(_StopwatchWidget(190), 0,
                       Qt.AlignmentFlag.AlignCenter)
        tt = QLabel("¡Prueba gratuita activada!")
        tt.setStyleSheet(
            f"color: {TEXT}; font-size: 20px; font-weight: 800;")
        tt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(tt)
        st = QLabel("Disfruta de todas las voces premium sin limites.")
        st.setStyleSheet(f"color: {MUTED}; font-size: 12px;")
        st.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(st)
        card = QFrame()
        card.setObjectName("tcard")
        card.setFixedHeight(46)
        card.setStyleSheet(
            f"#tcard {{ background: {CARD}; border: 1px solid {BORDER};"
            " border-radius: 10px; }")
        cl = QHBoxLayout(card)
        cl.setContentsMargins(14, 0, 14, 0)
        cl.setSpacing(10)
        cr = QLabel()
        cr.setPixmap(_lic_svg("crown", GOLD, 16))
        cl.addWidget(cr)
        from datetime import datetime, timedelta
        fin = datetime.now() + timedelta(days=max(0, days_left))
        lb = QLabel(
            f'<span style="color:{GOLD}; font-weight:700;">'
            f'{days_left} dias</span>  ·  hasta el '
            f'{fin.strftime("%d/%m/%Y")}')
        lb.setStyleSheet(f"color: {TEXT}; font-size: 12px;")
        cl.addWidget(lb)
        coin = QLabel()
        coin.setPixmap(_lic_svg("coins", GOLD, 14))
        cl.addWidget(coin)
        tk = QLabel(
            f'<span style="color:{GOLD}; font-weight:700;">'
            f'{trial_tokens.TRIAL_TOKENS:,} tokens</span>')
        tk.setStyleSheet(f"color: {TEXT}; font-size: 12px;")
        cl.addWidget(tk)
        cl.addStretch()
        root.addWidget(card)
        btn = QPushButton("Comenzar a usar WillpoVoice")
        btn.setFixedHeight(44)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setIcon(QIcon(_lic_svg("bolt", "#ffffff", 16)))
        btn.setIconSize(QSize(16, 16))
        btn.setStyleSheet(
            "QPushButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            " stop:0 #6d5df0, stop:0.5 #7c5cff, stop:1 #6d5df0);"
            " color: white; border: none; border-radius: 10px;"
            " font-size: 13px; font-weight: 700; }"
            " QPushButton:hover { background: #8d75ff; }")
        btn.clicked.connect(self.accept)
        root.addWidget(btn)


class LicenseDialog(QDialog):
    def __init__(self, parent, machine_id: str, days_left: int):
        super().__init__(parent)
        self.activated_key = ""
        self.trial_accepted = False
        self.days_left = days_left
        self.machine_id = machine_id

        BG = "#0b0f17"
        PANEL = "#0d1117"
        CARD = "#151a24"
        BORDER = "#262d3a"
        TEXT = "#e6edf3"
        MUTED = "#8b949e"
        PURPLE = "#7c5cff"
        BLUE = "#58a6ff"
        GOLD = "#f0a020"
        RED = "#ef4444"
        GREEN = "#2ea043"

        self.setWindowTitle("WillpoVoice - Licencia")
        self.setModal(True)
        self.setFixedSize(860, 620)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setStyleSheet(
            f"LicenseDialog {{ background: {BG}; }}"
            " QLabel { background: transparent; }"
            " QLineEdit { background: transparent; border: none;"
            f" color: {TEXT}; font-size: 12px; padding: 0; }}"
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        bar = QFrame()
        bar.setObjectName("licbar")
        bar.setFixedHeight(42)
        bar.setStyleSheet(
            f"#licbar {{ background: {PANEL}; border-bottom: 1px solid {BORDER}; }}")
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(12, 0, 6, 0)
        bl.setSpacing(10)
        blogo = QLabel()
        logo_p = MainWindow._resource_path(Path("assets") / "icons" / "logo.png")
        if not logo_p.exists():
            logo_p = MainWindow._resource_path(Path("assets") / "icons" / "icon.ico")
        if logo_p.exists():
            blogo.setPixmap(QPixmap(str(logo_p)).scaledToHeight(
                18, Qt.TransformationMode.SmoothTransformation))
        bl.addWidget(blogo)
        btitle = QLabel("WillpoVoice - Licencia")
        btitle.setStyleSheet(f"color: {TEXT}; font-size: 12px; font-weight: 600;")
        bl.addWidget(btitle)
        bl.addStretch()
        close_btn = QPushButton()
        close_btn.setFixedSize(34, 34)
        close_btn.setIcon(QIcon(_lic_svg("x", TEXT, 14)))
        close_btn.setIconSize(QSize(14, 14))
        close_btn.setStyleSheet(
            "QPushButton { background: transparent; border: none;"
            " border-radius: 8px; }"
            f" QPushButton:hover {{ background: {CARD}; }}"
        )
        close_btn.clicked.connect(self.reject)
        bl.addWidget(close_btn)
        root.addWidget(bar)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        root.addLayout(body, 1)

        left = QFrame()
        left.setObjectName("licleft")
        left.setFixedWidth(230)
        left.setStyleSheet(
            f"#licleft {{ background: #0a0d13; border-right: 1px solid {BORDER}; }}")
        lv = QVBoxLayout(left)
        lv.setContentsMargins(0, 0, 0, 0)
        lv.setSpacing(10)
        img = QLabel()
        img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img.setMinimumHeight(300)
        img.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
        left_img = MainWindow._resource_path(
            Path("assets") / "icons" / "licencia_left.png")
        if not left_img.exists():
            left_img = MainWindow._resource_path(
                Path("assets") / "icons" / "portada.png")
        if left_img.exists():
            img.setPixmap(QPixmap(str(left_img)))
            img.setScaledContents(True)
        lv.addWidget(img, 1)
        pcard = QFrame()
        pcard.setObjectName("pcard")
        pcard.setStyleSheet(
            "#pcard { background: rgba(18,21,29,235);"
            f" border: 1px solid {BORDER}; border-radius: 12px; }}")
        pv = QVBoxLayout(pcard)
        pv.setContentsMargins(14, 14, 14, 14)
        pv.setSpacing(12)
        pt = QLabel(
            f'WillpoVoice <span style="color:#8b7bff; font-weight:700;">'
            'Premium</span>')
        pt.setStyleSheet(f"color: {TEXT}; font-size: 13px; font-weight: 700;")
        pv.addWidget(pt)
        feats = [
            ("wave", "Voces naturales<br>de alta calidad"),
            ("bolt", "Conversiones rapidas<br>e ilimitadas"),
            ("shield", "Soporte prioritario<br>y actualizaciones"),
            ("star", "Nuevas voces<br>todas las semanas"),
        ]
        for kind, txt in feats:
            row = QHBoxLayout()
            row.setSpacing(12)
            row.setContentsMargins(0, 0, 0, 0)
            ic = QLabel()
            ic.setFixedSize(18, 18)
            ic.setPixmap(_lic_svg(kind, "#d7dde7", 16))
            ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
            row.addWidget(ic)
            lb = QLabel(txt)
            lb.setStyleSheet("color: #c9d1d9; font-size: 11px;")
            row.addWidget(lb)
            row.addStretch()
            pv.addLayout(row)
        pwrap = QHBoxLayout()
        pwrap.setContentsMargins(26, 0, 26, 14)
        pwrap.addWidget(pcard)
        lv.addLayout(pwrap, 0)
        body.addWidget(left)

        neon = QFrame()
        neon.setFixedWidth(2)
        neon.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:0,y2:1,"
            " stop:0 rgba(124,92,255,30), stop:0.5 #7c5cff,"
            " stop:1 rgba(124,92,255,30));")
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
        ne = QGraphicsDropShadowEffect(neon)
        ne.setBlurRadius(14)
        ne.setOffset(0, 0)
        ne.setColor(QColor("#7c5cff"))
        neon.setGraphicsEffect(ne)
        body.addWidget(neon)

        right = QWidget()
        right.setObjectName("licright")
        right.setStyleSheet(
            "#licright { background: qlineargradient(x1:0,y1:0,x2:0,y2:1,"
            " stop:0 #0d1220, stop:1 #0b0e14); }")
        rv = QVBoxLayout(right)
        rv.setContentsMargins(30, 16, 30, 10)
        rv.setSpacing(10)

        logo = QLabel()
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if logo_p.exists():
            logo.setPixmap(QPixmap(str(logo_p)).scaledToHeight(
                62, Qt.TransformationMode.SmoothTransformation))
        rv.addWidget(logo)

        title = QLabel(
            '<span style="color:#ffffff; font-weight:800;">Willpo</span>'
            '<span style="color:#8b7bff; font-weight:800;">Voice</span>')
        title.setStyleSheet("font-size: 30px; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rv.addWidget(title)

        subtitle = QLabel("Convierte texto en voz con voces naturales")
        subtitle.setStyleSheet(f"color: {MUTED}; font-size: 12px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rv.addWidget(subtitle)
        rv.addSpacing(4)

        id_card = QFrame()
        id_card.setObjectName("idcard")
        id_card.setFixedHeight(46)
        id_card.setStyleSheet(
            f"#idcard {{ background: {CARD}; border: 1px solid {BORDER};"
            " border-radius: 10px; }")
        il = QHBoxLayout(id_card)
        il.setContentsMargins(14, 0, 8, 0)
        il.setSpacing(10)
        mic = QLabel()
        mic.setPixmap(_lic_svg("monitor", PURPLE, 16))
        il.addWidget(mic)
        idl = QLabel("ID de esta maquina:")
        idl.setStyleSheet(f"color: {TEXT}; font-size: 12px;")
        il.addWidget(idl)
        il.addStretch()
        idv = QLabel(machine_id)
        idv.setStyleSheet(f"color: {BLUE}; font-size: 14px; font-weight: 700;")
        il.addWidget(idv)
        copy_btn = QPushButton()
        copy_btn.setFixedSize(30, 30)
        copy_btn.setIcon(QIcon(_lic_svg("copy", MUTED, 14)))
        copy_btn.setIconSize(QSize(14, 14))
        copy_btn.setStyleSheet(
            "QPushButton { background: transparent; border: none;"
            " border-radius: 8px; }"
            f" QPushButton:hover {{ background: {BORDER}; }}"
        )
        copy_btn.setToolTip("Copiar ID de maquina")
        copy_btn.clicked.connect(self._copy_id)
        il.addWidget(copy_btn)
        rv.addWidget(id_card)

        trial_card = QFrame()
        trial_card.setObjectName("trialcard")
        self._trial_card = trial_card
        trial_card.setCursor(Qt.CursorShape.PointingHandCursor)
        trial_card.installEventFilter(self)
        trial_card.setFixedHeight(46)
        trial_card.setStyleSheet(
            f"#trialcard {{ background: {CARD}; border: 1px solid {BORDER};"
            " border-radius: 10px; }")
        tl = QHBoxLayout(trial_card)
        tl.setContentsMargins(14, 0, 14, 0)
        tl.addStretch()
        cr = QLabel()
        cr.setPixmap(_lic_svg("crown", GOLD, 16))
        tl.addWidget(cr)
        if days_left >= 0:
            tr_txt = (
                'Prueba gratuita:  <span style="color:' + GOLD + ';'
                ' font-weight:700;">' + str(days_left) +
                ' dia(s) restante(s)</span>')
        else:
            tr_txt = (
                '<span style="color:' + RED + '; font-weight:700;">'
                'El periodo de prueba ha terminado.</span>')
        trl = QLabel(tr_txt)
        trl.setStyleSheet(f"color: {TEXT}; font-size: 12px;")
        tl.addWidget(trl)
        tl.addStretch()
        rv.addWidget(trial_card)
        rv.addSpacing(2)

        kl = QLabel("Ingresa tu clave de licencia:")
        kl.setStyleSheet(f"color: {TEXT}; font-size: 12px;")
        rv.addWidget(kl)

        keyframe = QFrame()
        keyframe.setObjectName("keyframe")
        keyframe.setFixedHeight(44)
        keyframe.setStyleSheet(
            f"#keyframe {{ background: #10141c; border: 1.5px solid {PURPLE};"
            " border-radius: 10px; }")
        kf = QHBoxLayout(keyframe)
        kf.setContentsMargins(14, 0, 14, 0)
        kf.setSpacing(10)
        kicon = QLabel()
        kicon.setPixmap(_lic_svg("key", PURPLE, 16))
        kf.addWidget(kicon)
        self.key_edit = QLineEdit()
        self.key_edit.setPlaceholderText(
            "WVP-XXXX-XXXX-XXXX-XXXX  o  WVP2-...")
        kf.addWidget(self.key_edit)
        rv.addWidget(keyframe)

        hint_row = QHBoxLayout()
        hint_row.setSpacing(8)
        hi = QLabel()
        hi.setPixmap(_lic_svg("info", MUTED, 14))
        hint_row.addWidget(hi)
        self.hint_label = QLabel(
            "Puedes encontrar tu clave en el correo de compra.")
        self.hint_label.setStyleSheet(f"color: {MUTED}; font-size: 10.5px;")
        hint_row.addWidget(self.hint_label)
        hint_row.addStretch()
        rv.addLayout(hint_row)
        rv.addSpacing(2)

        activate = QPushButton("Activar Licencia")
        activate.setFixedHeight(44)
        activate.setCursor(Qt.CursorShape.PointingHandCursor)
        activate.setIcon(QIcon(_lic_svg("shield", "#ffffff", 18)))
        activate.setIconSize(QSize(18, 18))
        activate.setStyleSheet(
            "QPushButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            " stop:0 #6d5df0, stop:0.5 #7c5cff, stop:1 #6d5df0);"
            " color: white; border: none; border-radius: 10px;"
            " font-size: 14px; font-weight: 700; }"
            " QPushButton:hover { background: #8d75ff; }"
        )
        activate.clicked.connect(self.try_activate)
        rv.addWidget(activate)

        row2 = QHBoxLayout()
        row2.setSpacing(10)
        buy = QPushButton("Comprar por WhatsApp")
        buy.setFixedHeight(42)
        buy.setCursor(Qt.CursorShape.PointingHandCursor)
        buy.setIcon(QIcon(_lic_svg("wa", GREEN, 16)))
        buy.setIconSize(QSize(16, 16))
        buy.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {GREEN};"
            f" border: 1px solid {GREEN}; border-radius: 10px;"
            " font-size: 12px; font-weight: 600; }"
            " QPushButton:hover { background: rgba(46,160,67,35); }"
        )
        buy.clicked.connect(self.open_whatsapp)
        row2.addWidget(buy, 1)
        if days_left >= 0:
            trial_btn = QPushButton("Continuar en prueba")
            trial_btn.setFixedHeight(42)
            trial_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            trial_btn.setIcon(QIcon(_lic_svg("flask", "#c9d1d9", 16)))
            trial_btn.setIconSize(QSize(16, 16))
            trial_btn.setStyleSheet(
                f"QPushButton {{ background: transparent; color: #c9d1d9;"
                f" border: 1px solid {BORDER}; border-radius: 10px;"
                " font-size: 12px; font-weight: 600; }"
                f" QPushButton:hover {{ border-color: {MUTED}; }}"
            )
            trial_btn.clicked.connect(self.accept_trial)
            row2.addWidget(trial_btn, 1)
        rv.addLayout(row2)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {BORDER};")
        rv.addWidget(sep)

        footer = QHBoxLayout()
        footer.setSpacing(8)
        lo = QLabel()
        lo.setPixmap(_lic_svg("lock", MUTED, 13))
        footer.addWidget(lo)
        fl = QLabel("Tu informacion esta 100% segura y encriptada.")
        fl.setStyleSheet(f"color: {MUTED}; font-size: 10.5px;")
        footer.addWidget(fl)
        footer.addStretch()
        help_btn = QPushButton("Necesitas ayuda?")
        help_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        help_btn.setIcon(QIcon(_lic_svg("help", BLUE, 14)))
        help_btn.setIconSize(QSize(14, 14))
        help_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {BLUE};"
            " border: none; font-size: 11px; font-weight: 600; }"
            " QPushButton:hover { text-decoration: underline; }"
        )
        help_btn.clicked.connect(self.open_whatsapp)
        footer.addWidget(help_btn)
        rv.addLayout(footer)
        body.addWidget(right, 1)

        self._drag_pos = None

    def _copy_id(self):
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(self.machine_id)
        self.hint_label.setText("ID copiado al portapapeles.")
        self.hint_label.setStyleSheet("color: #58a6ff; font-size: 10.5px;")

    def mousePressEvent(self, event):
        self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def try_activate(self) -> None:
        key = self.key_edit.text()
        if license_manager.validate_key(key, self.machine_id):
            self.activated_key = "".join(key.strip().upper().split())
            self.accept()
        else:
            self.hint_label.setText("Clave invalida para esta maquina.")
            self.hint_label.setStyleSheet("color: #ef4444; font-size: 10.5px;")

    def open_whatsapp(self) -> None:
        msg = quote(
            f"Hola, quiero una licencia de WillpoVoice. "
            f"Mi ID de maquina: {self.machine_id}"
        )
        QDesktopServices.openUrl(QUrl(f"https://wa.me/51923073560?text={msg}"))

    def eventFilter(self, obj, event):
        from PySide6.QtCore import QEvent
        if (obj is getattr(self, "_trial_card", None) and
                event.type() == QEvent.Type.MouseButtonRelease):
            self._on_trial_card_clicked()
            return True
        return super().eventFilter(obj, event)

    def _on_trial_card_clicked(self):
        if getattr(self, "_trial_open", False):
            return
        if getattr(self, "days_left", -1) < 0:
            return
        self._trial_open = True
        dlg = TrialActivatedDialog(self, max(0, self.days_left))
        dlg.exec()
        self._trial_open = False
        self.trial_accepted = True
        self.accept()

    def accept_trial(self) -> None:
        self.trial_accepted = True
        self.accept()



PREMIUM_PHOTOS = {
    "andrew": "ms_andrew.png",
    "ava": "ms_ava.png",
    "brian": "ms_brian.png",
    "emma": "ms_emma.png",
    "florian": "ms_florian.png",
    "giuseppe": "ms_giuseppe.png",
    "hyunsu": "ms_hyunsu.png",
    "remy": "ms_remy.png",
    "seraphina": "ms_seraphina.png",
    "william": "ms_william.png",
    "vivienne": "ms_vivienne.png",
    "thalita": "ms_thalita.png",
    "elvira": "ms_elvira.png",
    "alonso": "ms_alonso.png",
    "dalia": "ms_dalia.png",
}

FEMALE_NAMES = (
    "helena", "sabina", "elena", "elvira", "dalia", "paloma", "zira",
    "susan", "jenny", "aria", "michelle", "ashley", "heera",
    "katja", "hortense", "elsa", "laura", "conchita", "lucia",
    "valeria", "sofia", "paula", "camila", "francisca", "marina",
    "irene", "joana", "carmen", "penelope", "yara", "mariana",
    "isabela", "nuria", "libby", "maisie", "natasha", "clara",
    "cora", "layla", "sonia", "xiaoxiao", "yaoyao", "vivienne",
    "thalita", "emma", "ava", "seraphina", "ines", "maria",
    "ana", "diana", "sara", "vera", "nina",
)

MALE_NAMES = (
    "tomas", "jorge", "alvaro", "alonso", "raul", "pablo", "juan",
    "diego", "carlos", "enrique", "david", "guy", "davis",
    "brandon", "eric", "stephane", "stefan", "willem", "cosimo",
    "george", "harry", "ryan", "thomas", "andrew", "brian",
    "florian", "giuseppe", "hyunsu", "remy", "william", "liam",
    "noah", "james", "pedro", "mateo", "sebastian", "oscar",
    "hugo", "ivan", "sergio", "andres", "felipe",
)



class PreviewWorker(QThread):
    def __init__(self, adapter, voice, text):
        super().__init__()
        self.adapter = adapter
        self.voice = voice
        self.text = text

    def run(self):
        import pythoncom
        import win32com.client
        pythoncom.CoInitialize()
        try:
            sapi = win32com.client.Dispatch("SAPI.SpVoice")
            if self.adapter is not None:
                if self.voice:
                    self.adapter.set_voice(self.voice)
                try:
                    sapi.Voice = self.adapter.sapi.Voice
                except Exception:
                    pass
            sapi.Rate = 0
            sapi.Volume = 100
            sapi.Speak(self.text)
        finally:
            pythoncom.CoUninitialize()


class VoiceRow(QFrame):
    def __init__(self, window, voice_name, premium, photo_path=None, parent=None):
        super().__init__(parent)
        self.window = window
        self.voice_name = voice_name
        self.premium = premium
        self._selected = False
        self.setFixedHeight(58)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 6, 8)
        layout.setSpacing(8)

        photo = QLabel()
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
        layout.addWidget(photo)

        texts_widget = QWidget()
        texts_widget.setStyleSheet("background: transparent;")
        texts = QVBoxLayout(texts_widget)
        texts.setContentsMargins(0, 0, 0, 0)
        texts.setSpacing(1)
        name_label = QLabel(self._display_name())
        name_label.setStyleSheet(
            "color: #eef2fa; font-size: 12px; font-weight: 700; "
            "background: transparent;"
        )
        sub_label = QLabel("WillpoVoice Premium" if premium else "Voz estandar")
        sub_label.setStyleSheet(
            ("color: #ffd75e;" if premium else "color: #8fa0bd;")
            + " font-size: 10px; background: transparent;"
        )
        name_label.setMinimumWidth(0)
        name_label.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred
        )
        sub_label.setMinimumWidth(0)
        sub_label.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred
        )
        texts_widget.setMinimumWidth(0)
        texts.addWidget(name_label)
        texts.addWidget(sub_label)
        layout.addWidget(texts_widget, 1)

        self.play_btn = QPushButton()
        self.play_btn.setFixedSize(30, 30)
        self.play_btn.setToolTip("Hola, esta es mi voz")
        play_pix = QPixmap(14, 14)
        play_pix.fill(Qt.GlobalColor.transparent)
        painter_play = QPainter(play_pix)
        painter_play.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter_play.setBrush(QColor("#4a7dff"))
        painter_play.setPen(Qt.PenStyle.NoPen)
        painter_play.drawPolygon(
            QPolygon([QPoint(3, 1), QPoint(13, 7), QPoint(3, 13)])
        )
        painter_play.end()
        self.play_btn.setIcon(QIcon(play_pix))
        self.play_btn.setIconSize(QSize(14, 14))
        self.play_btn.setStyleSheet(
            "QPushButton { background: #1a2236; border: none; border-radius: 15px; }"
            "QPushButton:hover { background: #232f4b; }"
        )
        self.play_btn.clicked.connect(self._preview)
        layout.addWidget(self.play_btn)

        self.plus_btn = QPushButton()
        self.plus_btn.setFixedSize(30, 30)
        if premium:
            plus_bg = (
                "background: qlineargradient(x1:0,y1:0,x2:0,y2:1, "
                "stop:0 #ffd75e, stop:1 #f79009); color: white;"
            )
        else:
            plus_bg = "background: #1a2236; color: #eef2fa;"
        self.plus_btn.setStyleSheet(
            "QPushButton { " + plus_bg + " border: none; border-radius: 15px; "
            "font-size: 15px; font-weight: 700; }"
            "QPushButton:hover { border: 1px solid #4a7dff; }"
        )
        self.plus_btn.clicked.connect(self._select)
        layout.addWidget(self.plus_btn)
        self._apply_style()
        self.mouseReleaseEvent = lambda event: self._select()

    def _display_name(self):
        n = self.voice_name.replace("Microsoft ", "")
        if "Multilingual" in n:
            first = n.split("Multilingual")[0].strip()
            return f"{first} (Multilingual)"
        n = n.replace("Online (Natural)", "").replace("(Natural)", "")
        return n.strip()

    def _avatar_pixmap(self, source: QPixmap, size: int, ring: str) -> QPixmap:
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
        return pix

    def _plus_icon(self) -> QIcon:
        pix = QPixmap(16, 16)
        pix.fill(Qt.GlobalColor.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(
            QPen(
                QColor("#ffffff"),
                2.6,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
            )
        )
        p.drawLine(3, 8, 13, 8)
        p.drawLine(8, 3, 8, 13)
        p.end()
        return QIcon(pix)

    def _check_icon(self) -> QIcon:
        pix = QPixmap(16, 16)
        pix.fill(Qt.GlobalColor.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(
            QPen(
                QColor("#ffffff"),
                2.6,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin,
            )
        )
        p.drawPolyline(QPolygon([QPoint(3, 8), QPoint(6, 12), QPoint(13, 4)]))
        p.end()
        return QIcon(pix)

    def _apply_style(self):
        if self._selected:
            self.setStyleSheet(
                "VoiceRow { background: #1a2236; border: 1px solid #ffd75e; "
                "border-radius: 12px; }"
            )
            self.plus_btn.setIcon(self._check_icon())
            self.plus_btn.setIconSize(QSize(16, 16))
        else:
            self.setStyleSheet(
                "VoiceRow { background: #131a2b; border: 1px solid #232f4b; "
                "border-radius: 12px; }"
            )
            self.plus_btn.setIcon(self._plus_icon())
            self.plus_btn.setIconSize(QSize(16, 16))

    def set_selected(self, selected):
        self._selected = selected
        self._apply_style()

    def _select(self):
        self.window.voice_combo.setCurrentText(self.voice_name)
        try:
            self.window.engine.select_voice(self.voice_name)
        except Exception:
            pass
        self.window._sync_row_selection()
        self.window.statusBar().showMessage(
            f"Voz seleccionada: {self.voice_name}"
        )

    def _preview(self):
        self.window._preview_voice(self.voice_name)



class MainWindow(QMainWindow):

    MAX_HISTORY = 10

    def __init__(self):
        super().__init__()

        self.logger = logging.getLogger("naturalvoice_tts.ui")
        self.settings = load_settings()

        self.setWindowTitle("WillpoVoice v1.2.8")
        self.resize(950, 650)

        icon_path = self._resource_path(Path("assets") / "icons" / "icon.ico")

        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self.engine = TTSEngine(logger=self.logger)
        self.exporter = AudioExporter(adapter=self.engine.adapter, logger=self.logger)
        self.export_worker = None
        self.swatch_buttons = []

        self._build_ui()
        self._connect_signals()
        self._apply_theme()
        self._load_voices()
        self._history_full = []
        self._load_history()

        self.resize(950, 650)
        self._center_on_screen(self)

    @staticmethod
    def _center_on_screen(widget):
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QPoint
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        geo = screen.availableGeometry()
        x = geo.x() + (geo.width() - widget.width()) // 2
        y = geo.y() + (geo.height() - widget.height()) // 2
        widget.move(QPoint(x, y))

    @staticmethod
    def _resource_path(rel: Path) -> Path:
        base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
        return base / rel

    def _animate_fire(self) -> None:
        if not getattr(self, "_hot_indices", None):
            return

        if not getattr(self, "_fire_frames", None):
            return

        self._fire_frame = (self._fire_frame + 1) % len(self._fire_frames)
        icon = self._fire_frames[self._fire_frame]

        for i in self._hot_indices:
            self.voice_combo.setItemData(
                i, icon, Qt.ItemDataRole.DecorationRole
            )

        header_index = getattr(self, "_multi_header_index", None)

        if header_index is not None and getattr(self, "_header_frames", None):
            frame = self._header_frames[self._fire_frame % len(self._header_frames)]
            self.voice_combo.setItemData(
                header_index, frame, Qt.ItemDataRole.DecorationRole
            )

            if getattr(self, "_flames_movie", None) is None:
                if self.settings.get("dark_mode", True):
                    text_colors = [
                        "#ff3d00",
                        "#ff6a00",
                        "#ff9500",
                        "#ffb400",
                        "#ff7b00",
                    ]
                else:
                    text_colors = ["#b91c1c", "#c2410c", "#9a3412", "#b45309"]

                self.voice_combo.setItemData(
                    header_index,
                    QColor(text_colors[self._fire_frame % len(text_colors)]),
                    Qt.ItemDataRole.ForegroundRole,
                )

    def _update_spain_bg(self, _frame: int = 0) -> None:
        movie = getattr(self, "_spain_movie", None)

        if movie is None:
            return

        header_index = getattr(self, "_es_header_index", None)

        if header_index is None:
            return

        pixmap = movie.currentPixmap()
        width = max(self.voice_combo.width(), 1)
        height = 30

        canvas = QPixmap(width, height)
        canvas.fill(QColor("#3a0d0d"))

        painter = QPainter(canvas)

        stretched = pixmap.scaled(
            width,
            height,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        painter.drawPixmap(0, 0, stretched)
        painter.fillRect(canvas.rect(), QColor(0, 0, 0, 150))

        flag = pixmap.scaledToHeight(
            height - 4, Qt.TransformationMode.SmoothTransformation
        )
        painter.drawPixmap(width - flag.width() - 4, 2, flag)
        painter.end()

        self._spain_canvas = canvas
        self.voice_combo.view().viewport().update()

    def _update_flames_bg(self, _frame: int = 0) -> None:
        movie = getattr(self, "_flames_movie", None)

        if movie is None:
            return

        pixmap = movie.currentPixmap()
        offset = int(pixmap.height() * 0.4)
        strip = pixmap.copy(
            0, offset, pixmap.width(), pixmap.height() - offset
        )
        brush = QBrush(strip)

        header_index = getattr(self, "_multi_header_index", None)

        if header_index is not None:
            self.voice_combo.setItemData(
                header_index, brush, Qt.ItemDataRole.BackgroundRole
            )

    def _apply_hot_background(self) -> None:
        dark = self.settings.get("dark_mode", True)

        if dark:
            hot_color = QColor("#2a2410")
            group_colors = {
                "es": QColor("#101c33"),
                "desktop": QColor("#131a2b"),
                "en": QColor("#131a2b"),
            }
        else:
            hot_color = QColor("#fff6d8")
            group_colors = {
                "es": QColor("#e8f0ff"),
                "desktop": QColor("#eef1f6"),
                "en": QColor("#eef1f6"),
            }

        hot_brush = QBrush(hot_color)

        for i in getattr(self, "_hot_indices", []):
            self.voice_combo.setItemData(
                i, hot_brush, Qt.ItemDataRole.BackgroundRole
            )

        for group, indices in getattr(self, "_group_indices", {}).items():
            brush = QBrush(group_colors[group])

            for i in indices:
                self.voice_combo.setItemData(
                    i, brush, Qt.ItemDataRole.BackgroundRole
                )

    def _icon_all_modes(self, name: str):
        path = self._resource_path(Path("assets") / "icons" / name)

        if not path.exists():
            return QIcon()

        pix = QPixmap(str(path))
        icon = QIcon()
        icon.addPixmap(pix, QIcon.Mode.Normal)
        icon.addPixmap(pix, QIcon.Mode.Disabled)
        icon.addPixmap(pix, QIcon.Mode.Selected)
        return icon

    def _add_shadow(self, widget) -> None:
        effect = QGraphicsDropShadowEffect(widget)
        effect.setBlurRadius(12)
        effect.setOffset(0, 2)
        effect.setColor(QColor(0, 0, 0, 90))
        widget.setGraphicsEffect(effect)

    def _button_icon(self, name: str):
        path = self._resource_path(Path("assets") / "icons" / name)

        if path.exists():
            return QIcon(str(path))

        return QIcon()

    def _voices_icon_pixmap(self) -> QPixmap:
        pix = QPixmap(24, 24)
        pix.fill(Qt.GlobalColor.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = QColor("#ffd75e")
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(color)
        p.drawEllipse(5, 4, 7, 7)
        body = QPainterPath()
        body.addRoundedRect(2, 13, 13, 8, 4, 4)
        p.drawPath(body)
        p.setBrush(Qt.GlobalColor.transparent)
        p.setPen(QPen(color, 1.8))
        p.drawArc(QRect(14, 7, 8, 8), -50 * 16, 100 * 16)
        p.drawArc(QRect(15, 4, 9, 9), -50 * 16, 100 * 16)
        p.end()
        return pix

    def _build_ui(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        self.cover_label = QLabel()
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._cover_pixmap = None
        self._cover_player = None
        self._cover_video_path = self._resource_path(
            Path("assets") / "icons" / "portada.webm"
        )

        if not self._cover_video_path.exists():
            self._cover_video_path = self._resource_path(
                Path("assets") / "icons" / "portada.mp4"
            )

        self._cover_image_path = self._resource_path(
            Path("assets") / "icons" / "portada.png"
        )

        self.header_widget = QWidget()
        self.header_widget.setFixedHeight(170)
        self.header_widget.setStyleSheet("background: transparent;")
        header_layout = QHBoxLayout(self.header_widget)

        logo_label = QLabel()
        logo_label.setStyleSheet("background: transparent;")
        logo_path = self._resource_path(Path("assets") / "icons" / "logo.png")

        if not logo_path.exists():
            logo_path = self._resource_path(Path("assets") / "icons" / "icon.ico")

        if logo_path.exists():
            pixmap = QPixmap(str(logo_path)).scaledToHeight(
                48, Qt.TransformationMode.SmoothTransformation
            )
            logo_label.setPixmap(pixmap)

        title_label = QLabel("WillpoVoice")
        title_label.setStyleSheet(
            "font-size: 22px; font-weight: 700; background: transparent;"
        )

        subtitle_label = QLabel("Convierte texto en voz con voces naturales")
        subtitle_label.setStyleSheet("font-size: 12px; background: transparent;")

        text_container = QWidget()
        text_container.setStyleSheet("background: transparent;")
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(10, 0, 0, 0)
        text_layout.setSpacing(4)
        text_layout.addWidget(title_label)
        text_layout.addWidget(subtitle_label)

        for lbl in (logo_label, title_label, subtitle_label):
            shadow = QGraphicsDropShadowEffect(lbl)
            shadow.setBlurRadius(8)
            shadow.setColor(QColor(0, 0, 0, 160))
            shadow.setOffset(0, 1)
            lbl.setGraphicsEffect(shadow)

        header_layout.addWidget(logo_label, 0, Qt.AlignmentFlag.AlignVCenter)
        header_layout.addWidget(text_container, 0, Qt.AlignmentFlag.AlignVCenter)
        header_layout.addStretch()

        main_layout.addWidget(self.header_widget)
        self._setup_cover()

        self.voice_group = QGroupBox("Voz")
        voice_layout = QVBoxLayout(self.voice_group)
        self.voice_combo = QComboBox()
        voice_layout.addWidget(self.voice_combo)
        self.voice_group.hide()

        self.voice_search = QLineEdit()
        self.voice_search.setPlaceholderText("Buscar voces...")
        self.voice_search.textChanged.connect(self._filter_voice_rows)
        self.refresh_voices_button = QPushButton("Actualizar voces")

        self.voice_scroll = QScrollArea()
        self.voice_scroll.setWidgetResizable(True)
        self.voice_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.voice_scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        self.voice_rows_container = QWidget()
        self.voice_rows_container.setStyleSheet("background: transparent;")
        self.voice_rows_layout = QVBoxLayout(self.voice_rows_container)
        self.voice_rows_layout.setContentsMargins(0, 0, 0, 0)
        self.voice_rows_layout.setSpacing(8)
        self.voice_scroll.setWidget(self.voice_rows_container)
        self.voice_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.voice_dock = QDockWidget("Voces", self)
        self.voice_dock.setObjectName("voiceDock")
        self.voice_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetClosable
        )
        self.voice_dock.setStyleSheet(
            "QDockWidget { background: #0a0f1c; color: #ffd75e; font-weight: 700; border: none; }"
            "QDockWidget::title { background: #131a2b; padding: 8px; }"
        )
        dock_content = QWidget()
        dock_content.setStyleSheet("background: #0a0f1c;")
        dock_layout = QVBoxLayout(dock_content)
        dock_layout.setContentsMargins(10, 10, 10, 10)
        dock_layout.setSpacing(8)
        dock_top = QHBoxLayout()
        dock_top.addWidget(self.voice_search, 1)
        dock_top.addWidget(self.refresh_voices_button)
        dock_layout.addLayout(dock_top)
        dock_layout.addWidget(self.voice_scroll, 1)
        self.voice_dock.setWidget(dock_content)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.voice_dock)
        self.voice_dock.setVisible(False)

        self.history_group = QGroupBox("Historial")
        history_layout = QHBoxLayout(self.history_group)

        self.history_combo = QComboBox()
        self.history_combo.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
        )
        self.history_combo.setMinimumWidth(250)
        self.clear_history_button = QPushButton("Limpiar")
        self.support_button = QPushButton("Soporte")
        self.help_button = QPushButton("? Ayuda")
        self.help_button.setToolTip("Guia paso a paso de WillpoVoice")
        self.help_button.clicked.connect(self.show_help)

        support_icon = self._resource_path(Path("assets") / "icons" / "headset.png")

        if support_icon.exists():
            self.support_button.setIcon(QIcon(str(support_icon)))
            self.support_button.setIconSize(QSize(18, 18))


        history_layout.addWidget(self.history_combo, 1)
        history_layout.addWidget(self.clear_history_button)
        main_layout.addWidget(self.history_group)

        palette_layout = QHBoxLayout()
        palette_layout.addStretch()
        palette_layout.addWidget(self.support_button)
        palette_layout.addWidget(self.help_button)
        main_layout.addLayout(palette_layout)

        self.text_edit = QPlainTextEdit()
        self.text_edit.setPlaceholderText(
            "Escribe aquí el texto que quieres convertir a voz..."
        )
        main_layout.addWidget(self.text_edit, 1)

        counter_layout = QHBoxLayout()
        counter_layout.addStretch()
        self.counter_label = QLabel("0 caracteres")
        counter_layout.addWidget(self.counter_label)
        main_layout.addLayout(counter_layout)

        controls_layout = QHBoxLayout()

        controls_layout.addWidget(QLabel("Velocidad:"))
        self.rate_slider = QSlider(Qt.Orientation.Horizontal)
        self.rate_slider.setMinimum(-10)
        self.rate_slider.setMaximum(10)
        self.rate_slider.setValue(0)
        self.rate_value_label = QLabel("0")
        controls_layout.addWidget(self.rate_slider)
        controls_layout.addWidget(self.rate_value_label)

        controls_layout.addSpacing(20)

        controls_layout.addWidget(QLabel("Volumen:"))
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(100)
        self.volume_value_label = QLabel("100")
        controls_layout.addWidget(self.volume_slider)
        controls_layout.addWidget(self.volume_value_label)

        main_layout.addLayout(controls_layout)

        buttons_layout = QHBoxLayout()

        self.speak_button = QPushButton("Reproducir")
        self.speak_button.setIcon(self._button_icon("play.png"))

        self.stop_button = QPushButton("Detener")
        self.stop_button.setIcon(self._button_icon("pause.png"))

        self.export_button = QPushButton("Exportar")
        self.export_button.setIcon(self._button_icon("save.png"))
        self.export_menu = QMenu(self)
        self.export_menu.setMinimumWidth(260)
        self.export_menu.setStyleSheet(
            "QMenu { background-color: #131a2b; border: 1px solid #232f4b; "
            "border-radius: 12px; padding: 6px; } "
            "QMenu::separator { height: 1px; background: #232f4b; }"
        )
        self._add_menu_row(
            self._audio_icon("#4da3ff", "WAV"),
            "Audio WAV  (.wav, sin compresion)",
            self.export_wav,
            menu=self.export_menu,
        )
        self.export_menu.addSeparator()
        self._add_menu_row(
            self._audio_icon("#f2a33c", "MP3"),
            "Audio MP3  (.mp3, comprimido)",
            self.export_mp3,
            menu=self.export_menu,
        )
        self.export_button.installEventFilter(self)
        self.export_menu.installEventFilter(self)

        self.open_file_button = QPushButton("Abrir")
        self.open_menu = QMenu(self)
        self.open_menu.setMinimumWidth(260)
        self.open_menu.setStyleSheet(
            "QMenu { background-color: #131a2b; border: 1px solid #232f4b; "
            "border-radius: 12px; padding: 6px; } "
            "QMenu::separator { height: 1px; background: #232f4b; }"
        )

        self._add_menu_row(
            self._format_icon("#4da3ff", "TXT"),
            "Texto plano  (.txt, .md, .log)",
            lambda: self._open_document(
                "Archivos de texto (*.txt *.md *.log *.csv)"
            ),
        )
        self.open_menu.addSeparator()
        self._add_menu_row(
            self._format_icon("#e02020", "PDF"),
            "Documento PDF  (.pdf)",
            lambda: self._open_document("Documentos PDF (*.pdf)"),
        )
        self.open_menu.addSeparator()
        self._add_menu_row(
            self._format_icon("#2b7de9", "DOC"),
            "Word moderno  (.docx)",
            lambda: self._open_document("Documentos Word (*.docx)"),
        )
        self.open_menu.addSeparator()
        self._add_menu_row(
            self._format_icon("#185abd", "DOC"),
            "Word antiguo  (.doc, requiere Word)",
            lambda: self._open_document("Word antiguo (*.doc)"),
        )
        self.open_menu.addSeparator()
        self._add_menu_row(
            self._format_icon("#f2a33c", "RTF"),
            "Formato enriquecido  (.rtf)",
            lambda: self._open_document("Formato enriquecido (*.rtf)"),
        )
        self.open_menu.addSeparator()
        self._add_menu_row(
            self._format_icon("#9b59f6", "WEB"),
            "Pagina web  (.html)",
            lambda: self._open_document("Paginas web (*.html *.htm)"),
        )
        self.open_menu.addSeparator()
        self._add_menu_row(
            self._format_icon("#4de3b0", "TODO"),
            "Todos los formatos",
            lambda: self._open_document(
                "Todos (*.txt *.md *.log *.csv *.pdf *.docx *.doc *.rtf "
                "*.html *.htm)"
            ),
        )
        self.open_file_button.installEventFilter(self)
        self.open_menu.installEventFilter(self)
        self.open_file_button.setIcon(self._button_icon("folder.png"))

        self.voices_button = QPushButton("Voces")
        self.voices_button.setIcon(self._button_icon("multi_0.png"))
        self.voices_button.setIconSize(QSize(18, 18))
        self.header_widget.layout().insertWidget(
            0,
            self.voices_button,
            0,
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
        )
        self.voices_button.setStyleSheet(
            "QPushButton { background: #131a2b; border: 1px solid #ffd75e; "
            "border-radius: 10px; color: #ffd75e; font-weight: 700; "
            "padding: 8px 16px; }"
            "QPushButton:hover { background: #1a2236; }"
        )
        self.theme_button = QPushButton("Modo claro")
        self.theme_button.setIcon(self._button_icon("theme.png"))

        self.exit_button = QPushButton("Salir")
        self.exit_button.setIcon(self._button_icon("exit.png"))

        for btn in (
            self.speak_button,
            self.stop_button,
            self.export_button,
            self.open_file_button,
            self.theme_button,
            self.exit_button,
        ):
            btn.setIconSize(QSize(18, 18))

        for btn in (
            self.speak_button,
            self.stop_button,
            self.export_button,
            self.open_file_button,
            self.theme_button,
            self.exit_button,
            self.support_button,
        ):
            self._add_shadow(btn)

        buttons_layout.addWidget(self.speak_button)
        buttons_layout.addWidget(self.stop_button)
        buttons_layout.addWidget(self.export_button)
        buttons_layout.addWidget(self.open_file_button)
        buttons_layout.addWidget(self.theme_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.exit_button)

        main_layout.addLayout(buttons_layout)

    def _connect_signals(self) -> None:
        self.speak_button.clicked.connect(self.speak_text)
        self.stop_button.clicked.connect(self.stop_speech)
        self.export_button.clicked.connect(self._show_export_menu)
        self.open_file_button.clicked.connect(self._show_open_menu)
        self.theme_button.clicked.connect(self.toggle_theme)
        self.refresh_voices_button.clicked.connect(self.refresh_voices)
        self.voices_button.clicked.connect(self.toggle_voice_dock)
        self.clear_history_button.clicked.connect(self.clear_history)
        self.support_button.clicked.connect(self.open_support)

        self.support_hue = 0
        self.support_timer = QTimer(self)
        self.support_timer.timeout.connect(self._cycle_support_color)
        self.support_timer.start(120)

        self.fire_timer = QTimer(self)
        self.fire_timer.timeout.connect(self._animate_fire)
        self.fire_timer.start(200)
        self.exit_button.clicked.connect(self.close)

        self.history_combo.activated.connect(self.on_history_selected)
        self.text_edit.textChanged.connect(self.update_counter)

        self.rate_slider.valueChanged.connect(
            lambda value: self.rate_value_label.setText(str(value))
        )
        self.volume_slider.valueChanged.connect(
            lambda value: self.volume_value_label.setText(str(value))
        )

    def _launch_first_tour(self) -> None:
        self.settings["tour_seen"] = True

        for name in ("_save_settings", "save_settings"):
            fn = getattr(self, name, None)

            if callable(fn):
                try:
                    fn()
                except Exception:
                    pass

                break

        self.show_help()

    def showEvent(self, event):
        super().showEvent(event)

        if not getattr(self, "_license_checked", False):
            self._license_checked = True

            if not self._check_license():
                self.close()
                return

        if not getattr(self, "_tour_pending_checked", False):
            self._tour_pending_checked = True

            if not self.settings.get("tour_seen", False):
                QTimer.singleShot(400, self._launch_first_tour)


    def _place_cover(self) -> None:
        central = self.centralWidget()
        header = getattr(self, "header_widget", None)

        if header is None:
            return

        bottom = header.y() + header.height()
        self.cover_label.setGeometry(0, 0, central.width(), bottom)

    def _setup_cover(self) -> None:
        frames_dir = self._resource_path(
            Path("assets") / "icons" / "portada_frames"
        )

        if frames_dir.exists():
            files = sorted(frames_dir.glob("*.jpg"))

            if files:
                from PySide6.QtCore import QByteArray

                self._cover_frames = [
                    QByteArray(f.read_bytes()) for f in files
                ]
                self._cover_index = 0
                self.cover_label.setParent(self.header_widget)
                self.cover_label.setGeometry(
                    0,
                    0,
                    self.header_widget.width(),
                    self.header_widget.height(),
                )
                self.cover_label.lower()

                for child in self.header_widget.findChildren(QWidget):
                    if child is not self.cover_label:
                        child.raise_()

                self._cover_timer = QTimer(self)
                self._cover_timer.timeout.connect(self._advance_cover)
                self._cover_timer.start(100)
                self._advance_cover()
                return

        self._use_static_cover()

    def _advance_cover(self) -> None:
        frames = getattr(self, "_cover_frames", None)

        if not frames:
            return

        pix = QPixmap()
        pix.loadFromData(frames[self._cover_index])
        self._cover_index = (self._cover_index + 1) % len(frames)

        if self.cover_label.width() > 10:
            pix = pix.scaled(
                self.cover_label.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )

        self.cover_label.setPixmap(pix)

    def _cover_status(self, status) -> None:
        if int(status) == 6:
            self._cover_failed()

    def _use_static_cover(self) -> None:
        image_path = getattr(self, "_cover_image_path", None)

        if image_path is None or not image_path.exists():
            return

        self._cover_pixmap = QPixmap(str(image_path))
        self.cover_label.setParent(self.centralWidget())
        self._place_cover()
        self.cover_label.lower()
        self._rescale_cover()

    def _cover_failed(self, *args) -> None:
        video = getattr(self, "cover_video", None)

        if video is not None:
            video.hide()

        self._use_static_cover()

    def _rescale_cover(self) -> None:
        pix = getattr(self, "_cover_pixmap", None)

        if pix is None or pix.isNull():
            return

        self.cover_label.setPixmap(
            pix.scaled(
                self.cover_label.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)

        label = getattr(self, "cover_label", None)

        if label is None or label.parent() is None:
            return

        self._place_cover()

        if getattr(self, "_cover_frames", None):
            self._advance_cover()
        elif getattr(self, "_cover_pixmap", None) is not None:
            self._rescale_cover()

    def _add_menu_row(self, icon: QIcon, label: str, handler, menu=None) -> None:
        row = QFrame()
        row.setObjectName("openMenuRow")
        row.setCursor(Qt.CursorShape.PointingHandCursor)
        row.setStyleSheet(
            "QFrame#openMenuRow { background: transparent; } "
            "QFrame#openMenuRow:hover { background: #1a2236; } "
            "QFrame#openMenuRow QLabel { background: transparent; }"
        )

        layout = QHBoxLayout(row)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        icon_label = QLabel()
        icon_label.setPixmap(icon.pixmap(20, 24))
        layout.addWidget(icon_label)

        text_label = QLabel(label)
        text_label.setStyleSheet("color: #eef2fa;")
        layout.addWidget(text_label)
        layout.addStretch()

        row.mouseReleaseEvent = lambda event: (
            (menu or self.open_menu).close(),
            handler(),
        )

        target_menu = menu or self.open_menu
        action = QWidgetAction(target_menu)
        action.setDefaultWidget(row)
        target_menu.addAction(action)

    def _format_icon(self, color: str, label: str) -> QIcon:
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

    def _show_open_menu(self) -> None:
        pos = self.open_file_button.mapToGlobal(
            QPoint(0, self.open_file_button.height())
        )
        self.open_menu.popup(pos)

    def _open_document(self, filter_text: str) -> None:
        path_str, _ = QFileDialog.getOpenFileName(
            self, "Abrir documento", "", filter_text
        )

        if not path_str:
            return

        try:
            content = file_reader.extract_text(Path(path_str))
        except Exception as exc:
            QMessageBox.warning(
                self, "WillpoVoice", f"No se pudo leer el archivo: {exc}"
            )
            return

        self.text_edit.setPlainText(content)
        self._loaded_file_path = path_str
        self._add_to_history(content, file_path=path_str)
        self.statusBar().showMessage(
            f"Documento cargado: {Path(path_str).name}"
        )

    def eventFilter(self, obj, event):
        if obj is self.open_file_button and event.type() == QEvent.Type.HoverEnter:
            self._show_open_menu()

        if obj is self.export_button and event.type() == QEvent.Type.HoverEnter:
            self._show_export_menu()

        if obj in (self.open_menu, self.export_menu) and event.type() == QEvent.Type.Leave:
            QTimer.singleShot(200, lambda menu=obj: self._close_if_out(menu))

        return super().eventFilter(obj, event)

    def _close_if_out(self, menu) -> None:
        if not menu.isVisible():
            return

        if menu.rect().contains(menu.mapFromGlobal(QCursor.pos())):
            return

        menu.close()

    def show_help(self) -> None:
        overlay = SpotlightOverlay(self)
        overlay.setGeometry(0, 0, self.width(), self.height())
        overlay.show()
        overlay.raise_()

        wizard = HelpWizard(
            self,
            targets=[
                None,
                "voices_button",
                "text_edit",
                "rate_slider",
                "speak_button",
                "stop_button",
                "export_button",
                "history_combo",
                "help_button",
            ],
            overlay=overlay,
        )
        wizard.exec()

        overlay.hide()
        overlay.deleteLater()

    def _check_license(self) -> bool:
        state, days_left = license_manager.check_status()

        if state == "licensed":
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
            self.statusBar().showMessage("Licencia activada. Gracias!")
            return True

        return dialog.trial_accepted

    def _apply_theme(self) -> None:
        accent = self.settings.get("accent", "#0E639C")
        dark = self.settings.get("dark_mode", True)

        self.setStyleSheet(build_qss(accent, dark))
        self._apply_titlebar()
        self.theme_button.setText("Modo claro" if dark else "Modo oscuro")

        accent_color = QColor(accent)
        hover = accent_color.lighter(125).name()
        pressed = accent_color.darker(125).name()

        teal_btn = "#4de3b0" if dark else "#0fa87a"
        button_style = (
            "QPushButton {"
            " background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #4de3b0, stop:1 #4a7dff);"
            " color: white;"
            " border: 1px solid rgba(255,255,255,0.08);"
            " border-radius: 10px;"
            " padding: 8px 18px;"
            " font-size: 13px;"
            " font-weight: 700;"
            " }"
            " QPushButton:hover { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #5ff0c0, stop:1 #5a8dff); border: 1px solid rgba(255,255,255,0.18); }"
            " QPushButton:pressed { background: #3a63d8; }"
            " QPushButton:disabled { background: #1a2236; color: #9aa7bd; border: 1px solid #182238; }"
        )

        for btn in (
            self.speak_button,
            self.stop_button,
            self.export_button,
            self.open_file_button,
            self.theme_button,
            self.exit_button,
            self.refresh_voices_button,
            self.clear_history_button,
        ):
            btn.setStyleSheet(button_style)

        hue = accent_color.hslHue()

        if hue < 0:
            hue = 0

        sat = min(accent_color.hslSaturation(), 150)

        if dark:
            group_top = "#161f36"
            group_bottom = "#111828"
            group_border = "#182238"
        else:
            group_top = "#ffffff"
            group_bottom = "#f2f5fa"
            group_border = "#e2e8f2"

        title_color = "#4de3b0" if dark else "#0fa87a"
        group_style = (
            "QGroupBox {"
            f" background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 {group_top}, stop:1 {group_bottom});"
            f" border: 1px solid {group_border};"
            " border-radius: 14px;"
            " margin-top: 18px;"
            " padding: 18px 12px 12px 12px;"
            " }"
            " QGroupBox::title {"
            " subcontrol-origin: margin;"
            " subcontrol-position: top left;"
            " left: 16px;"
            " padding: 0px 6px;"
            " font-weight: 700;"
            f" color: {title_color};"
            " background: transparent;"
            " }"
        )

        self.voice_group.setStyleSheet(group_style)
        self.history_group.setStyleSheet(group_style)

        self._apply_hot_background()

        for chip in self.swatch_buttons:
            active = chip.property("accent") == accent
            chip.setStyleSheet(
                f"background-color:{chip.property('accent')}; "
                f"border-radius:11px; "
                f"border:2px solid {'#ffffff' if active else 'transparent'};"
            )

    def _apply_titlebar(self) -> None:
        try:
            import ctypes

            dark = self.settings.get("dark_mode", True)
            if dark:
                caption = 0x001C0F0A
                textcol = 0x00FAF2EE
            else:
                caption = 0x00FAF7F5
                textcol = 0x0036221A
            hwnd = int(self.winId())
            dwm = ctypes.windll.dwmapi
            dwm.DwmSetWindowAttribute(
                hwnd, 35, ctypes.byref(ctypes.c_uint32(caption)), 4
            )
            dwm.DwmSetWindowAttribute(
                hwnd, 36, ctypes.byref(ctypes.c_uint32(textcol)), 4
            )
        except Exception:
            pass



    def toggle_theme(self) -> None:
        self.settings["dark_mode"] = not self.settings.get("dark_mode", True)
        self._apply_theme()

    def update_counter(self) -> None:
        total = len(self.text_edit.toPlainText())
        self.counter_label.setText(f"{total} caracteres")

    def open_txt(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir archivo de texto",
            "",
            "Archivos de texto (*.txt);;Todos los archivos (*)",
        )

        if not path:
            return

        try:
            content = Path(path).read_text(encoding="utf-8", errors="ignore")
            self.text_edit.setPlainText(content)
            self._loaded_file_path = path
            self._add_to_history(content, file_path=path)
            self.statusBar().showMessage(f"Archivo cargado: {path}")
        except Exception as exc:
            QMessageBox.warning(
                self,
                "Error",
                f"No se pudo leer el archivo:\n{exc}",
            )

    def _load_history(self) -> None:
        raw = self.settings.get("history", [])
        self._history_full = []

        for it in raw:
            if isinstance(it, dict):
                self._history_full.append(it)
            else:
                self._history_full.append(
                    {"content": it, "kind": "text", "label": "Texto manual", "ext": "txt"}
                )

        self.history_combo.clear()

        color_map = {
            "pdf": "#e02020",
            "doc": "#185abd",
            "docx": "#2b7de9",
            "rtf": "#f2a33c",
            "html": "#9b59f6",
            "htm": "#9b59f6",
            "txt": "#4da3ff",
            "md": "#4da3ff",
            "log": "#4da3ff",
            "csv": "#4da3ff",
        }

        label_map = {
            "pdf": "PDF",
            "doc": "DOC",
            "docx": "DOC",
            "rtf": "RTF",
            "html": "WEB",
            "htm": "WEB",
            "txt": "TXT",
            "md": "MD",
            "log": "LOG",
            "csv": "CSV",
        }

        for entry in self._history_full:
            ext = entry.get("ext", "txt").lower()
            color = color_map.get(ext, "#4da3ff")
            badge = label_map.get(ext, ext.upper()[:3])
            icon = self._format_icon(color, badge)
            display = entry.get("label", "Sin titulo")
            self.history_combo.addItem(icon, display)

    def _add_to_history(
        self, text: str, file_path: str | None = None
    ) -> None:
        text = (text or "").strip()

        if not text:
            return

        items = self.settings.get("history", [])

        kind = "text"
        label = "Texto manual"
        ext = "txt"

        if file_path:
            kind = "file"
            p = Path(file_path)
            label = p.name
            ext = p.suffix.lstrip(".").lower() or "txt"

        entry = {
            "content": text,
            "kind": kind,
            "label": label,
            "ext": ext,
        }

        items = [
            it if isinstance(it, dict) else {
                "content": it, "kind": "text", "label": "Texto manual", "ext": "txt"
            }
            for it in items
        ]

        items = [it for it in items if it.get("content") != text]
        items.insert(0, entry)
        self.settings["history"] = items[: self.MAX_HISTORY]
        self._load_history()

    def on_history_selected(self, index: int) -> None:
        if 0 <= index < len(self._history_full):
            entry = self._history_full[index]
            self.text_edit.setPlainText(entry.get("content", ""))

    def clear_history(self) -> None:
        self.settings["history"] = []
        self._load_history()
        self.statusBar().showMessage("Historial limpiado.")

    def open_support(self) -> None:
        QDesktopServices.openUrl(QUrl("https://wa.me/51923073560"))
        self.statusBar().showMessage("Abriendo WhatsApp de soporte...")

    def _cycle_support_color(self) -> None:
        self.support_hue = (self.support_hue + 8) % 360

        border = QColor.fromHsl(self.support_hue, 220, 150).name()
        top = QColor.fromHsl(self.support_hue, 220, 90).name()
        bottom = QColor.fromHsl(self.support_hue, 220, 60).name()

        self.support_button.setStyleSheet(
            "QPushButton {"
            f" background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {top}, stop:1 {bottom});"
            " color: white;"
            f" border: 2px solid {border};"
            " border-radius: 10px;"
            " padding: 6px 12px;"
            " font-weight: 600;"
            " }"
        )

    def _load_voices(self) -> None:
        try:
            self.engine.refresh_voices()
            self.engine.select_natural_voice_if_available()

            voices = self.engine.get_available_voices()

            def sort_key(name: str):
                lower = name.lower()

                if "multilingual" in lower:
                    return (0, lower)

                if "spanish" in lower or "español" in lower or "(es" in lower:
                    return (1, lower)

                if "desktop" in lower:
                    return (2, lower)

                return (3, lower)

            voices = sorted(voices, key=sort_key)

            def group_of(name: str) -> str:
                lower = name.lower()

                if "multilingual" in lower:
                    return "multi"

                if "spanish" in lower or "español" in lower or "(es" in lower:
                    return "es"

                if "desktop" in lower:
                    return "desktop"

                return "en"

            headers = [
                ("multi", "Recomendadas - WillpoVoice Premium"),
                ("es", "Español"),
                ("desktop", "ESTANDAR - funcionan sin internet"),
                ("en", "INGLES"),
            ]

            header_colors = {
                "multi": "#ffd75e",
                "es": "#2ea043",
                "desktop": "#1f6feb",
                "en": "#8c8c96",
            }

            self.voice_combo.clear()
            self._hot_indices = []
            self._group_indices = {"es": [], "desktop": [], "en": []}
            self._fire_frames = [
                self._button_icon(f"multi_{i}.png") for i in range(3)
            ]
            self._header_frames = [
                self._icon_all_modes(f"fire_{i}.png") for i in range(3)
            ]
            self._fire_frame = 0
            self._multi_header_index = None
            self._es_header_index = None

            icons = {
                "es": self._button_icon("dot_es.png"),
                "desktop": self._button_icon("dot_desktop.png"),
                "en": self._button_icon("dot_en.png"),
            }

            flames_active = self._resource_path(
                Path("assets") / "icons" / "flames.gif"
            ).exists()
            spain_path = self._resource_path(Path("assets") / "icons" / "spain.gif")
            spain_active = spain_path.exists()

            tooltip_multi = (
                "Voz Multilingual: compatible con cualquier idioma "
                "y de calidad ultra realista."
            )

            for group_id, header_text in headers:
                members = [v for v in voices if group_of(v) == group_id]

                if not members:
                    continue

                header_index = self.voice_combo.count()
                self.voice_combo.addItem(header_text)

                header_item = self.voice_combo.model().item(header_index)
                header_item.setEnabled(False)

                font = header_item.font()
                font.setBold(True)
                header_item.setFont(font)
                if (flames_active and group_id == "multi") or (
                    spain_active and group_id == "es"
                ):
                    header_item.setForeground(QColor("#ffffff"))
                else:
                    header_item.setForeground(QColor(header_colors[group_id]))

                if group_id == "multi":
                    self._multi_header_index = header_index
                    self.voice_combo.setItemData(
                        header_index,
                        self._header_frames[0],
                        Qt.ItemDataRole.DecorationRole,
                    )
                else:
                    if group_id == "es":
                        self._es_header_index = header_index

                    if group_id == "es" and spain_active:
                        reader = QImageReader(str(spain_path))
                        pix = QPixmap.fromImage(reader.read())
                        pix = pix.scaled(
                            22,
                            15,
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation,
                        )
                        flag_icon = QIcon()
                        flag_icon.addPixmap(pix, QIcon.Mode.Normal)
                        flag_icon.addPixmap(pix, QIcon.Mode.Disabled)
                        flag_icon.addPixmap(pix, QIcon.Mode.Selected)
                        header_icon = flag_icon
                    else:
                        header_icon = icons[group_id]

                    self.voice_combo.setItemData(
                        header_index,
                        header_icon,
                        Qt.ItemDataRole.DecorationRole,
                    )

                for voice in members:
                    index = self.voice_combo.count()
                    self.voice_combo.addItem(voice)

                    if group_id == "multi":
                        self._hot_indices.append(index)
                        self.voice_combo.setItemData(
                            index,
                            self._fire_frames[0],
                            Qt.ItemDataRole.DecorationRole,
                        )
                        self.voice_combo.setItemData(
                            index,
                            tooltip_multi,
                            Qt.ItemDataRole.ToolTipRole,
                        )


                    else:
                        self._group_indices[group_id].append(index)
                        self.voice_combo.setItemData(
                            index,
                            icons[group_id],
                            Qt.ItemDataRole.DecorationRole,
                        )

            self._apply_hot_background()

            self._flames_movie = None
            flames_path = self._resource_path(Path("assets") / "icons" / "flames.gif")

            if flames_path.exists():
                self._flames_movie = QMovie(str(flames_path))
                self._flames_movie.frameChanged.connect(self._update_flames_bg)
                self._flames_movie.start()

            self._spain_movie = None
            spain_path = self._resource_path(Path("assets") / "icons" / "spain.gif")

            if spain_path.exists():
                self._spain_movie = QMovie(str(spain_path))
                self._spain_movie.frameChanged.connect(self._update_spain_bg)
                self._spain_movie.start()

            if getattr(self, "_spain_movie", None) is not None and not getattr(
                self, "_banner_delegate", None
            ):
                self._banner_delegate = BannerDelegate(self)
                self.voice_combo.setItemDelegate(self._banner_delegate)

            self._build_voice_rows(voices)
            last_voice = self.settings.get("last_voice", "")

            if last_voice and last_voice in voices:
                self.voice_combo.setCurrentText(last_voice)
            else:
                preferred = next(
                    (v for v in voices if "AndrewMultilingual" in v), None
                )

                if preferred:
                    self.voice_combo.setCurrentText(preferred)
                    self.engine.select_voice(preferred)
                else:
                    current_voice = self.engine.current_voice_description

                    if current_voice and current_voice in voices:
                        self.voice_combo.setCurrentText(current_voice)

            if voices:
                self.speak_button.setEnabled(True)
                self.statusBar().showMessage(f"Voces disponibles: {len(voices)}")
            else:
                self.speak_button.setEnabled(False)
                self.statusBar().showMessage("No hay voces disponibles.")

        except Exception as exc:
            self.logger.exception("Error cargando voces.")
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudieron cargar las voces:\n{exc}",
            )

    def _filter_voices(self, text: str) -> None:
        q = text.strip().lower()
        view = self.voice_combo.view()
        model = self.voice_combo.model()
        for i in range(self.voice_combo.count()):
            is_header = not model.item(i).isEnabled()
            label = self.voice_combo.itemText(i).lower()
            view.setRowHidden(i, bool(q) and not is_header and q not in label)

    def _preview_voice(self, voice_name):
        self.statusBar().showMessage("Reproduciendo: Hola, esta es mi voz...")
        self._preview_worker = PreviewWorker(
            self.engine.adapter, voice_name, "Hola, esta es mi voz."
        )
        self._preview_worker.start()

    def _sync_row_selection(self):
        current = self.voice_combo.currentText()
        for row, name in getattr(self, "_voice_rows", []):
            row.set_selected(name == current)

    def _toggle_section(self, gid):
        self._section_expanded[gid] = not self._section_expanded.get(gid, False)
        self._update_section_ui(gid)
        self._refresh_rows_visibility()

    def _update_section_ui(self, gid):
        header = self._section_headers.get(gid)
        if header is None:
            return
        title, count, _ = self._section_titles[gid]
        expanded = self._section_expanded.get(gid, False)
        arrow = "▼" if expanded else "▶"
        header.setText(f"{arrow}  {title}  ({count})")

    def _refresh_rows_visibility(self):
        q = (self.voice_search.text() or "").strip().lower()
        for gid, rows in self._section_rows.items():
            expanded = self._section_expanded.get(gid, False)
            any_match = False
            for row in rows:
                match = q in row.voice_name.lower()
                any_match = any_match or match
                if q:
                    row.setVisible(match)
                else:
                    row.setVisible(expanded)
            header = self._section_headers.get(gid)
            if header is not None:
                header.setVisible(True if not q else any_match)

    def _filter_voice_rows(self, text):
        self._refresh_rows_visibility()

    def _voice_photo(self, voice_name, premium):
        low = voice_name.lower()
        for key, fname in PREMIUM_PHOTOS.items():
            if key in low:
                return self._resource_path(Path("assets") / "icons" / fname)
        first = (
            voice_name.replace("Microsoft ", "")
            .split(" ")[0]
            .strip()
            .lower()
        )
        female_names = {
            "carmen", "belen", "mercedes", "flor", "noor", "mar",
            "soledad", "paz", "nieves",
        }
        male_names = {"joshua", "luca", "elias", "noah", "jonah"}
        if first in female_names:
            female = True
        elif first in male_names:
            female = False
        else:
            female = first.endswith("a")
        fname = "face_f.png" if female else "face_m.png"
        return self._resource_path(Path("assets") / "icons" / fname)


    def _build_voice_rows(self, voices):
        container = getattr(self, "voice_rows_container", None)
        if container is None:
            return
        layout = self.voice_rows_layout
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget() if item else None
            if w is not None:
                w.deleteLater()
        self._voice_rows = []
        self._section_rows = {}
        self._section_headers = {}

        premium_keys = set(PREMIUM_PHOTOS)

        def group_of(name):
            lower = name.lower()
            if "multilingual" in lower:
                return "multi"
            if any(k in lower for k in premium_keys):
                return "multi"
            if "spanish" in lower or "español" in lower or "(es" in lower:
                return "es"
            if "desktop" in lower:
                return "desktop"
            return "en"

        seen = set()
        unique_voices = []
        for v in voices:
            if v not in seen:
                seen.add(v)
                unique_voices.append(v)

        sections = [
            ("multi", "RECOMENDADAS - PREMIUM", "#ffd75e"),
            ("es", "ESPANOL", "#8fa0bd"),
            ("desktop", "ESTANDAR - SIN INTERNET", "#8fa0bd"),
            ("en", "INGLES", "#8fa0bd"),
        ]
        for gid, title, color in sections:
            members = [v for v in unique_voices if group_of(v) == gid]
            if not members:
                continue
            header = QLabel(title)
            header.setStyleSheet(
                f"color: {color}; font-size: 10px; font-weight: 700; "
                "letter-spacing: 1px; background: transparent; "
                "padding: 8px 4px 2px 4px;"
            )
            self._section_headers[gid] = header
            layout.addWidget(header)
            rows = []
            for v in members:
                premium = gid == "multi"
                photo = self._voice_photo(v, premium)
                row = VoiceRow(self, v, premium, photo)
                layout.addWidget(row)
                rows.append(row)
                self._voice_rows.append((row, v))
            self._section_rows[gid] = rows
        layout.addStretch()
        self._sync_row_selection()


    def _ensure_voice_panel(self) -> None:
        if getattr(self, "voice_panel", None) is not None:
            return
        from PySide6.QtWidgets import QDockWidget, QScrollArea

        panel = QDockWidget("Voces - WillpoVoice", self)
        panel.setObjectName("voiceDock")
        panel.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetClosable
        )
        panel.setStyleSheet(
            "QDockWidget { background: #0a0f1c; color: #ffd75e; "
            "font-weight: 700; border: none; }"
            "QDockWidget::title { background: #131a2b; padding: 8px; }"
        )
        content = QWidget()
        content.setStyleSheet("background: #0a0f1c;")
        lay = QVBoxLayout(content)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(10)

        search = QLineEdit()
        search.setPlaceholderText("Buscar voces...")
        search.setFixedHeight(34)
        lay.addWidget(search)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        scroll.setStyleSheet(
            "QScrollArea { background: transparent; border: none; }"
        )
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        rows_layout = QVBoxLayout(container)
        rows_layout.setContentsMargins(0, 0, 4, 0)
        rows_layout.setSpacing(6)
        scroll.setWidget(container)
        lay.addWidget(scroll, 1)

        panel.setWidget(content)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, panel)
        panel.setMinimumWidth(340)
        self.voice_panel = panel
        self.voice_search = search
        self.voice_rows_layout = rows_layout
        self.voice_rows_container = container
        self.voice_scroll = scroll
        self._build_voice_rows(self.engine.get_available_voices())
        search.textChanged.connect(self._filter_voice_rows)

    def toggle_voice_dock(self) -> None:
        self._ensure_voice_panel()
        panel = self.voice_panel
        if panel.isVisible():
            panel.hide()
        else:
            panel.setMinimumWidth(320)
            panel.show()
            QTimer.singleShot(
                50,
                lambda: self.resizeDocks(
                    [panel], [340], Qt.Orientation.Horizontal
                ),
            )

    def _preview_voice(self, voice_name):
        self.statusBar().showMessage("Reproduciendo: Hola, esta es mi voz...")
        self._preview_worker = PreviewWorker(
            self.engine.adapter, voice_name, "Hola, esta es mi voz."
        )
        self._preview_worker.start()

    def _sync_row_selection(self):
        current = self.voice_combo.currentText()
        for row, name in getattr(self, "_voice_rows", []):
            row.set_selected(name == current)

    def _filter_voice_rows(self, text):
        q = (text or "").strip().lower()
        for gid, rows in getattr(self, "_section_rows", {}).items():
            any_match = False
            for row in rows:
                match = q in row.voice_name.lower()
                row.setVisible(match)
                any_match = any_match or match
            header = self._section_headers.get(gid)
            if header is not None:
                header.setVisible(any_match)

    def _build_voice_rows(self, voices):
        container = getattr(self, "voice_rows_container", None)
        if container is None:
            return
        layout = self.voice_rows_layout
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget() if item else None
            if w is not None:
                w.deleteLater()
        self._voice_rows = []
        self._section_rows = {}
        self._section_headers = {}

        premium_keys = set(PREMIUM_PHOTOS)

        def group_of(name):
            lower = name.lower()
            if "multilingual" in lower:
                return "multi"
            if any(k in lower for k in premium_keys):
                return "multi"
            if "spanish" in lower or "español" in lower or "(es" in lower:
                return "es"
            if "desktop" in lower:
                return "desktop"
            return "en"

        def photo_for(name):
            low = name.lower()
            for key, fname in PREMIUM_PHOTOS.items():
                if key in low:
                    return self._resource_path(
                        Path("assets") / "icons" / fname
                    )
            first = (
                name.replace("Microsoft ", "")
                .split(" ")[0]
                .strip()
                .lower()
            )
            female_names = {
                "carmen", "belen", "mercedes", "flor", "noor", "mar",
                "soledad", "paz", "nieves", "consuelo", "rocio",
            }
            male_names = {"joshua", "luca", "elias", "noah", "jonah"}
            if first in female_names:
                female = True
            elif first in male_names:
                female = False
            else:
                female = first.endswith("a")
            fname = "face_f.png" if female else "face_m.png"
            return self._resource_path(Path("assets") / "icons" / fname)

        seen = set()
        unique_voices = []
        for v in voices:
            if v not in seen:
                seen.add(v)
                unique_voices.append(v)

        sections = [
            ("multi", "RECOMENDADAS - PREMIUM", "#ffd75e"),
            ("es", "ESPANOL", "#8fa0bd"),
            ("desktop", "ESTANDAR - SIN INTERNET", "#8fa0bd"),
            ("en", "INGLES", "#8fa0bd"),
        ]
        for gid, title, color in sections:
            members = [v for v in unique_voices if group_of(v) == gid]
            if not members:
                continue
            header = QLabel(title)
            header.setStyleSheet(
                f"color: {color}; font-size: 10px; font-weight: 700; "
                "letter-spacing: 1px; background: transparent; "
                "padding: 8px 4px 2px 4px;"
            )
            self._section_headers[gid] = header
            layout.addWidget(header)
            rows = []
            for v in members:
                premium = gid == "multi"
                row = VoiceRow(self, v, premium, photo_for(v))
                layout.addWidget(row)
                rows.append(row)
                self._voice_rows.append((row, v))
            self._section_rows[gid] = rows
        layout.addStretch()
        self._sync_row_selection()

    def refresh_voices(self) -> None:
        self._load_voices()

    def speak_text(self) -> None:
        try:
            text = self.text_edit.toPlainText().strip()

            if not text:
                self.statusBar().showMessage("Escribe un texto antes de reproducir.")
                return

            selected_voice = self.voice_combo.currentText().strip()

            if selected_voice:
                self.engine.select_voice(selected_voice)

            self.engine.set_rate(self.rate_slider.value())
            self.engine.set_volume(self.volume_slider.value())

            self.engine.speak_async(text)
            self._add_to_history(text, file_path=getattr(self, "_loaded_file_path", None))

            self.speaking_dialog = SpeakingDialog(self, self.engine)
            self.speaking_dialog.show()

            self.statusBar().showMessage("Reproduciendo...")

        except Exception as exc:
            self.logger.exception("Error al reproducir texto.")
            QMessageBox.warning(
                self,
                "Error",
                f"No se pudo reproducir el texto:\n{exc}",
            )

    def stop_speech(self) -> None:
        try:
            self.engine.stop()
            self.statusBar().showMessage("Reproducción detenida.")
        except Exception as exc:
            self.logger.exception("Error al detener la reproducción.")
            QMessageBox.warning(
                self,
                "Error",
                f"No se pudo detener la reproducción:\n{exc}",
            )

    def _show_export_menu(self) -> None:
        pos = self.export_button.mapToGlobal(
            QPoint(0, self.export_button.height())
        )
        self.export_menu.popup(pos)

    def _audio_icon(self, color: str, label: str) -> QIcon:
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
        painter.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
        painter.drawText(
            QRect(1, 6, 21, 9), Qt.AlignmentFlag.AlignCenter, label
        )

        painter.setPen(QPen(QColor("white"), 1.6))
        painter.drawEllipse(6, 19, 5, 4)
        painter.drawLine(11, 21, 11, 14)
        painter.drawLine(11, 14, 15, 13)
        painter.end()

        return QIcon(pix)

    def export_mp3(self) -> None:
        import tempfile

        text = self.text_edit.toPlainText().strip()

        if not text:
            self.statusBar().showMessage("Escribe un texto antes de exportar.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar audio MP3",
            "willpovoice_audio.mp3",
            "Archivos MP3 (*.mp3)",
        )

        if not path:
            return

        if not path.lower().endswith(".mp3"):
            path += ".mp3"

        self._mp3_final_path = path
        temp_wav = tempfile.mktemp(suffix=".wav")

        voice = self.voice_combo.currentText().strip()

        self.statusBar().showMessage("Exportando audio...")

        self._start_export_progress()

        self.export_worker = ExportWorker(
            exporter=self.exporter,
            text=text,
            path=temp_wav,
            voice=voice,
            rate=self.rate_slider.value(),
            volume=self.volume_slider.value(),
        )
        self.export_worker.export_ok.connect(self.on_export_ok)
        self.export_worker.export_progress.connect(self._on_export_progress)
        self.export_worker.export_error.connect(self.on_export_error)
        self.export_worker.start()

    def _start_export_progress(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("Exportando")
        dialog.setModal(True)
        dialog.setFixedWidth(380)

        layout = QVBoxLayout(dialog)

        label = QLabel("Exportando audio...")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        row = QHBoxLayout()

        bar = ShineProgressBar()
        bar.setRange(0, 100)
        bar.setTextVisible(False)
        bar.setValue(0)
        row.addWidget(bar, 1)

        pct = QLabel("0%")
        pct.setFixedWidth(48)
        pct.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        row.addWidget(pct)

        layout.addLayout(row)

        dialog.show()

        self.export_progress = dialog
        self._export_bar = bar
        self._export_pct = pct


    def _on_export_progress(self, value: int) -> None:
        bar = getattr(self, "_export_bar", None)

        if bar is not None:
            bar.setValue(value)

        pct = getattr(self, "_export_pct", None)

        if pct is not None:
            pct.setText(f"{value}%")

    def _tick_export_progress(self) -> None:
        bar = getattr(self, "_export_bar", None)

        if bar is None:
            return

        if bar.value() < 90:
            bar.setValue(bar.value() + 2)

        pct = getattr(self, "_export_pct", None)

        if pct is not None:
            pct.setText(f"{bar.value()}%")

    def _finish_export_progress(self) -> None:
        timer = getattr(self, "_export_tick_timer", None)

        if timer is not None:
            timer.stop()
            self._export_tick_timer = None

        bar = getattr(self, "_export_bar", None)

        if bar is not None:
            bar.setValue(100)

        pct = getattr(self, "_export_pct", None)

        if pct is not None:
            pct.setText("100%")

        prog = getattr(self, "export_progress", None)

        if prog is not None:
            prog.close()
            self.export_progress = None

    def export_wav(self) -> None:
        text = self.text_edit.toPlainText().strip()

        if not text:
            self.statusBar().showMessage("Escribe un texto antes de exportar.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar audio WAV",
            "willpovoice_audio.wav",
            "Archivos WAV (*.wav)",
        )

        if not path:
            return

        voice = self.voice_combo.currentText().strip()

        self.statusBar().showMessage("Exportando audio...")

        self._start_export_progress()

        self.export_worker = ExportWorker(
            exporter=self.exporter,
            text=text,
            path=path,
            voice=voice,
            rate=self.rate_slider.value(),
            volume=self.volume_slider.value(),
        )
        self.export_worker.export_ok.connect(self.on_export_ok)
        self.export_worker.export_progress.connect(self._on_export_progress)
        self.export_worker.export_error.connect(self.on_export_error)
        self.export_worker.start()

    def on_export_ok(self, path: str) -> None:
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
                QMessageBox.warning(
                    self, "Error", f"No se pudo convertir a MP3:\n{exc}"
                )
                return

        self._add_to_history(self.text_edit.toPlainText(), file_path=getattr(self, "_loaded_file_path", None))
        self.statusBar().showMessage(f"Audio guardado en: {final_path}")

        QMessageBox.information(
            self,
            "Exportación exitosa",
            f"El audio se guardó correctamente en:\n{final_path}",
        )

    def on_export_error(self, message: str) -> None:
        self._finish_export_progress()

        self.statusBar().showMessage("Error al exportar el audio.")
        QMessageBox.warning(
            self,
            "Error",
            f"No se pudo exportar el audio:\n{message}",
        )

    def closeEvent(self, event) -> None:
        try:
            self.settings["last_voice"] = self.voice_combo.currentText()
            save_settings(self.settings)
            self.engine.stop()
        except Exception:
            self.logger.exception("Error al cerrar la aplicación.")

        event.accept()
















































