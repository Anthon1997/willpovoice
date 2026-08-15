from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

s = t.find("def _tick_player")
e = t.find("\ndef ", s + 10)
new_tick = '''def _tick_player(self):
    if not getattr(self, "_started", False):
        return
    if getattr(self, "_paused", False):
        return
    try:
        st = self.engine.adapter.sapi.Status
        state = st.RunningState
        ms = max(0.0, float(st.AudioPosition))
    except Exception:
        return
    if not getattr(self, "_saw_running", False):
        if state == 2:
            self._saw_running = True
            self._set_player_icon(True, loading=False)
            self.statusBar().showMessage("Reproduciendo...")
        else:
            return
    if state == 2:
        self._seconds = ms / 1000.0
    elif state == 1 and self._seconds > 0.3:
        self.player_timer.stop()
        self._started = False
        self._paused = False
        self.time_tot.setText(self._fmt_time(self._seconds))
        self.time_cur.setText(self._fmt_time(self._seconds))
        self.progress_slider.setValue(100)
        self._set_player_icon(False)
        self.statusBar().showMessage("Reproduccion terminada.")
        return
    est = max(1.0, getattr(self, "_est_seconds", 1.0))
    self.time_cur.setText(self._fmt_time(self._seconds))
    self.progress_slider.setValue(
        min(100, int(self._seconds / est * 100)))


'''
if s != -1 and e != -1 and e > s:
    t = t[:s] + new_tick + t[e:]
    print("_tick_player con valores SAPI correctos (2=hablando, 1=done).")
else:
    print("AVISO: anclas no encontradas.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
