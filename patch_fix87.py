from pathlib import Path
import re, ast

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

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
                self.resizeDocks([panel], [420], Qt.Orientation.Horizontal)
            except Exception:
                pass

'''

t, n = re.subn(
    r"    def _ensure_voice_panel\(self\) -> None:[\s\S]*?"
    r"\n    def toggle_voice_dock\(self\) -> None:[\s\S]*?"
    r"(?=\n    def (?!toggle_voice_dock|_ensure_voice_panel))",
    "\n" + new_methods,
    t,
    count=1,
)
print(f"Metodos convertidos a QDockWidget: {n}")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(p.read_text(encoding="utf-8"))
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
