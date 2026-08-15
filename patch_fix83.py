from pathlib import Path
import ast

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

old = """    def toggle_voice_dock(self) -> None:
        self.voice_dock.setVisible(not self.voice_dock.isVisible())"""

new = """    def toggle_voice_dock(self) -> None:
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
                pass"""

if old in t:
    t = t.replace(old, new, 1)
    print("toggle_voice_dock reforzado (ancho 400 + al frente).")
else:
    print("AVISO: toggle no encontrado tal cual.")

p.write_text(t, encoding="utf-8")
try:
    ast.parse(p.read_text(encoding="utf-8"))
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
