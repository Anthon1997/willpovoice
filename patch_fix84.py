from pathlib import Path
import re, ast

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

new_code = '''    def _ensure_voice_dock(self) -> None:
        if getattr(self, "voice_dock", None) is not None:
            return
        from PySide6.QtWidgets import QDockWidget, QScrollArea

        dock = QDockWidget("Voces", self)
        dock.setObjectName("voiceDock")
        dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetClosable
        )
        dock.setStyleSheet(
            "QDockWidget { background: #0a0f1c; color: #ffd75e; font-weight: 700; border: none; }"
            "QDockWidget::title { background: #131a2b; padding: 8px; }"
        )
        content = QWidget()
        content.setStyleSheet("background: #0a0f1c;")
        lay = QVBoxLayout(content)
        lay.setContentsMargins(10, 10, 10, 10)
        lay.setSpacing(8)
        top = QHBoxLayout()
        search = getattr(self, "voice_search", None)
        if search is None:
            search = QLineEdit()
            search.setPlaceholderText("Buscar voces...")
            search.textChanged.connect(self._filter_voice_rows)
            self.voice_search = search
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
        lay.addWidget(scroll, 1)
        dock.setWidget(content)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
        self.voice_dock = dock
        if not getattr(self, "_voice_rows", None):
            try:
                self._build_voice_rows(self.engine.get_available_voices())
            except Exception:
                pass

    def toggle_voice_dock(self) -> None:
        self._ensure_voice_dock()
        show = not self.voice_dock.isVisible()
        self.voice_dock.setVisible(show)
        if show:
            self.voice_dock.setMinimumWidth(400)
            self.voice_dock.raise_()
            try:
                self.resizeDocks(
                    [self.voice_dock], [400], Qt.Orientation.Horizontal
                )
            except Exception:
                pass

'''

if "def _ensure_voice_dock" not in t:
    t2, n = re.subn(
        r"    def toggle_voice_dock\(self\) -> None:.*?(?=\n    def )",
        "\n" + new_code,
        t,
        count=1,
        flags=re.S,
    )
    if n:
        t = t2
        print("toggle_voice_dock reemplazado por version bajo demanda.")
    else:
        t = t.replace(
            "    def refresh_voices(self) -> None:",
            new_code + "    def refresh_voices(self) -> None:",
            1,
        )
        print("Metodos insertados antes de refresh_voices.")
else:
    print("_ensure_voice_dock ya existia.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(p.read_text(encoding="utf-8"))
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
