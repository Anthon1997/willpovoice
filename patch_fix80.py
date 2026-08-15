from pathlib import Path
import re, ast

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

# 1. Imports: QDockWidget y QPolygon
if "QDockWidget" not in t:
    t = t.replace("QDialog,", "QDialog,\nQDockWidget,", 1)
    print("1. QDockWidget importado.")
if "QPolygon" not in t:
    t = t.replace("QPen, QPixmap, QTransform", "QPen, QPixmap, QPolygon, QTransform", 1)
    print("1b. QPolygon importado.")

# 2. Mover el panel de voces a un dock lateral
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
print("2. Panel de voces movido a dock lateral.")

# 3. Boton "Voces" en la barra de botones
if "voices_button" not in t:
    t = t.replace(
        'self.theme_button = QPushButton("Modo claro")',
        'self.voices_button = QPushButton("Voces")\n'
        '        self.voices_button.setIcon(self._button_icon("multi_0.png"))\n'
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
    print("3. Boton Voces agregado y conectado.")

# 4. Metodo toggle
if "def toggle_voice_dock" not in t:
    t = t.replace(
        "    def refresh_voices(self) -> None:",
        "    def toggle_voice_dock(self) -> None:\n"
        "        self.voice_dock.setVisible(not self.voice_dock.isVisible())\n"
        "\n"
        "    def refresh_voices(self) -> None:",
        1,
    )
    print("4. toggle_voice_dock agregado.")

# 5. Play con icono dibujado (no texto)
t = t.replace(
    '        self.play_btn.setText("▶")',
    "        play_pix = QPixmap(18, 18)\n"
    "        play_pix.fill(Qt.GlobalColor.transparent)\n"
    "        painter_play = QPainter(play_pix)\n"
    "        painter_play.setRenderHint(QPainter.RenderHint.Antialiasing)\n"
    "        painter_play.setBrush(QColor(\"#4a7dff\"))\n"
    "        painter_play.setPen(Qt.PenStyle.NoPen)\n"
    "        painter_play.drawPolygon(QPolygon([QPoint(4, 2), QPoint(16, 9), QPoint(4, 16)]))\n"
    "        painter_play.end()\n"
    "        self.play_btn.setIcon(QIcon(play_pix))\n"
    "        self.play_btn.setIconSize(QSize(18, 18))",
    1,
)
print("5. Icono play dibujado en cada fila.")

# 6. Fila completa clickeable para seleccionar
t = t.replace(
    "        layout.addWidget(photo)\n        self._apply_style()",
    "        layout.addWidget(photo)\n"
    "        self._apply_style()\n"
    "        self.mouseReleaseEvent = lambda event: self._select()",
    1,
)
print("6. Fila completa selecciona voz al clic.")

# 7. Tour apunta al boton Voces
t = t.replace('"voice_combo",', '"voices_button",', 1)
print("7. Tour actualizado.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(p.read_text(encoding="utf-8"))
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR SINTAXIS:", e.lineno, e.msg)
