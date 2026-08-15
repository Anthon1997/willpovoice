from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# Reescribir _tick_player con logica real del diagnostico
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
        sapi = self.engine.adapter.sapi
        st = sapi.Status
        state = int(st.RunningState)
    except Exception:
        return
    # state==2: hablando (valor real del diagnostico)
    # state==0: idle/done (valor real del diagnostico)
    if not getattr(self, "_saw_running", False):
        if state == 2:
            self._saw_running = True
            self._set_player_icon(True, loading=False)
            self.statusBar().showMessage("Reproduciendo...")
        else:
            return
    # Si ya no esta hablando (state != 2) y ya vio running => termino
    if state != 2:
        self.player_timer.stop()
        self._started = False
        self._paused = False
        try:
            self._set_player_icon(False)
        except Exception:
            pass
        self.statusBar().showMessage("Reproduccion terminada.")
        return
    # Sigue hablando: calcular posicion por palabra actual
    try:
        texto = getattr(self, "_texto_para_ratio", "") or self.text_edit.toPlainText()
        pos = int(st.InputWordPosition)
        if len(texto) > 0 and pos > 0:
            ratio = min(1.0, pos / max(1, len(texto)))
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
    print("_tick_player reescrito con logica real (state 2=habla, 0=done).")
else:
    print("AVISO: anclas no encontradas.")

# Reescribir _player_play_clicked con Pause/Resume correctos
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
    try:
        sapi = self.engine.adapter.sapi
        if getattr(self, "_paused", False):
            sapi.Resume()
            self._paused = False
            self.player_timer.start(100)
            self._set_player_icon(True, loading=False)
            self.statusBar().showMessage("Reanudando reproduccion...")
        else:
            sapi.Pause()
            self._paused = True
            self.player_timer.stop()
            self._set_player_icon(False)
            self.statusBar().showMessage("Reproduccion pausada.")
    except Exception as exc:
        self.statusBar().showMessage(f"Error: {exc}")


'''
if s != -1 and e != -1 and e > s:
    t = t[:s] + new_play + t[e:]
    print("_player_play_clicked reescrito con logica real.")

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
