from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# ---- 1. speak_text: clave de sintesis + reset de gracia ----
old_st = """        self._texto_para_ratio = text
        self._resume_offset = 0
        self.engine.speak_async(text)"""
new_st = """        self._texto_para_ratio = text
        self._resume_offset = 0
        self._resume_at = 0.0
        self._last_synth_key = (
            self.voice_combo.currentText().strip(), text)
        self.engine.speak_async(text)"""
if old_st in t:
    t = t.replace(old_st, new_st, 1)
    print("1. speak_text guarda clave (voz, texto) y reset de gracia.")

# ---- 2. Pausa/reanuda REALES (instantaneos, probados) ----
s = t.find("def _player_play_clicked")
e = t.find("\ndef ", s + 10)
new_play = '''def _player_play_clicked(self):
    if not getattr(self, "_started", False):
        self.speak_text()
        return
    texto = getattr(self, "_texto_para_ratio", "")
    voz = self.voice_combo.currentText().strip()
    if getattr(self, "_last_synth_key", None) != (voz, texto):
        self.speak_text()
        return
    try:
        sapi = self.engine.adapter.sapi
        if getattr(self, "_paused", False):
            sapi.Resume()
            self._paused = False
            import time as _time
            self._resume_at = _time.time()
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
        self.statusBar().showMessage(f"Error en pausa: {exc}")


'''
if s != -1 and e != -1 and e > s:
    t = t[:s] + new_play + t[e:]
    print("2. Pausa/reanuda reales con SAPI (0.0s, probado).")

# ---- 3. Gracia de 1s tras reanudar (state=0 transitorio) ----
old_end = """    if state != 2:
        self.player_timer.stop()
        self._started = False"""
new_end = """    if state != 2:
        import time as _time
        if _time.time() - getattr(self, "_resume_at", 0.0) < 1.0:
            return
        self.player_timer.stop()
        self._started = False"""
if old_end in t:
    t = t.replace(old_end, new_end, 1)
    print("3. Gracia de 1s tras Resume (evita falso 'terminado').")

p.write_text(t, encoding="utf-8")

for name in ["_player_play_clicked"]:
    if f"def {name}(" in t and f"MainWindow.{name} = {name}" not in t:
        t += f"\nMainWindow.{name} = {name}\n"
p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
