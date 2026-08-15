from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# ---- 1. _on_combo_voice: usar token COM y detener todo ----
old_combo = """def _on_combo_voice(self):
    voz_texto = self.voice_combo.currentText().strip()
    if voz_texto:
        self.engine.select_voice(voz_texto)
        self.statusBar().showMessage(f"Voz: {voz_texto}")"""
new_combo = """def _on_combo_voice(self):
    # Obtener el token COM que YA guarda el combo (no el texto)
    token = self.voice_combo.currentData(Qt.ItemDataRole.UserRole)
    voz_texto = self.voice_combo.currentText().strip()
    # Detener cualquier reproduccion en curso
    try:
        self.engine.stop()
    except Exception:
        pass
    self.player_timer.stop()
    self._started = False
    self._paused = False
    self._saw_running = False
    self._resume_offset = 0
    self._set_player_icon(False)
    self.progress_slider.setValue(0)
    self.time_cur.setText("0:00")
    # Asignar el token COM directamente al adapter (salta el matcher)
    if token:
        try:
            self.engine.adapter.sapi.Voice = token
            self.statusBar().showMessage(f"Voz cambiada: {voz_texto}")
            # Invalidar la ultima sintesis para que Play resintetice
            self._last_synth_key = None
        except Exception as exc:
            self.statusBar().showMessage(f"Error al cambiar voz: {exc}")
    else:
        self.statusBar().showMessage(f"Voz: {voz_texto} (sin token)")"""
if old_combo in t:
    t = t.replace(old_combo, new_combo, 1)
    print("1. _on_combo_voice usa token COM + detiene todo.")
else:
    print("AVISO: _on_combo_voice no encontrado exacto.")

# ---- 2. speak_text: usar token COM en vez de voz_data ----
old_speak = """        voice_data = self.voice_combo.currentData(Qt.ItemDataRole.UserRole)
        if voice_data:
            self.engine.select_voice(voice_data)"""
new_speak = """        voice_token = self.voice_combo.currentData(Qt.ItemDataRole.UserRole)
        if voice_token:
            try:
                self.engine.adapter.sapi.Voice = voice_token
            except Exception:
                pass"""
if old_speak in t:
    t = t.replace(old_speak, new_speak, 1)
    print("2. speak_text asigna token COM directo (no matcher).")
else:
    print("AVISO: speak_text no encontrado exacto.")

p.write_text(t, encoding="utf-8")

# Auto-reparo
for name in ["_on_combo_voice"]:
    if f"def {name}(" in t and f"MainWindow.{name} = {name}" not in t:
        t += f"\nMainWindow.{name} = {name}\n"
p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
