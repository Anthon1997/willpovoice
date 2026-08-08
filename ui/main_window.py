from __future__ import annotations

import logging
import sys
from urllib.parse import quote
from pathlib import Path

from PySide6.QtCore import QEvent, Qt, QThread, QTimer, QUrl, Signal, QSize
from PySide6.QtGui import QBrush, QColor, QCursor, QDesktopServices, QIcon, QFont, QLinearGradient, QMovie, QImageReader, QPainter, QPainterPath, QPen, QPixmap, QTransform
from PySide6.QtCore import QPoint, QRect, QRectF, QSize
from PySide6.QtWidgets import (
    QComboBox,
    QColorDialog,
    QDialog,
    QFileDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QProgressDialog,
    QPushButton,
    QGraphicsDropShadowEffect,
    QSlider,
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




from core import file_reader
from core import license_manager


class LicenseDialog(QDialog):
    def __init__(self, parent, machine_id: str, days_left: int):
        super().__init__(parent)
        self.activated_key = ""
        self.trial_accepted = False
        self.machine_id = machine_id

        self.setWindowTitle("WillpoVoice - Licencia")
        self.setModal(True)
        self.setFixedWidth(430)

        layout = QVBoxLayout(self)

        title = QLabel("WillpoVoice")
        title.setStyleSheet("font-size: 20px; font-weight: 700;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        info = QLabel(f"ID de esta maquina: {machine_id}")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(info)

        if days_left >= 0:
            trial = QLabel(f"Prueba gratuita: {days_left} dia(s) restante(s)")
        else:
            trial = QLabel("El periodo de prueba ha terminado.")

        trial.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(trial)

        layout.addWidget(QLabel("Ingresa tu clave de licencia:"))

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

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #e05252;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.error_label)

    def try_activate(self) -> None:
        key = self.key_edit.text()

        if license_manager.validate_key(key, self.machine_id):
            self.activated_key = "".join(key.strip().upper().split())
            self.accept()
        else:
            self.error_label.setText("Clave invalida para esta maquina.")

    def open_whatsapp(self) -> None:
        msg = quote(
            f"Hola, quiero una licencia de WillpoVoice. "
            f"Mi ID de maquina: {self.machine_id}"
        )
        QDesktopServices.openUrl(QUrl(f"https://wa.me/51923073560?text={msg}"))

    def accept_trial(self) -> None:
        self.trial_accepted = True
        self.accept()


class MainWindow(QMainWindow):
    MAX_HISTORY = 10

    def __init__(self):
        super().__init__()

        self.logger = logging.getLogger("naturalvoice_tts.ui")
        self.settings = load_settings()

        self.setWindowTitle("WillpoVoice")
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
            hot_color = QColor("#4a2c10")
            group_colors = {
                "es": QColor("#123524"),
                "desktop": QColor("#1d2f45"),
                "en": QColor("#2b2b33"),
            }
        else:
            hot_color = QColor("#ffe3c2")
            group_colors = {
                "es": QColor("#d7f0e0"),
                "desktop": QColor("#dbe7f5"),
                "en": QColor("#e8e8ee"),
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
        voice_layout = QHBoxLayout(self.voice_group)

        self.voice_combo = QComboBox()
        self.refresh_voices_button = QPushButton("Actualizar voces")
        voice_layout.addWidget(self.voice_combo, 1)
        voice_layout.addWidget(self.refresh_voices_button)
        main_layout.addWidget(self.voice_group)

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
        palette_layout.addWidget(QLabel("Paleta:"))

        for hex_color in PRESET_COLORS:
            chip = QToolButton()
            chip.setFixedSize(22, 22)
            chip.setProperty("accent", hex_color)
            chip.setStyleSheet(
                f"background-color:{hex_color}; border-radius:11px; border:2px solid transparent;"
            )
            chip.clicked.connect(self.on_swatch_clicked)
            palette_layout.addWidget(chip)
            self.swatch_buttons.append(chip)

        self.custom_color_button = QPushButton("Personalizar...")
        self.custom_color_button.clicked.connect(self.pick_custom_color)
        palette_layout.addWidget(self.custom_color_button)

        self.gif_label = QLabel()
        gif_path = self._resource_path(Path("assets") / "icons" / "palette.gif")

        if gif_path.exists():
            self.movie = QMovie(str(gif_path))

            reader = QImageReader(str(gif_path))
            original = reader.size()

            target_height = 28

            if original.height() > 0:
                target_width = int(original.width() * target_height / original.height())
            else:
                target_width = target_height

            self.movie.setScaledSize(QSize(target_width, target_height))
            self.gif_label.setMovie(self.movie)
            self.movie.start()

        palette_layout.addWidget(self.gif_label)
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
            "QMenu { background-color: #0e3a46; border: 1px solid #1f4a55; "
            "border-radius: 6px; padding: 0px; } "
            "QMenu::separator { height: 1px; background: #1f5a68; }"
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
            "QMenu { background-color: #0e3a46; border: 1px solid #1f4a55; "
            "border-radius: 6px; padding: 0px; } "
            "QMenu::separator { height: 1px; background: #1f5a68; }"
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
            "QFrame#openMenuRow:hover { background: #1596a8; } "
            "QFrame#openMenuRow QLabel { background: transparent; }"
        )

        layout = QHBoxLayout(row)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        icon_label = QLabel()
        icon_label.setPixmap(icon.pixmap(20, 24))
        layout.addWidget(icon_label)

        text_label = QLabel(label)
        text_label.setStyleSheet("color: #eaf7f4;")
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
                "voice_combo",
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
        self.theme_button.setText("Modo claro" if dark else "Modo oscuro")

        accent_color = QColor(accent)
        hover = accent_color.lighter(125).name()
        pressed = accent_color.darker(125).name()

        button_style = (
            "QPushButton {"
            f" background-color: {accent_color.name()};"
            " color: white;"
            f" border: 1px solid {pressed};"
            " border-radius: 10px;"
            " padding: 8px 18px;"
            " font-size: 13px;"
            " font-weight: 600;"
            " }"
            f" QPushButton:hover {{ background-color: {hover}; }}"
            f" QPushButton:pressed {{ background-color: {pressed}; }}"
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
            group_bg = QColor.fromHsl(hue, sat, 38).name()
            group_border = QColor.fromHsl(hue, sat, 60).name()
            window_bg = QColor.fromHsl(hue, sat, 30).name()
        else:
            group_bg = "#ffffff"
            group_border = "#000000"
            window_bg = "#f5f6fa"

        group_style = (
            "QGroupBox {"
            f" background-color: {group_bg};"
            f" border: 2px solid {group_border};"
            " border-radius: 10px;"
            " margin-top: 14px;"
            " padding: 14px 8px 8px 8px;"
            " }"
            " QGroupBox::title {"
            " subcontrol-origin: margin;"
            " subcontrol-position: top left;"
            " left: 12px;"
            " padding: 2px 8px;"
            " font-weight: 700;"
            f" color: {group_border};"
            f" background-color: {window_bg};"
            " border-radius: 4px;"
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

    def on_swatch_clicked(self) -> None:
        chip = self.sender()
        self.settings["accent"] = chip.property("accent")
        self._apply_theme()

    def pick_custom_color(self) -> None:
        initial = QColor(self.settings.get("accent", "#0E639C"))
        color = QColorDialog.getColor(initial, self, "Elige tu color corporativo")

        if color.isValid():
            self.settings["accent"] = color.name()
            self._apply_theme()

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
                ("multi", "MULTILINGUAL - hablan cualquier idioma, ultra realistas"),
                ("es", "Español"),
                ("desktop", "ESTANDAR - funcionan sin internet"),
                ("en", "INGLES"),
            ]

            header_colors = {
                "multi": "#ff6a00",
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
















































