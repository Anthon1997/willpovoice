from pathlib import Path
import re, ast

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

# 1. VoiceRow compacto estilo sidebar profesional
new_voicerow = '''class VoiceRow(QFrame):
    def __init__(self, window, voice_name, premium, photo_path=None, parent=None):
        super().__init__(parent)
        self.window = window
        self.voice_name = voice_name
        self.premium = premium
        self._selected = False
        self.setFixedHeight(58)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 8, 8)
        layout.setSpacing(8)

        photo = QLabel()
        photo.setFixedSize(36, 36)
        pix = None
        if photo_path is not None:
            pp = Path(photo_path)
            if pp.exists():
                pix = QPixmap(str(pp)).scaled(
                    36,
                    36,
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation,
                )
        if pix is None or pix.isNull():
            pix = self._initials_pixmap()
        photo.setPixmap(pix)
        photo.setScaledContents(True)
        ring = "2px solid #ffd75e;" if premium else "1px solid #232f4b;"
        photo.setStyleSheet(
            "background: transparent; border-radius: 18px; border: " + ring
        )
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

        self.plus_btn = QPushButton("+")
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
        return n

    def _initials_pixmap(self):
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
        painter.end()
        return pix

    def _apply_style(self):
        if self._selected:
            self.setStyleSheet(
                "VoiceRow { background: #1a2236; border: 1px solid #ffd75e; "
                "border-radius: 12px; }"
            )
            self.plus_btn.setText("✓")
        else:
            self.setStyleSheet(
                "VoiceRow { background: #131a2b; border: 1px solid #232f4b; "
                "border-radius: 12px; }"
            )
            self.plus_btn.setText("+")

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


'''

t = re.sub(
    r"class VoiceRow\(QFrame\):[\s\S]*?(?=\nclass MainWindow)",
    new_voicerow,
    t,
    count=1,
)
print("1. VoiceRow compacto (58px) estilo sidebar.")

# 2. Metodos del panel: secciones planas profesionales
new_methods = '''    def _ensure_voice_panel(self) -> None:
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
            panel.show()
            try:
                self.resizeDocks([panel], [320], Qt.Orientation.Horizontal)
            except Exception:
                pass

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
            ("multi", "RECOMENDADAS - PREMIUM", "#ffd75e"),
            ("es", "ESPANOL", "#8fa0bd"),
            ("desktop", "ESTANDAR - SIN INTERNET", "#8fa0bd"),
            ("en", "INGLES", "#8fa0bd"),
        ]
        for gid, title, color in sections:
            members = [v for v in voices if group_of(v) == gid]
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
                photo = None
                if premium:
                    low = v.lower()
                    for key, fname in PREMIUM_PHOTOS.items():
                        if key in low:
                            photo = self._resource_path(
                                Path("assets") / "icons" / fname
                            )
                            break
                row = VoiceRow(self, v, premium, photo)
                layout.addWidget(row)
                rows.append(row)
                self._voice_rows.append((row, v))
            self._section_rows[gid] = rows
        layout.addStretch()
        self._sync_row_selection()

'''

t = re.sub(
    r"    def _ensure_voice_panel\(self\) -> None:[\s\S]*?(?=    def refresh_voices)",
    new_methods,
    t,
    count=1,
)
print("2. Panel con secciones planas y ancho 320px.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(p.read_text(encoding="utf-8"))
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
