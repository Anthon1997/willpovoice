from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# ---- 1. speak_text: reproduccion en vivo + spinner ----
s = t.find("def speak_text(self):")
e = t.find("def _on_synth_ready")
new_speak = '''def speak_text(self):
    try:
        text = self.text_edit.toPlainText().strip()
        if not text:
            self.statusBar().showMessage("Escribe un texto antes de reproducir.")
            return
        voice_data = self.voice_combo.currentData(Qt.ItemDataRole.UserRole)
        if voice_data:
            self.engine.select_voice(voice_data)
        self.engine.set_rate(self.rate_slider.value())
        self.engine.set_volume(self.volume_slider.value())
        self._add_to_history(text)
        self.settings["conv_today"] = int(self.settings.get("conv_today", 0)) + 1
        self.stat_conv.value_label.setText(str(self.settings["conv_today"]))
        words = len(text.split()) or 1
        factor = 1.0 + self.rate_slider.value() / 20.0
        self._est_seconds = words / (2.8 * factor) + 0.6
        self._seconds = 0
        self._started = True
        self._saw_running = False
        self._paused = False
        self.time_tot.setText(self._fmt_time(self._est_seconds))
        self.time_cur.setText("0:00")
        self.progress_slider.setValue(0)
        self._set_player_icon(True, loading=True)
        self.statusBar().showMessage("Preparando audio...")
        self.engine.speak_async(text)
        self.player_timer.start(100)
    except Exception as exc:
        QMessageBox.warning(self, "Error", f"No se pudo reproducir: {exc}")


'''
if s != -1 and e != -1 and e > s:
    t = t[:s] + new_speak + t[e:]
    print("1. speak_text en vivo con spinner.")

# ---- 2. _tick_player: posicion REAL por AudioPosition ----
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
        if state == 1:
            self._saw_running = True
            self._set_player_icon(True, loading=False)
            self.statusBar().showMessage("Reproduciendo...")
        else:
            return
    if state == 1:
        self._seconds = ms / 1000.0
    elif state == 0 and self._seconds > 0.3:
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
    print("2. _tick_player con AudioPosition real.")

# ---- 3. _player_play_clicked: pausa/reanuda reales ----
s = t.find("def _player_play_clicked")
e = t.find("def _set_player_icon")
new_play = '''def _player_play_clicked(self):
    if not getattr(self, "_started", False):
        self.speak_text()
        return
    if getattr(self, "_paused", False):
        try:
            self.engine.adapter.sapi.Resume()
        except Exception:
            pass
        self._paused = False
        self.player_timer.start(100)
        self._set_player_icon(True, loading=False)
        self.statusBar().showMessage("Reanudando reproduccion...")
    else:
        try:
            self.engine.adapter.sapi.Pause()
        except Exception:
            pass
        self._paused = True
        self.player_timer.stop()
        self._set_player_icon(False)
        self.statusBar().showMessage("Reproduccion pausada.")


'''
if s != -1 and e != -1 and e > s:
    t = t[:s] + new_play + t[e:]
    print("3. Pausa/reanuda reales con SAPI.")

# ---- 4. Volumen tambien al motor en vivo ----
s = t.find("def _on_volume_changed")
e = t.find("\ndef ", s + 10)
if e == -1 or e < s:
    e = t.find("\nMainWindow.", s)
new_vol = '''def _on_volume_changed(self, value):
    try:
        self.audio_out.setVolume(value / 100.0)
    except Exception:
        pass
    try:
        self.engine.set_volume(value)
    except Exception:
        pass


'''
if s != -1 and e != -1 and e > s:
    t = t[:s] + new_vol + t[e:]
    print("4. Volumen aplicado al motor en vivo.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
