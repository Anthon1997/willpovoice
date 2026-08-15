from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

s = t.find("def _on_combo_voice")
if s == -1:
    print("AVISO: _on_combo_voice no encontrado.")
else:
    e = t.find("\ndef ", s + 10)
    if e == -1 or e < s:
        e = t.find("\nMainWindow._on_combo_voice", s)
    if e == -1 or e < s:
        e = s + 2500
    print("----- VERSION ACTUAL (para registro) -----")
    print(t[s:e])

    new_fn = '''def _on_combo_voice(self):
    data = self.voice_combo.currentData(Qt.ItemDataRole.UserRole)
    voz_texto = self.voice_combo.currentText().strip()
    was_active = getattr(self, "_started", False)
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
    if isinstance(data, dict):
        desc = data.get("description", "") or voz_texto
    else:
        desc = data or voz_texto
    try:
        self.engine.adapter.set_voice(desc)
        self.statusBar().showMessage(f"Voz cambiada: {voz_texto}")
        self._last_synth_key = None
        if was_active:
            self.speak_text()
    except Exception as exc:
        self.statusBar().showMessage(f"Error al cambiar voz: {exc}")


'''
    t = t[:s] + new_fn + t[e:]
    print("----- _on_combo_voice reescrito con auto-rearranque -----")

p.write_text(t, encoding="utf-8")

if "MainWindow._on_combo_voice = _on_combo_voice" not in t:
    t += "\nMainWindow._on_combo_voice = _on_combo_voice\n"
    p.write_text(t, encoding="utf-8")
    print("Asignacion agregada.")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
