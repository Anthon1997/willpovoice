from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# ---- 1. speak_text: resetear offset de reanudacion ----
old_st = """        self._texto_para_ratio = text
        self.engine.speak_async(text)
        self.player_timer.start(100)"""
new_st = """        self._texto_para_ratio = text
        self._resume_offset = 0
        self.engine.speak_async(text)
        self.player_timer.start(100)"""
if old_st in t:
    t = t.replace(old_st, new_st, 1)
    print("1. speak_text resetea offset de reanudacion.")

# ---- 2. _tick_player: ratio con offset + guardar posicion ----
s = t.find("def _tick_player")
e = t.find("\ndef ", s + 10)
if e == -1 or e < s:
    e = t.find("\nMainWindow._tick_player", s)
if e == -1:
    e = s + 2000

new_tick = '''def _tick_player(self):
    if not getattr(self, "_started", False):
        return
    if getattr(self, "_paused", False):
        return
    try:
        st = self.engine.adapter.sapi.Status
        state = int(st.RunningState)
    except Exception:
        return
    if not getattr(self, "_saw_running", False):
        if state == 2:
            self._saw_running = True
            self._set_player_icon(True, loading=False)
            self.statusBar().showMessage("Reproduciendo...")
        else:
            return
    if state != 2:
        self.player_timer.stop()
        self._started = False
        self._paused = False
        self._resume_offset = 0
        self._set_player_icon(False)
        self.statusBar().showMessage("Reproduccion terminada.")
        return
    try:
        texto = getattr(self, "_texto_para_ratio", "") or self.text_edit.toPlainText()
        offset = getattr(self, "_resume_offset", 0)
        pos = int(st.InputWordPosition)
        full_pos = offset + pos
        if len(texto) > 0 and full_pos > 0:
            ratio = min(1.0, full_pos / max(1, len(texto)))
        else:
            ratio = 0.0
        est = max(1.0, getattr(self, "_est_seconds", 1.0))
        secs = ratio * est
        self._seconds = secs
        self.time_cur.setText(self._fmt_time(secs))
        self.progress_slider.setValue(min(100, int(ratio * 100)))
    except Exception:
        pass


'''
if s != -1 and e != -1 and e > s:
    t = t[:s] + new_tick + t[e:]
    print("2. _tick_player con offset de reanudacion.")

# ---- 3. _player_play_clicked: pausa por posicion, sin Pause/Resume ----
s = t.find("def _player_play_clicked")
e = t.find("\ndef ", s + 10)
if e == -1 or e < s:
    e = t.find("\nMainWindow._player_play_clicked", s)
if e == -1:
    e = s + 1500

new_play = '''def _player_play_clicked(self):
    if not getattr(self, "_started", False):
        self.speak_text()
        return
    if getattr(self, "_paused", False):
        # Reanudar desde la posicion guardada
        texto = getattr(self, "_texto_para_ratio", "")
        offset = getattr(self, "_resume_offset", 0)
        resto = texto[offset:]
        if resto.strip():
            self._paused = False
            self._saw_running = False
            self._set_player_icon(True, loading=True)
            self.statusBar().showMessage("Reanudando...")
            self.engine.speak_async(resto)
            self.player_timer.start(100)
        else:
            self._paused = False
            self._set_player_icon(False)
        return
    # Pausar: guardar posicion y detener audio
    try:
        st = self.engine.adapter.sapi.Status
        pos = int(st.InputWordPosition)
    except Exception:
        pos = 0
    self._resume_offset = getattr(self, "_resume_offset", 0) + pos
    try:
        self.engine.stop()
    except Exception:
        pass
    self._paused = True
    self.player_timer.stop()
    self._set_player_icon(False)
    self.statusBar().showMessage(
        f"Pausa en caracter {self._resume_offset}.")


'''
if s != -1 and e != -1 and e > s:
    t = t[:s] + new_play + t[e:]
    print("3. Pausa por posicion (sin Pause/Resume bloqueante).")

p.write_text(t, encoding="utf-8")

# Auto-reparo asignaciones
for name in ["_tick_player", "_player_play_clicked"]:
    if f"def {name}(" in t and f"MainWindow.{name} = {name}" not in t:
        t += f"\nMainWindow.{name} = {name}\n"

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
