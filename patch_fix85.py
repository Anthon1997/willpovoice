from pathlib import Path
import re, ast

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

# 1. Eliminar _ensure_voice_dock si existe
t = re.sub(
    r"    def _ensure_voice_dock\(self\) -> None:[\s\S]*?\n    def toggle_voice_dock",
    "    def toggle_voice_dock",
    t,
    count=1,
)

new_methods = '''    def _ensure_voice_panel(self) -> None:
        dock = getattr(self, "voice_dock", None)
        if dock is not None:
            try:
                self.removeDockWidget(dock)
                dock.deleteLater()
            except Exception:
                pass
            self.voice_dock = None
        if getattr(self, "voice_panel", None) is not None:
            return
        from PySide6.QtWidgets import QScrollArea, QDialog

        panel = QDialog(self)
        panel.setWindowTitle("Voces - WillpoVoice")
        panel.setModal(False)
        panel.setWindowFlags(
            Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint
        )
        panel.setStyleSheet("background: #0a0f1c;")
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(10, 10, 10, 10)
        lay.setSpacing(8)

        search = getattr(self, "voice_search", None)
        if search is None:
            search = QLineEdit()
            search.setPlaceholderText("Buscar voces...")
            search.textChanged.connect(self._filter_voice_rows)
            self.voice_search = search
        top = QHBoxLayout()
        top.addWidget(search, 1)
        top.addWidget(self.refresh_voices_button)
        lay.addLayout(top)

        scroll = getattr(self, "voice_scroll", None)
        if scroll is None:
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.Shape.NoFrame)
            scroll.setStyleSheet(
                "QScrollArea { background: transparent; border: none; }"
            )
            container = QWidget()
            container.setStyleSheet("background: transparent;")
            self.voice_rows_layout = QVBoxLayout(container)
            self.voice_rows_layout.setContentsMargins(0, 0, 0, 0)
            self.voice_rows_layout.setSpacing(8)
            scroll.setWidget(container)
            self.voice_rows_container = container
            self.voice_scroll = scroll
        scroll.setParent(None)
        lay.addWidget(scroll, 1)
        self.voice_panel = panel
        if not getattr(self, "_voice_rows", None):
            try:
                self._build_voice_rows(self.engine.get_available_voices())
            except Exception:
                pass

    def toggle_voice_dock(self) -> None:
        self._ensure_voice_panel()
        panel = self.voice_panel
        if panel.isVisible():
            panel.hide()
        else:
            panel.resize(400, 620)
            geo = self.frameGeometry()
            panel.move(geo.x() + geo.width() - 390, geo.y() + 70)
            panel.show()
            panel.raise_()
            panel.activateWindow()

'''

if "    def toggle_voice_dock(self) -> None:" in t:
    t = re.sub(
        r"    def toggle_voice_dock\(self\) -> None:[\s\S]*?(?=\n    def )",
        new_methods,
        t,
        count=1,
    )
    print("toggle_voice_dock reemplazado por panel QDialog.")
else:
    t = t.replace(
        "    def refresh_voices(self) -> None:",
        new_methods + "    def refresh_voices(self) -> None:",
        1,
    )
    print("Metodos insertados antes de refresh_voices.")

# 2. Asegurar conexion del boton
if "voices_button.clicked.connect(self.toggle_voice_dock)" not in t:
    t = t.replace(
        "self.refresh_voices_button.clicked.connect(self.refresh_voices)",
        "self.refresh_voices_button.clicked.connect(self.refresh_voices)\n"
        "        self.voices_button.clicked.connect(self.toggle_voice_dock)",
        1,
    )
    print("Conexion del boton Voces asegurada.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(p.read_text(encoding="utf-8"))
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
