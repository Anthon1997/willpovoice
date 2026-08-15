from pathlib import Path
import ast

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

# 1. Quitar Voces de la barra inferior
old = "buttons_layout.addWidget(self.voices_button)\n        buttons_layout.addStretch()"
if old in t:
    t = t.replace(old, "buttons_layout.addStretch()", 1)
    print("1. Voces fuera de la barra inferior.")

# 2. Boton Voces en la esquina superior derecha del header
old = '''        self.voices_button = QPushButton("Voces")
        self.voices_button.setIcon(self._button_icon("multi_0.png"))
        self.voices_button.setIconSize(QSize(18, 18))'''
new = '''        self.voices_button = QPushButton("Voces")
        self.voices_button.setIcon(self._button_icon("multi_0.png"))
        self.voices_button.setIconSize(QSize(18, 18))
        self.header_widget.layout().addWidget(
            self.voices_button, 0, Qt.AlignmentFlag.AlignVCenter
        )
        self.voices_button.setStyleSheet(
            "QPushButton { background: #131a2b; border: 1px solid #ffd75e; "
            "border-radius: 10px; color: #ffd75e; font-weight: 700; "
            "padding: 8px 16px; }"
            "QPushButton:hover { background: #1a2236; }"
        )'''
if old in t:
    t = t.replace(old, new, 1)
    print("2. Boton Voces arriba a la derecha, estilo dorado.")

# 3. Ancho minimo del dock
old = "self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, panel)"
new = (
    "self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, panel)\n"
    "        panel.setMinimumWidth(320)"
)
if old in t and "panel.setMinimumWidth(320)" not in t:
    t = t.replace(old, new, 1)
    print("3. Dock con ancho minimo 320px.")

# 4. Toggle con resize diferido (garantiza 320px)
old = '''    def toggle_voice_dock(self) -> None:
        self._ensure_voice_panel()
        panel = self.voice_panel
        if panel.isVisible():
            panel.hide()
        else:
            panel.show()
            try:
                self.resizeDocks([panel], [320], Qt.Orientation.Horizontal)
            except Exception:
                pass'''
new = '''    def toggle_voice_dock(self) -> None:
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
                    [panel], [320], Qt.Orientation.Horizontal
                ),
            )'''
if old in t:
    t = t.replace(old, new, 1)
    print("4. Toggle con ancho garantizado.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(p.read_text(encoding="utf-8"))
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
