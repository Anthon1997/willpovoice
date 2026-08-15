from pathlib import Path
import re, ast

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

# 1. Eliminar _ensure_voice_panel viejo si existe
t = re.sub(
    r"    def _ensure_voice_panel\(self\) -> None:[\s\S]*?\n    def toggle_voice_dock",
    "    def toggle_voice_dock",
    t,
    count=1,
)

new_toggle = '''    def _ensure_voice_panel(self) -> None:
        from PySide6.QtWidgets import QScrollArea, QDialog

        old = getattr(self, "voice_panel", None)
        if old is not None:
            try:
                old.close()
                old.deleteLater()
            except Exception:
                pass
            self.voice_panel = None
        dock = getattr(self, "voice_dock", None)
        if dock is not None:
            try:
                self.removeDockWidget(dock)
                dock.deleteLater()
            except Exception:
                pass
            self.voice_dock = None

        panel = QDialog(self)
        panel.setWindowTitle("Voces - WillpoVoice")
        panel.setModal(False)
        panel.setWindowFlags(
            Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint
        )
        panel.setStyleSheet("QDialog { background: #0a0f1c; }")
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(10, 10, 10, 10)
        lay.setSpacing(8)

        search = QLineEdit()
        search.setPlaceholderText("Buscar voces...")
        lay.addWidget(search)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(
            "QScrollArea { background: transparent; border: none; }"
        )
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        rows_layout = QVBoxLayout(container)
        rows_layout.setContentsMargins(0, 0, 0, 0)
        rows_layout.setSpacing(8)
        scroll.setWidget(container)
        lay.addWidget(scroll, 1)

        self.voice_panel = panel
        self.voice_search = search
        self.voice_rows_layout = rows_layout
        self.voice_rows_container = container
        self.voice_scroll = scroll
        self._build_voice_rows(self.engine.get_available_voices())
        search.textChanged.connect(self._filter_voice_rows)

    def toggle_voice_dock(self) -> None:
        try:
            print(">>> TOGGLE VOCES LLAMADO")
            self._ensure_voice_panel()
            panel = self.voice_panel
            panel.resize(400, 620)
            geo = self.frameGeometry()
            panel.move(geo.x() + geo.width() - 380, geo.y() + 80)
            panel.show()
            panel.raise_()
            panel.activateWindow()
        except Exception:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self, "Error", "No se pudo abrir el panel de voces."
            )

'''

t = re.sub(
    r"    def toggle_voice_dock\(self\) -> None:[\s\S]*?(?=\n    def (?!toggle_voice_dock|_ensure_voice_panel))",
    "\n" + new_toggle,
    t,
    count=1,
)
print("toggle_voice_dock + _ensure_voice_panel reescritos (a prueba de fallos).")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(p.read_text(encoding="utf-8"))
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
