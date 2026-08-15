from pathlib import Path
import re, ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

new_toggle = '''def _player_play_clicked(self):
    if getattr(self, "_started", False) and not getattr(
            self, "_paused", False):
        try:
            self.engine.adapter.sapi.Pause()
        except Exception:
            pass
        self.player_timer.stop()
        self._paused = True
        self._set_player_icon(False)
        self.statusBar().showMessage("Reproduccion pausada.")
    elif getattr(self, "_paused", False):
        try:
            self.engine.adapter.sapi.Resume()
        except Exception:
            pass
        self.player_timer.start(200)
        self._paused = False
        self._set_player_icon(True)
        self.statusBar().showMessage("Reanudando reproduccion...")
    else:
        self.speak_text()


'''
t = re.sub(
    r"def _player_play_clicked\(self\):[\s\S]*?(?=\ndef _set_player_icon)",
    new_toggle,
    t,
    count=1,
)
print("Toggle corregido: pausa solo si NO esta pausado.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
