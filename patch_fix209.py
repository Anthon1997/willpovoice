from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# ---- 1. _toggle_preview: pausa main + instancia propia ----
s = t.find("def _toggle_preview")
e = t.find("\ndef ", s + 10)
new_toggle = '''def _toggle_preview(self, name):
    if getattr(self, "_preview_name", "") == name and getattr(
            self, "_preview_playing", False):
        self._stop_preview()
        return
    self._stop_preview()
    # Pausa instantanea de la reproduccion principal
    if getattr(self, "_started", False) and not getattr(
            self, "_paused", False):
        try:
            self.engine.adapter.sapi.Pause()
            self._paused = True
            self._preview_paused_main = True
            self.player_timer.stop()
            self._set_player_icon(False)
            self.statusBar().showMessage(
                "Reproduccion pausada por previsualizacion.")
        except Exception:
            pass
    try:
        import win32com.client
        if not hasattr(self, "_preview_sapi"):
            self._preview_sapi = win32com.client.Dispatch("SAPI.SpVoice")
        token = self.exporter.adapter._get_voice_token(name)
        if token is None:
            raise ValueError(f"Voz no encontrada: {name}")
        self._preview_sapi.Voice = token
        self._preview_sapi.Speak("Hola esta es mi voz", 1)
        self._preview_name = name
        self._preview_playing = True
        self.preview_changed.emit(name, True)
        self.statusBar().showMessage(f"Previsualizando: {name}")
    except Exception as exc:
        self._preview_playing = False
        if getattr(self, "_preview_paused_main", False):
            self._preview_paused_main = False
            try:
                self.engine.adapter.sapi.Resume()
                self._paused = False
                self.player_timer.start(100)
                self._set_player_icon(True, loading=False)
            except Exception:
                pass
        QMessageBox.warning(self, "WillpoVoice",
                            f"No se pudo reproducir la muestra: {exc}")


'''
if s != -1 and e != -1 and e > s:
    t = t[:s] + new_toggle + t[e:]
    print("1. _toggle_preview: pausa main + instancia propia (sin set_voice).")

# ---- 2. _stop_preview: reanuda main si el preview lo pauso ----
s = t.find("def _stop_preview")
e = t.find("\ndef ", s + 10)
new_stop = '''def _stop_preview(self):
    old = getattr(self, "_preview_name", "")
    if getattr(self, "_preview_sapi", None) is not None:
        try:
            self._preview_sapi.Speak("", 2)
        except Exception:
            pass
    self._preview_playing = False
    self._preview_name = ""
    if getattr(self, "_preview_paused_main", False):
        self._preview_paused_main = False
        try:
            import time as _time
            self.engine.adapter.sapi.Resume()
            self._paused = False
            self._resume_at = _time.time()
            self.player_timer.start(100)
            self._set_player_icon(True, loading=False)
            self.statusBar().showMessage("Reanudando reproduccion...")
        except Exception:
            pass
    if old:
        self.preview_changed.emit(old, False)


'''
if s != -1 and e != -1 and e > s:
    t = t[:s] + new_stop + t[e:]
    print("2. _stop_preview: reanuda la reproduccion principal.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
