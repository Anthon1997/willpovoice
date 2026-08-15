from pathlib import Path
import re, ast

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

print("--- marcadores ---")
for s in ["class VoiceRow", "def _build_voice_rows", "self._build_voice_rows(voices)",
          "voice_dock", "self.voices_button = QPushButton", "addWidget(self.voices_button)",
          "voices_button.clicked.connect", "def toggle_voice_dock", "QDockWidget"]:
    print(f"{s}: {s in t}")

VOICEROW = '''
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


class VoiceRow(QFrame):
    def __init__(self, window, voice_name, premium, photo_path=None, parent=None):
        super().__init__(parent)
        self.window = window
        self.voice_name = voice_name
        self.premium = premium
        self._selected = False
        self.setFixedHeight(64)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
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
        name_label.setStyleSheet(
            "color: #eef2fa; font-size: 14px; font-weight: 700; background: transparent;"
        )
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
        play_pix = QPixmap(18, 18)
        play_pix.fill(Qt.GlobalColor.transparent)
        painter_play = QPainter(play_pix)
        painter_play.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter_play.setBrush(QColor("#4a7dff"))
        painter_play.setPen(Qt.PenStyle.NoPen)
        painter_play.drawPolygon(QPolygon([QPoint(4, 2), QPoint(16, 9), QPoint(4, 16)]))
        painter_play.end()
        self.play_btn.setIcon(QIcon(play_pix))
        self.play_btn.setIconSize(QSize(18, 18))
        self.play_btn.setStyleSheet(
            "QPushButton { background: #1a2236; border: none; border-radius: 18px; }"
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
                    44,
                    44,
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation,
                )
        if pix is None or pix.isNull():
            pix = self._initials_pixmap()
        photo.setPixmap(pix)
        photo.setScaledContents(True)
        photo.setStyleSheet("background: transparent; border-radius: 22px;")
        layout.addWidget(photo)
        self._apply_style()
        self.mouseReleaseEvent = lambda event: self._select()

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
        if self._selected:
            border = "2px solid #ffd75e"
        elif self.premium:
            border = "1px solid #ffd75e"
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


'''

METHODS = '''    def toggle_voice_dock(self) -> None:
        self.voice_dock.setVisible(not self.voice_dock.isVisible())

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
        for gid, rows in getattr(self, "_section_rows", {}).items():
            expanded = self._section_expanded.get(gid, False)
            any_match = False
            for row in rows:
                match = q in row.voice_name.lower()
                any_match = any_match or match
                row.setVisible(match if q else expanded)
            header = self._section_headers.get(gid)
            if header is not None:
                header.setVisible(True if not q else any_match)

    def _filter_voice_rows(self, text):
        self._refresh_rows_visibility()

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
        self._section_titles = {}
        self._section_expanded = {}

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
            ("multi", "★ Recomendadas - WillpoVoice Premium", "#ffd75e", True),
            ("es", "español - España", "#eef2fa", False),
            ("desktop", "ESTANDAR - sin internet", "#eef2fa", False),
            ("en", "INGLES", "#eef2fa", False),
        ]
        for gid, title, color, expanded in sections:
            members = [v for v in voices if group_of(v) == gid]
            if not members:
                continue
            self._section_titles[gid] = (title, len(members), color)
            self._section_expanded[gid] = expanded
            header = QPushButton()
            header.setCursor(Qt.CursorShape.PointingHandCursor)
            header.setFixedHeight(42)
            if gid == "multi":
                header.setStyleSheet(
                    "QPushButton { background: #131a2b; border: 1px solid #ffd75e; border-radius: 12px; color: #ffd75e; font-weight: 700; text-align: left; padding: 0 14px; }"
                    "QPushButton:hover { background: #1a2236; }"
                )
            else:
                header.setStyleSheet(
                    f"QPushButton {{ background: #131a2b; border: 1px solid #232f4b; border-radius: 12px; color: {color}; font-weight: 700; text-align: left; padding: 0 14px; }}"
                    "QPushButton:hover { background: #1a2236; }"
                )
            header.clicked.connect(lambda _=False, g=gid: self._toggle_section(g))
            self._section_headers[gid] = header
            layout.addWidget(header)
            self._update_section_ui(gid)

            rows = []
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
                rows.append(row)
                self._voice_rows.append((row, v))
            self._section_rows[gid] = rows
        layout.addStretch()
        self._refresh_rows_visibility()
        self._sync_row_selection()

'''

DOCK = '''
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
'''

# 0. Imports
if "QDockWidget" not in t:
    t = t.replace("QDialog,", "QDialog,\nQDockWidget,", 1)
    print("+ import QDockWidget")
if "QScrollArea" not in t:
    t = t.replace("QSlider,", "QSlider,\nQScrollArea,", 1)
    print("+ import QScrollArea")
if "QSizePolicy" not in t:
    t = t.replace("QSlider,", "QSlider,\nQSizePolicy,", 1)
    print("+ import QSizePolicy")
if "QPolygon" not in t:
    t = t.replace("QPen, QPixmap, QTransform", "QPen, QPixmap, QPolygon, QTransform", 1)
    print("+ import QPolygon")
if "class PreviewWorker" not in t:
    pw = '''class PreviewWorker(QThread):
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


'''
    t = t.replace("class MainWindow(QMainWindow):", pw + "class MainWindow(QMainWindow):", 1)
    print("+ PreviewWorker")

# 1. Clase VoiceRow
if "class VoiceRow" not in t:
    t = t.replace("class MainWindow(QMainWindow):", VOICEROW + "class MainWindow(QMainWindow):", 1)
    print("+ VoiceRow")

# 2. Metodos
if "def _build_voice_rows" not in t:
    t = t.replace("    def refresh_voices(self) -> None:", METHODS + "    def refresh_voices(self) -> None:", 1)
    print("+ metodos")
elif "def toggle_voice_dock" not in t:
    t = t.replace("    def refresh_voices(self) -> None:", "    def toggle_voice_dock(self) -> None:\n        self.voice_dock.setVisible(not self.voice_dock.isVisible())\n\n    def refresh_voices(self) -> None:", 1)
    print("+ toggle")

# 3. Llamada
if "self._build_voice_rows(voices)" not in t:
    t = t.replace(
        '        last_voice = self.settings.get("last_voice", "")',
        '        self._build_voice_rows(voices)\n        last_voice = self.settings.get("last_voice", "")',
        1,
    )
    print("+ llamada _build_voice_rows")

# 4. Dock
if "voice_dock" not in t:
    anchor = "self.voice_scroll.setWidget(self.voice_rows_container)"
    if anchor in t:
        t = t.replace(anchor, anchor + DOCK, 1)
        print("+ dock")
    else:
        print("AVISO: sin anchor para dock")

# 5. Boton Voces: creacion
if "self.voices_button = QPushButton" not in t:
    idx = t.find("self.theme_button = QPushButton")
    if idx != -1:
        ls = t.rfind("\n", 0, idx) + 1
        ind = t[ls:idx]
        insert = (
            ind + 'self.voices_button = QPushButton("Voces")\n'
            + ind + 'self.voices_button.setIcon(self._button_icon("multi_0.png"))\n'
            + ind + 'self.voices_button.setIconSize(QSize(18, 18))\n'
        )
        t = t[:ls] + insert + t[ls:]
        print("+ creacion voices_button")

# 6. Boton en layout
if "addWidget(self.voices_button)" not in t:
    idx = t.find("buttons_layout.addStretch()")
    if idx != -1:
        ls = t.rfind("\n", 0, idx) + 1
        ind = t[ls:idx]
        t = t[:ls] + ind + "buttons_layout.addWidget(self.voices_button)\n" + t[ls:]
        print("+ voices_button en layout")

# 7. Conexion
if "voices_button.clicked.connect" not in t:
    idx = t.find("self.refresh_voices_button.clicked.connect(self.refresh_voices)")
    if idx != -1:
        end = t.find("\n", idx)
        ls = t.rfind("\n", 0, idx) + 1
        ind = t[ls:idx]
        t = t[: end + 1] + ind + "self.voices_button.clicked.connect(self.toggle_voice_dock)\n" + t[end + 1 :]
        print("+ conexion voices_button")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(p.read_text(encoding="utf-8"))
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR SINTAXIS:", e.lineno, e.msg)
