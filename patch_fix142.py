from pathlib import Path
import re, ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# ---- 1. RECOPILACION ----
for m in ("def _tick_player", "self.player_timer.start(500)",
          "def stop_speech"):
    print(f"--- {m!r} indice:", t.find(m))

# ---- 2. _tick_player vinculado al audio real ----
new_tick = '''def _tick_player(self):
    try:
        st = self.engine.adapter.sapi.Status
        state = st.RunningState
        elapsed = max(0.0, float(st.AudioPosition)) / 1000.0
    except Exception:
        state = 1
        self._seconds += 0.2
        elapsed = self._seconds
    if state == 2:
        self._started = True
        self._seconds = elapsed
        self.time_cur.setText(self._fmt_time(elapsed))
        est = max(1.0, getattr(self, "_est_seconds", 1.0))
        self.progress_slider.setValue(
            min(100, int(elapsed / est * 100)))
    if state != 2 and getattr(self, "_started", False):
        self.player_timer.stop()
        self._started = False
        tot = getattr(self, "_est_seconds", elapsed)
        self.time_cur.setText(self._fmt_time(tot))
        self.progress_slider.setValue(100)


'''
t = re.sub(
    r"def _tick_player\(self\):[\s\S]*?(?=\ndef speak_text)",
    new_tick,
    t,
    count=1,
)
print("2. _tick_player con posicion real de audio.")

# ---- 3. speak_text: duracion estimada + total + timer 200ms ----
old_play = """        self._seconds = 0
        self.player_timer.start(500)
        self.statusBar().showMessage("Reproduciendo...")"""
new_play = """        words = len(text.split()) or 1
        factor = 1.0 + self.rate_slider.value() / 20.0
        self._est_seconds = words / (2.8 * factor) + 0.6
        self._seconds = 0
        self._started = False
        self.time_tot.setText(self._fmt_time(self._est_seconds))
        self.time_cur.setText("0:00")
        self.progress_slider.setValue(0)
        self.player_timer.start(200)
        self.statusBar().showMessage("Reproduciendo...")"""
if old_play in t:
    t = t.replace(old_play, new_play, 1)
    print("3. speak_text con duracion estimada real.")

# ---- 4. stop_speech resetea todo ----
old_stop = """        self.player_timer.stop()
        self._seconds = 0
        self.time_cur.setText("0:00")
        self.progress_slider.setValue(0)
        self.statusBar().showMessage("Reproducción detenida.")"""
new_stop = """        self.player_timer.stop()
        self._seconds = 0
        self._started = False
        self.time_cur.setText("0:00")
        self.time_tot.setText("0:00")
        self.progress_slider.setValue(0)
        self.statusBar().showMessage("Reproducción detenida.")"""
if old_stop in t:
    t = t.replace(old_stop, new_stop, 1)
    print("4. stop_speech resetea reproductor.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
