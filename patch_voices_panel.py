from pathlib import Path
import re, shutil

base = Path(__file__).resolve().parent
proj = Path(".")

# 1. Copiar retratos desde el proyecto Android si existen
src_dir = Path(r"C:\Users\antho\AndroidStudioProjects\WillpoVoice\app\src\main\res\drawable")
dst_dir = proj / "assets" / "icons"
for f in ["ms_andrew.png","ms_ava.png","ms_brian.png","ms_emma.png","ms_florian.png",
          "ms_giuseppe.png","ms_hyunsu.png","ms_remy.png","ms_seraphina.png",
          "face_f.png","face_m.png"]:
    s = src_dir / f
    if s.exists():
        shutil.copy(s, dst_dir / f)
        print(f"Foto copiada: {f}")

p = proj / "ui" / "main_window.py"
t = p.read_text(encoding="utf-8")

# 2. Import QScrollArea
if "QScrollArea" not in t:
    t = t.replace("QProgressBar,", "QProgressBar,\nQScrollArea,", 1)
    print("Import QScrollArea agregado.")

# 3. Clases nuevas antes de MainWindow
new_classes = '''
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
}


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
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)

        self.plus_btn = QPushButton("+")
        self.plus_btn.setFixedSize(44, 44)
        if premium:
            self.plus_btn.setStyleSheet(
                "QPushButton { background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #ffd75e, stop:1 #f79009); color: white; border: none; border-radius: 22px; font-size: 20px; font-weight: 700; }"
            )
        else:
            self.plus_btn.setStyleSheet(
                "QPushButton { background: #1a2236; color: white; border: none; border-radius: 22px; font-size: 20px; font-weight: 700; }"
            )
        self.plus_btn.clicked.connect(self._select)
        layout.addWidget(self.plus_btn)

        texts_widget = QWidget()
        texts_widget.setStyleSheet("background: transparent;")
        texts = QVBoxLayout(texts_widget)
        texts.setContentsMargins(0, 0, 0, 0)
        texts.setSpacing(2)
        name_label = QLabel(self._display_name())
        name_label.setStyleSheet("color: #eef2fa; font-size: 14px; font-weight: 700; background: transparent;")
        sub_label = QLabel("WillpoVoice Premium" if premium else "Voz estandar")
        sub_label.setStyleSheet(
            ("color: #ffd75e;" if premium else "color: #9aa7bd;")
            + " font-size: 11px; background: transparent;"
        )
        texts.addWidget(name_label)
        texts.addWidget(sub_label)
        layout.addWidget(texts_widget, 1)

        self.play_btn = QPushButton()
        self.play_btn.setFixedSize(36, 36)
        self.play_btn.setToolTip("Hola, esta es mi voz")
        self.play_btn.setText("\\u25B6")
        self.play_btn.setStyleSheet(
            "QPushButton { background: #1a2236; border: none; border-radius: 18px; color: #4a7dff; font-size: 15px; font-weight: 700; }"
            "QPushButton:hover { background: #232f4b; }"
        )
        self.play_btn.clicked.connect(self._preview)
        layout.addWidget(self.play_btn)

        photo = QLabel()
        photo.setFixedSize(44, 44)
        pix = None
        if photo_path is not None:
            pp = Path(photo_path)
            if pp.exists():
                pix = QPixmap(str(pp)).scaled(
                    44, 44,
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation,
                )
        if pix is None or pix.isNull():
            pix = self._initials_pixmap()
        photo.setPixmap(pix)
        photo.setScaledContents(True)
        photo.setStyleSheet("background: transparent;")
        layout.addWidget(photo)
        self._apply_style()

    def _display_name(self):
        n = self.voice_name.replace("Microsoft ", "")
        if "Multilingual" in n:
            first = n.split("Multilingual")[0].strip()
            return f"{first} (Multilingual)"
        return n

    def _initials_pixmap(self):
        pix = QPixmap(44, 44)
        pix.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor("#1a2236"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, 44, 44)
        painter.setPen(QColor("#4a7dff"))
        painter.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        painter.drawText(QRect(0, 0, 44, 44), Qt.AlignmentFlag.AlignCenter, self.voice_name[:1].upper())
        painter.end()
        return pix

    def _apply_style(self):
        if self._selected or self.premium:
            border = "2px solid #ffd75e" if self._selected else "1px solid #ffd75e"
        else:
            border = "1px solid #232f4b"
        self.setStyleSheet(
            "VoiceRow { background: #131a2b; border: " + border + "; border-radius: 14px; }"
        )

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
        self.window.statusBar().showMessage(f"Voz seleccionada: {self.voice_name}")

    def _preview(self):
        self.window._preview_voice(self.voice_name)


class MainWindow(QMainWindow):
'''

t = t.replace("class MainWindow(QMainWindow):", new_classes, 1)
print("Clases VoiceRow y PreviewWorker agregadas.")

# 4. Nuevo layout del grupo Voz
new_voice_block = '''self.voice_group = QGroupBox("Voz")
        voice_layout = QVBoxLayout(self.voice_group)
        top_row = QHBoxLayout()
        self.voice_search = QLineEdit()
        self.voice_search.setPlaceholderText("Buscar voces...")
        self.voice_search.textChanged.connect(self._filter_voice_rows)
        top_row.addWidget(self.voice_search, 1)
        self.refresh_voices_button = QPushButton("Actualizar voces")
        top_row.addWidget(self.refresh_voices_button)
        voice_layout.addLayout(top_row)
        self.voice_combo = QComboBox()
        self.voice_combo.hide()
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
        voice_layout.addWidget(self.voice_scroll, 1)
        main_layout.addWidget(self.voice_group)'''

t = re.sub(
    r"self\.voice_group = QGroupBox\(\"Voz\"\)[\s\S]*?main_layout\.addWidget\(self\.voice_group\)",
    new_voice_block,
    t,
    count=1,
)
print("Grupo Voz reconstruido con panel de filas.")

# 5. Metodos nuevos en MainWindow
new_methods = '''    def _preview_voice(self, voice_name):
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
        q = text.strip().lower()
        for row, name in getattr(self, "_voice_rows", []):
            row.setVisible(not q or q in name.lower())
        layout = self.voice_rows_layout
        for i in range(layout.count()):
            item = layout.itemAt(i)
            w = item.widget() if item else None
            if isinstance(w, QLabel):
                j = i + 1
                any_vis = False
                while j < layout.count():
                    it2 = layout.itemAt(j)
                    nw = it2.widget() if it2 else None
                    if isinstance(nw, QLabel):
                        break
                    if nw is not None and nw.isVisible():
                        any_vis = True
                        break
                    j += 1
                w.setVisible(any_vis or not q)

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

        def group_of(name):
            lower = name.lower()
            if "multilingual" in lower:
                return "multi"
            if "spanish" in lower or "español" in lower or "(es" in lower:
                return "es"
            if "desktop" in lower:
                return "desktop"
            return "en"

        sections = [
            ("multi", "★ Recomendadas - WillpoVoice Premium", "#ffd75e"),
            ("es", "español - España", "#eef2fa"),
            ("desktop", "ESTANDAR - funcionan sin internet", "#eef2fa"),
            ("en", "INGLES", "#eef2fa"),
        ]
        for gid, title, color in sections:
            members = [v for v in voices if group_of(v) == gid]
            if not members:
                continue
            header = QLabel(f"{title}  ({len(members)})")
            header.setStyleSheet(
                f"color: {color}; font-size: 13px; font-weight: 700; background: transparent;"
            )
            layout.addWidget(header)
            for v in members:
                premium = gid == "multi"
                photo = None
                if premium:
                    low = v.lower()
                    for key, fname in PREMIUM_PHOTOS.items():
                        if key in low:
                            photo = self._resource_path(Path("assets") / "icons" / fname)
                            break
                row = VoiceRow(self, v, premium, photo)
                layout.addWidget(row)
                self._voice_rows.append((row, v))
        layout.addStretch()
        self._sync_row_selection()

    def refresh_voices(self) -> None:'''

t = t.replace("    def refresh_voices(self) -> None:", new_methods, 1)
print("Metodos de filas, preview y filtro agregados.")

# 6. Construir filas al cargar voces
t = t.replace(
    "self._apply_hot_background()\n        self._flames_movie = None",
    "self._apply_hot_background()\n        self._build_voice_rows(voices)\n        self._flames_movie = None",
    1,
)
print("Filas construidas al cargar voces.")

p.write_text(t, encoding="utf-8")
print("Listo. Apartado de voces estilo movil aplicado.")
