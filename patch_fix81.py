from pathlib import Path
import re, ast

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

print("dock:", "self.voice_dock" in t)
print("voices_button:", "voices_button" in t)
print("toggle:", "def toggle_voice_dock" in t)
print("VoiceRow:", "class VoiceRow" in t)
print("build_rows:", "def _build_voice_rows" in t)

# 1. Imports
if "QDockWidget" not in t:
    t = t.replace("QDialog,", "QDialog,\nQDockWidget,", 1)
if "QScrollArea" not in t:
    t = t.replace("QSlider,", "QSlider,\nQScrollArea,", 1)
if "QPolygon" not in t:
    t = t.replace("QPen, QPixmap, QTransform", "QPen, QPixmap, QPolygon, QTransform", 1)
print("1. Imports verificados.")

# 2. Clases si faltan
if "class VoiceRow" not in t:
    classes = '''
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


class MainWindow(QMainWindow):
'''
    t = t.replace("class MainWindow(QMainWindow):", classes, 1)
    print("2. Clases VoiceRow/PreviewWorker insertadas.")

# 3. Dock si falta
if "self.voice_dock" not in t:
    t = re.sub(
        r"self\.voice_group = QGroupBox\(\"Voz\"\)[\s\S]*?main_layout\.addWidget\(self\.voice_group\)",
        '''self.voice_group = QGroupBox("Voz")
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
        self.voice_dock.setVisible(False)''',
        t,
        count=1,
    )
    print("3. Dock lateral creado.")

# 4. Boton Voces si falta
if "voices_button" not in t:
    t = t.replace(
        '        self.theme_button = QPushButton("Modo claro")',
        '        self.voices_button = QPushButton("Voces")\n'
        '        self.voices_button.setIcon(self._button_icon("multi_0.png"))\n'
        '        self.voices_button.setIconSize(QSize(18, 18))\n'
        '        self.theme_button = QPushButton("Modo claro")',
        1,
    )
    t = t.replace(
        "buttons_layout.addStretch()",
        "buttons_layout.addWidget(self.voices_button)\n        buttons_layout.addStretch()",
        1,
    )
    t = t.replace(
        "self.refresh_voices_button.clicked.connect(self.refresh_voices)",
        "self.refresh_voices_button.clicked.connect(self.refresh_voices)\n"
        "        self.voices_button.clicked.connect(self.toggle_voice_dock)",
        1,
    )
    t = t.replace(
        "self.theme_button,\n            self.exit_button,\n        ):\n            btn.setIconSize",
        "self.theme_button,\n            self.exit_button,\n            self.voices_button,\n        ):\n            btn.setIconSize",
        1,
    )
    print("4. Boton Voces agregado.")

# 5. Metodos si faltan
if "def toggle_voice_dock" not in t:
    t = t.replace(
        "    def refresh_voices(self) -> None:",
        "    def toggle_voice_dock(self) -> None:\n"
        "        self.voice_dock.setVisible(not self.voice_dock.isVisible())\n"
        "\n"
        "    def _preview_voice(self, voice_name):\n"
        "        self.statusBar().showMessage(\"Reproduciendo: Hola, esta es mi voz...\")\n"
        "        self._preview_worker = PreviewWorker(\n"
        "            self.engine.adapter, voice_name, \"Hola, esta es mi voz.\"\n"
        "        )\n"
        "        self._preview_worker.start()\n"
        "\n"
        "    def _sync_row_selection(self):\n"
        "        current = self.voice_combo.currentText()\n"
        "        for row, name in getattr(self, \"_voice_rows\", []):\n"
        "            row.set_selected(name == current)\n"
        "\n"
        "    def _filter_voice_rows(self, text):\n"
        "        q = (self.voice_search.text() or \"\").strip().lower()\n"
        "        for gid, rows in getattr(self, \"_section_rows\", {}).items():\n"
        "            expanded = self._section_expanded.get(gid, False)\n"
        "            any_match = False\n"
        "            for row in rows:\n"
        "                match = q in row.voice_name.lower()\n"
        "                any_match = any_match or match\n"
        "                row.setVisible(match if q else expanded)\n"
        "            header = self._section_headers.get(gid)\n"
        "            if header is not None:\n"
        "                header.setVisible(True if not q else any_match)\n"
        "\n"
        "    def _toggle_section(self, gid):\n"
        "        self._section_expanded[gid] = not self._section_expanded.get(gid, False)\n"
        "        self._update_section_ui(gid)\n"
        "        self._filter_voice_rows(self.voice_search.text())\n"
        "\n"
        "    def _update_section_ui(self, gid):\n"
        "        header = self._section_headers.get(gid)\n"
        "        if header is None:\n"
        "            return\n"
        "        title, count, _ = self._section_titles[gid]\n"
        "        expanded = self._section_expanded.get(gid, False)\n"
        "        arrow = \"▼\" if expanded else \"▶\"\n"
        "        header.setText(f\"{arrow}  {title}  ({count})\")\n"
        "\n"
        "    def _build_voice_rows(self, voices):\n"
        "        container = getattr(self, \"voice_rows_container\", None)\n"
        "        if container is None:\n"
        "            return\n"
        "        layout = self.voice_rows_layout\n"
        "        while layout.count():\n"
        "            item = layout.takeAt(0)\n"
        "            w = item.widget() if item else None\n"
        "            if w is not None:\n"
        "                w.deleteLater()\n"
        "        self._voice_rows = []\n"
        "        self._section_rows = {}\n"
        "        self._section_headers = {}\n"
        "        self._section_titles = {}\n"
        "        self._section_expanded = {}\n"
        "\n"
        "        def group_of(name):\n"
        "            lower = name.lower()\n"
        "            if \"multilingual\" in lower:\n"
        "                return \"multi\"\n"
        "            if \"spanish\" in lower or \"español\" in lower or \"(es\" in lower:\n"
        "                return \"es\"\n"
        "            if \"desktop\" in lower:\n"
        "                return \"desktop\"\n"
        "            return \"en\"\n"
        "\n"
        "        sections = [\n"
        "            (\"multi\", \"★ Recomendadas - WillpoVoice Premium\", \"#ffd75e\", True),\n"
        "            (\"es\", \"español - España\", \"#eef2fa\", False),\n"
        "            (\"desktop\", \"ESTANDAR - sin internet\", \"#eef2fa\", False),\n"
        "            (\"en\", \"INGLES\", \"#eef2fa\", False),\n"
        "        ]\n"
        "        for gid, title, color, expanded in sections:\n"
        "            members = [v for v in voices if group_of(v) == gid]\n"
        "            if not members:\n"
        "                continue\n"
        "            self._section_titles[gid] = (title, len(members), color)\n"
        "            self._section_expanded[gid] = expanded\n"
        "            header = QPushButton()\n"
        "            header.setCursor(Qt.CursorShape.PointingHandCursor)\n"
        "            header.setFixedHeight(42)\n"
        "            if gid == \"multi\":\n"
        "                header.setStyleSheet(\n"
        "                    \"QPushButton { background: #131a2b; border: 1px solid #ffd75e; border-radius: 12px; color: #ffd75e; font-weight: 700; text-align: left; padding: 0 14px; }\"\n"
        "                    \"QPushButton:hover { background: #1a2236; }\"\n"
        "                )\n"
        "            else:\n"
        "                header.setStyleSheet(\n"
        "                    f\"QPushButton {{ background: #131a2b; border: 1px solid #232f4b; border-radius: 12px; color: {color}; font-weight: 700; text-align: left; padding: 0 14px; }}\"\n"
        "                    \"QPushButton:hover { background: #1a2236; }\"\n"
        "                )\n"
        "            header.clicked.connect(lambda _=False, g=gid: self._toggle_section(g))\n"
        "            self._section_headers[gid] = header\n"
        "            layout.addWidget(header)\n"
        "            self._update_section_ui(gid)\n"
        "\n"
        "            rows = []\n"
        "            for v in members:\n"
        "                premium = gid == \"multi\"\n"
        "                photo = None\n"
        "                if premium:\n"
        "                    low = v.lower()\n"
        "                    for key, fname in PREMIUM_PHOTOS.items():\n"
        "                        if key in low:\n"
        "                            photo = self._resource_path(Path(\"assets\") / \"icons\" / fname)\n"
        "                            break\n"
        "                row = VoiceRow(self, v, premium, photo)\n"
        "                layout.addWidget(row)\n"
        "                rows.append(row)\n"
        "                self._voice_rows.append((row, v))\n"
        "            self._section_rows[gid] = rows\n"
        "        layout.addStretch()\n"
        "        self._filter_voice_rows(\"\")\n"
        "        self._sync_row_selection()\n"
        "\n"
        "    def refresh_voices(self) -> None:",
        1,
    )
    print("5. Metodos del panel agregados.")

# 6. Llamada en _load_voices
if "self._build_voice_rows(voices)" not in t:
    t = t.replace(
        '        last_voice = self.settings.get("last_voice", "")',
        '        self._build_voice_rows(voices)\n'
        '        last_voice = self.settings.get("last_voice", "")',
        1,
    )
    print("6. Llamada _build_voice_rows agregada.")

# 7. QSizePolicy si falta
if "QSizePolicy" not in t:
    t = t.replace("QSlider,", "QSlider,\nQSizePolicy,", 1)

p.write_text(t, encoding="utf-8")

try:
    ast.parse(p.read_text(encoding="utf-8"))
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR SINTAXIS:", e.lineno, e.msg)
