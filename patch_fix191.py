from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# ---- 1. SynthWorker: usar adapter.sapi (el que SI funciona con voces Online) ----
old_run = """            tmp = str(_P(tempfile.gettempdir()) / "willpovoice_player.wav")
            sapi = win32com.client.Dispatch("SAPI.SpVoice")
            if self.voice:
                try:
                    q = str(self.voice).lower()
                    first = q.split()[0] if q.split() else q
                    for token in sapi.GetVoices():
                        desc = token.GetDescription().lower()
                        if q in desc or first in desc:
                            sapi.Voice = token
                            break
                except Exception:
                    pass
            sapi.Rate = max(-10, min(10, int(self.rate)))
            sapi.Volume = max(0, min(100, int(self.volume)))"""
new_run = """            tmp = str(_P(tempfile.gettempdir()) / "willpovoice_player.wav")
            adapter = self.engine.adapter
            if self.voice:
                adapter.set_voice(self.voice)
            adapter.set_rate(self.rate)
            adapter.set_volume(self.volume)
            sapi = adapter.sapi"""
if old_run in t:
    t = t.replace(old_run, new_run, 1)
    print("1. SynthWorker usa adapter.sapi (voces Online OK).")

# ---- 2. speak_text: detener todo y registrar clave de sintesis ----
old_st = """        self._set_player_icon(True, loading=True)
        self.statusBar().showMessage("Preparando audio...")
        self._synth_worker = SynthWorker("""
new_st = """        self._set_player_icon(True, loading=True)
        self.statusBar().showMessage("Preparando audio...")
        try:
            self.player.stop()
        except Exception:
            pass
        try:
            self.engine.stop()
        except Exception:
            pass
        self._last_synth_key = (voice_text, text)
        self._synth_worker = SynthWorker("""
if old_st in t:
    t = t.replace(old_st, new_st, 1)
    print("2. speak_text detiene audio previo y registra clave.")

# ---- 3. Play: resintetiza si cambio la voz o el texto ----
old_play = """def _player_play_clicked(self):
    if not getattr(self, "_media_ready", False):
        self.speak_text()
        return"""
new_play = """def _player_play_clicked(self):
    texto = self.text_edit.toPlainText().strip()
    voz = self.voice_combo.currentText().strip()
    if (getattr(self, "_last_synth_key", None) != (voz, texto)
            or not getattr(self, "_media_ready", False)):
        self.speak_text()
        return"""
if old_play in t:
    t = t.replace(old_play, new_play, 1)
    print("3. Play resintetiza al cambiar voz/texto.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
