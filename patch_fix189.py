from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

old_run = """    def run(self):
        try:
            import tempfile
            from pathlib import Path as _P
            tmp = str(_P(tempfile.gettempdir()) / "willpovoice_player.wav")
            from core.text_normalizer import (
                needs_homograph_guard,
                normalize_for_tts,
            )
            texto = normalize_for_tts(
                self.text,
                guard=needs_homograph_guard(self.voice or ""),
            )
            self.engine.save_text_to_wav(
                text=texto,
                output_path=tmp,
                voice_query=self.voice,
                rate=self.rate,
                volume=self.volume,
            )
            self.ready.emit(tmp)
        except Exception as exc:
            self.error.emit(str(exc))"""

new_run = """    def run(self):
        try:
            import tempfile
            from pathlib import Path as _P
            import pythoncom
            import win32com.client
            pythoncom.CoInitialize()
            from core.text_normalizer import (
                needs_homograph_guard,
                normalize_for_tts,
            )
            texto = normalize_for_tts(
                self.text,
                guard=needs_homograph_guard(self.voice or ""),
            )
            tmp = str(_P(tempfile.gettempdir()) / "willpovoice_player.wav")
            adapter = self.engine.adapter
            if self.voice:
                adapter.set_voice(self.voice)
            sapi = win32com.client.Dispatch("SAPI.SpVoice")
            try:
                sapi.Voice = adapter.sapi.Voice
            except Exception:
                pass
            sapi.Rate = max(-10, min(10, int(self.rate)))
            sapi.Volume = max(0, min(100, int(self.volume)))
            stream = win32com.client.Dispatch("SAPI.SpFileStream")
            stream.Open(tmp, 3, False)
            sapi.AudioOutputStream = stream
            sapi.Speak(texto)
            stream.Close()
            sapi.AudioOutputStream = None
            self.ready.emit(tmp)
        except Exception as exc:
            self.error.emit(str(exc))"""

if old_run in t:
    t = t.replace(old_run, new_run, 1)
    print("SynthWorker sintetiza WAV directo con win32com.")
else:
    print("AVISO: run de SynthWorker no encontrado exacto.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
