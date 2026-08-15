from pathlib import Path
import re

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

# 0. Import QSizePolicy
if "QSizePolicy" not in t:
    t = t.replace("QSlider,", "QSlider,\nQSizePolicy,", 1)
    print("0. QSizePolicy importado.")

# 1. Scroll con altura profesional
t = t.replace(
    "voice_layout.addWidget(self.voice_scroll, 1)",
    "self.voice_scroll.setMinimumHeight(380)\n"
    "        self.voice_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)\n"
    "        voice_layout.addWidget(self.voice_scroll, 1)",
    1,
)
print("1. Scroll con altura minima 380.")

# 2. VoiceRow con altura fija (sin recortes)
new_voicerow = '''class VoiceRow(QFrame):
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
        self.play_btn.setText("▶")
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

t = re.sub(
    r"class VoiceRow\(QFrame\):[\s\S]*?(?=\nclass MainWindow)",
    new_voicerow,
    t,
    count=1,
)
print("2. VoiceRow con altura fija 64px.")

# 3. Metodos con secciones colapsables
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

t = re.sub(
    r"    def _preview_voice\(self, voice_name\):[\s\S]*?(?=    def refresh_voices)",
    new_methods,
    t,
    count=1,
)
print("3. Secciones colapsables con flecha ▼/▶.")

p.write_text(t, encoding="utf-8")
print("Listo.")
