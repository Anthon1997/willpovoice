from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# ---- 1. Handler de cambio de voz: usar texto visible ----
old_combo = """def _on_combo_voice(self):
    voice = self.voice_combo.currentData(Qt.ItemDataRole.UserRole)
    if voice:
        self._select_voice(voice)"""
new_combo = """def _on_combo_voice(self):
    voz_texto = self.voice_combo.currentText().strip()
    if voz_texto:
        self.engine.select_voice(voz_texto)
        self.statusBar().showMessage(f"Voz: {voz_texto}")"""
if old_combo in t:
    t = t.replace(old_combo, new_combo, 1)
    print("1. _on_combo_voice arreglado (crash al cambiar voz resuelto).")

# ---- 2. Eliminar conexiones fantasma de QMediaPlayer ----
fantasmas = [
    "self.player.positionChanged.connect(self._on_position_changed)",
    "self.player.durationChanged.connect(self._on_duration_changed)",
    "self.player.mediaStatusChanged.connect(self._on_media_status_changed)",
    "self.progress_slider.sliderMoved.connect(self._on_slider_moved)",
]
for f in fantasmas:
    if f in t:
        t = t.replace(f, "# " + f)
        print(f"2. Fantasma desactivado: {f.split('.')[1][:20]}...")

# ---- 3. Reescribir _tick_player con InputWordPosition ----
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
        pos = int(st.InputWordPosition)
        length = int(st.InputWordLength)
    except Exception:
        return
    total_chars = max(1, pos + length)
    texto = self.text_edit.toPlainText()
    if pos > 0 and len(texto) > 0:
        ratio = min(1.0, pos / max(1, len(texto)))
    else:
        ratio = 0.0
    est = max(1.0, getattr(self, "_est_seconds", 1.0))
    secs = ratio * est
    if not getattr(self, "_saw_running", False):
        if state == 2:
            self._saw_running = True
            self._set_player_icon(True, loading=False)
            self.statusBar().showMessage("Reproduciendo...")
        else:
            return
    if state == 2:
        self._seconds = secs
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
    self.time_cur.setText(self._fmt_time(self._seconds))
    self.progress_slider.setValue(min(100, int(ratio * 100)))


'''
if s != -1 and e != -1 and e > s:
    t = t[:s] + new_tick + t[e:]
    print("3. _tick_player usa InputWordPosition real.")

# ---- 4. Guardar texto normalizado al iniciar (para ratio estable) ----
old_st = """        self.engine.speak_async(text)
        self.player_timer.start(100)"""
new_st = """        self._texto_para_ratio = text
        self.engine.speak_async(text)
        self.player_timer.start(100)"""
if old_st in t:
    t = t.replace(old_st, new_st, 1)
    print("4. Texto para ratio guardado.")

# ---- 5. Usar texto guardado en tick (si existe) ----
t = t.replace(
    "texto = self.text_edit.toPlainText()",
    "texto = getattr(self, '_texto_para_ratio', None) or self.text_edit.toPlainText()"
)
print("5. Tick usa texto guardado (consistente con sintesis).")

# ---- 6. Verificar que _select_voice no exista como wrapper conflictivo ----
if "def _select_voice(self" in t:
    print("AVISO: existe wrapper _select_voice (podria causar problemas).")

p.write_text(t, encoding="utf-8")

# ---- 7. Auto-reparo de asignaciones ----
for name in ["_tick_player", "_on_combo_voice", "_player_play_clicked",
             "_set_player_icon", "_spin_tick", "_draw_spin", "speak_text"]:
    if f"def {name}(" in t and f"MainWindow.{name} = {name}" not in t:
        t += f"\nMainWindow.{name} = {name}\n"

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
