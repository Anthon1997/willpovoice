from __future__ import annotations

import logging
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QThread, QTimer, QUrl, Signal, QSize
from PySide6.QtGui import QBrush, QColor, QDesktopServices, QIcon, QMovie, QImageReader, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QColorDialog,
    QDialog,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressDialog,
    QPushButton,
    QGraphicsDropShadowEffect,
    QSlider,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from app.config import load_settings, save_settings
from core.audio_exporter import AudioExporter
from core.tts_engine import TTSEngine
from ui.theme import PRESET_COLORS, build_qss


class ExportWorker(QThread):
    export_ok = Signal(str)
    export_error = Signal(str)

    def __init__(self, exporter, text, path, voice, rate, volume):
        super().__init__()
        self.exporter = exporter
        self.text = text
        self.path = path
        self.voice = voice
        self.rate = rate
        self.volume = volume

    def run(self):
        try:
            import pythoncom
            pythoncom.CoInitialize()
        except Exception:
            pass

        try:
            result = self.exporter.save_text_to_wav(
                text=self.text,
                output_path=self.path,
                voice_query=self.voice,
                rate=self.rate,
                volume=self.volume,
            )
            self.export_ok.emit(str(result))
        except Exception as exc:
            self.export_error.emit(str(exc))


class SpeakingDialog(QDialog):
    def __init__(self, parent, engine):
        super().__init__(parent)
        self.engine = engine
        self.setWindowTitle("Reproduciendo")
        self.setModal(False)
        self.setFixedWidth(260)

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

        self.info_label = QLabel("Reproduciendo texto...")
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

        if state == 1:
            self.timer.stop()
            self.close()

    def stop_and_close(self):
        try:
            self.engine.stop()
        except Exception:
            pass

        self.timer.stop()
        self.close()


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

        header_layout = QHBoxLayout()

        logo_label = QLabel()
        logo_path = self._resource_path(Path("assets") / "icons" / "logo.png")

        if not logo_path.exists():
            logo_path = self._resource_path(Path("assets") / "icons" / "icon.ico")

        if logo_path.exists():
            pixmap = QPixmap(str(logo_path)).scaledToHeight(
                48, Qt.TransformationMode.SmoothTransformation
            )
            logo_label.setPixmap(pixmap)

        header_layout.addWidget(logo_label)

        title_layout = QVBoxLayout()

        title_label = QLabel("WillpoVoice")
        title_label.setStyleSheet("font-size: 22px; font-weight: 700;")

        subtitle_label = QLabel("Convierte texto en voz con voces naturales")
        subtitle_label.setStyleSheet("font-size: 12px;")

        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        main_layout.addLayout(header_layout)

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

        self.export_button = QPushButton("Guardar WAV")
        self.export_button.setIcon(self._button_icon("save.png"))

        self.open_file_button = QPushButton("Abrir TXT")
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
        self.export_button.clicked.connect(self.export_wav)
        self.open_file_button.clicked.connect(self.open_txt)
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
            self.statusBar().showMessage(f"Archivo cargado: {path}")
        except Exception as exc:
            QMessageBox.warning(
                self,
                "Error",
                f"No se pudo leer el archivo:\n{exc}",
            )

    def _load_history(self) -> None:
        self._history_full = list(self.settings.get("history", []))
        self.history_combo.clear()

        for item in self._history_full:
            display = item if len(item) <= 80 else item[:77] + "..."
            self.history_combo.addItem(display)

    def _add_to_history(self, text: str) -> None:
        items = self.settings.get("history", [])

        if text in items:
            items.remove(text)

        items.insert(0, text)
        self.settings["history"] = items[: self.MAX_HISTORY]
        self._load_history()

    def on_history_selected(self, index: int) -> None:
        if 0 <= index < len(self._history_full):
            self.text_edit.setPlainText(self._history_full[index])

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

            self.voice_combo.clear()
            self.voice_combo.addItems(voices)

            self._hot_indices = []
            self._group_indices = {"es": [], "desktop": [], "en": []}
            self._fire_frames = [
                self._button_icon(f"fire_{i}.png") for i in range(3)
            ]
            self._fire_frame = 0

            dot_es = self._button_icon("dot_es.png")
            dot_desktop = self._button_icon("dot_desktop.png")
            dot_en = self._button_icon("dot_en.png")

            for i in range(self.voice_combo.count()):
                lower = self.voice_combo.itemText(i).lower()

                if "multilingual" in lower:
                    self._hot_indices.append(i)
                    self.voice_combo.setItemData(
                        i, self._fire_frames[0], Qt.ItemDataRole.DecorationRole
                    )
                elif "spanish" in lower or "español" in lower or "(es" in lower:
                    self._group_indices["es"].append(i)
                    self.voice_combo.setItemData(
                        i, dot_es, Qt.ItemDataRole.DecorationRole
                    )
                elif "desktop" in lower:
                    self._group_indices["desktop"].append(i)
                    self.voice_combo.setItemData(
                        i, dot_desktop, Qt.ItemDataRole.DecorationRole
                    )
                else:
                    self._group_indices["en"].append(i)
                    self.voice_combo.setItemData(
                        i, dot_en, Qt.ItemDataRole.DecorationRole
                    )

            self._apply_hot_background()

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
            self._add_to_history(text)

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

        self.export_progress = QProgressDialog("Exportando audio...", None, 0, 0, self)
        self.export_progress.setWindowTitle("Exportando")
        self.export_progress.setModal(True)
        self.export_progress.show()

        self.export_worker = ExportWorker(
            exporter=self.exporter,
            text=text,
            path=path,
            voice=voice,
            rate=self.rate_slider.value(),
            volume=self.volume_slider.value(),
        )
        self.export_worker.export_ok.connect(self.on_export_ok)
        self.export_worker.export_error.connect(self.on_export_error)
        self.export_worker.start()

    def on_export_ok(self, path: str) -> None:
        if getattr(self, "export_progress", None):
            self.export_progress.close()
            self.export_progress = None

        self._add_to_history(self.text_edit.toPlainText().strip())
        self.statusBar().showMessage(f"Audio guardado en: {path}")

        QMessageBox.information(
            self,
            "Exportación exitosa",
            f"El audio se guardó correctamente en:\n{path}",
        )

    def on_export_error(self, message: str) -> None:
        if getattr(self, "export_progress", None):
            self.export_progress.close()
            self.export_progress = None

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


















