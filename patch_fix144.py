from pathlib import Path
import re, ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# ---- 1. RECOPILACION ----
for m in ("def _tick_player", "self._started = False",
          "def speak_text"):
    print(f"--- {m!r} indice:", t.find(m))

# ---- 2. _tick_player autonomo ----
new_tick = '''def _tick_player(self):
    elapsed = -1.0
    state = -1
    try:
        st = self.engine.adapter.sapi.Status
        state = st.RunningState
        elapsed = max(0.0, float(st.AudioPosition)) / 1000.0
    except Exception:
        pass
    if not getattr(self, "_started", False):
        return
    if state == 1:
        self._saw_running = True
        if elapsed >= 0:
            self._seconds = elapsed
        else:
            self._seconds += 0.2
    else:
        self._seconds += 0.2
    self.time_cur.setText(self._fmt_time(self._seconds))
    est = max(1.0, getattr(self, "_est_seconds", 1.0))
    self.progress_slider.setValue(
        min(100, int(self._seconds / est * 100)))
    done = (getattr(self, "_saw_running", False) and state == 0
            and self._seconds > 0.5) or self._seconds >= est
    if done:
        self.player_timer.stop()
        self._started = False
        self.time_cur.setText(self._fmt_time(est))
        self.progress_slider.setValue(100)


'''
t = re.sub(
    r"def _tick_player\(self\):[\s\S]*?(?=\ndef speak_text)",
    new_tick,
    t,
    count=1,
)
print("2. _tick_player autonomo.")

# ---- 3. speak_text marca inicio real ----
old_start = """        self._seconds = 0
        self._started = False
        self.time_tot.setText(self._fmt_time(self._est_seconds))"""
new_start = """        self._seconds = 0
        self._started = True
        self._saw_running = False
        self.time_tot.setText(self._fmt_time(self._est_seconds))"""
if old_start in t:
    t = t.replace(old_start, new_start, 1)
    print("3. speak_text marca _started=True.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
