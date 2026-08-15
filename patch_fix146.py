from pathlib import Path
import re, ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# ---- 1. RECOPILACION ----
for m in ("def _player_play_clicked", "MainWindow._pause_playback",
          "self._saw_running = False"):
    print(f"--- {m!r} indice:", t.find(m))

# ---- 2. Toggle con Pause/Resume reales ----
old_tail = r"def _player_play_clicked\(self\):[\s\S]*?MainWindow\._set_player_icon = _set_player_icon"
new_tail = '''def _player_play_clicked(self):
    if getattr(self, "_started", False):
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


def _set_player_icon(self, playing):
    self.player_play.icon.setPixmap(
        make_icon("pause" if playing else "play", TEXT, 15))


MainWindow._player_play_clicked = _player_play_clicked
MainWindow._set_player_icon = _set_player_icon'''
t2 = re.sub(old_tail, new_tail, t, count=1)
if t2 != t:
    t = t2
    print("2. Toggle Pause/Resume reales.")
else:
    print("AVISO: cola toggle no encontrada.")

# ---- 3. speak_text limpia estado de pausa ----
old_st = """        self._started = True
        self._saw_running = False"""
new_st = """        self._started = True
        self._saw_running = False
        self._paused = False"""
if old_st in t:
    t = t.replace(old_st, new_st, 1)
    print("3. speak_text limpia _paused.")

# ---- 4. Fin natural limpia pausa ----
old_done = """    if done:
        self.player_timer.stop()
        self._started = False
        self.time_cur.setText(self._fmt_time(est))"""
new_done = """    if done:
        self.player_timer.stop()
        self._started = False
        self._paused = False
        self.time_cur.setText(self._fmt_time(est))"""
if old_done in t:
    t = t.replace(old_done, new_done, 1)
    print("4. Fin natural limpia _paused.")

# ---- 5. Detener limpia pausa ----
old_stop = """        self._started = False
        self._set_player_icon(False)"""
new_stop = """        self._started = False
        self._paused = False
        self._set_player_icon(False)"""
if old_stop in t:
    t = t.replace(old_stop, new_stop, 1)
    print("5. Detener limpia _paused.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
