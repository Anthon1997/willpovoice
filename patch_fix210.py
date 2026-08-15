from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# ---- 1. Insertar PreviewWorker + handler antes de _toggle_preview ----
anchor = t.find("def _toggle_preview")
worker_code = '''class PreviewWorker(QThread):
    \"\"\"Previsualizacion de voz en hilo de fondo (no congela UI).\"\"\"

    def __init__(self, description):
        super().__init__()
        self._desc = description
        self._stop = False

    def request_stop(self):
        self._stop = True

    def run(self):
        import pythoncom
        import win32com.client
        pythoncom.CoInitialize()
        try:
            sapi = win32com.client.Dispatch("SAPI.SpVoice")
            tok = None
            for tk in sapi.GetVoices():
                if tk.GetDescription() == self._desc:
                    tok = tk
                    break
            if tok is not None:
                sapi.Voice = tok
                sapi.Speak("Hola esta es mi voz", 1)
                saw = False
                for _ in range(300):
                    if self._stop:
                        sapi.Speak("", 2)
                        break
                    st = int(sapi.Status.RunningState)
                    if st == 2:
                        saw = True
                    elif saw:
                        break
                    self.msleep(100)
        except Exception:
            pass
        finally:
            pythoncom.CoUninitialize()


def _on_preview_finished(self):
    worker = self.sender()
    if getattr(self, "_preview_worker", None) is not worker:
        return
    self._preview_worker = None
    self._preview_playing = False
    old = getattr(self, "_preview_name", "")
    self._preview_name = ""
    if old:
        self.preview_changed.emit(old, False)
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


'''
if anchor != -1 and "class PreviewWorker" not in t:
    t = t[:anchor] + worker_code + t[anchor:]
    print("1. PreviewWorker + _on_preview_finished insertados.")

# ---- 2. _toggle_preview sin COM en hilo principal ----
s = t.find("def _toggle_preview")
e = t.find("\ndef ", s + 10)
new_toggle = '''def _toggle_preview(self, name):
    if getattr(self, "_preview_name", "") == name and getattr(
            self, "_preview_playing", False):
        w = getattr(self, "_preview_worker", None)
        if w is not None:
            w.request_stop()
        return
    old_w = getattr(self, "_preview_worker", None)
    if old_w is not None:
        old_w.request_stop()
        self._preview_worker = None
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
    worker = PreviewWorker(name)
    worker.finished.connect(self._on_preview_finished)
    self._preview_worker = worker
    self._preview_name = name
    self._preview_playing = True
    self.preview_changed.emit(name, True)
    self.statusBar().showMessage(f"Previsualizando: {name}")
    worker.start()


'''
if s != -1 and e != -1 and e > s:
    t = t[:s] + new_toggle + t[e:]
    print("2. _toggle_preview sin COM en hilo principal.")

# ---- 3. _stop_preview delega al worker ----
s = t.find("def _stop_preview")
e = t.find("\ndef ", s + 10)
new_stop = '''def _stop_preview(self):
    w = getattr(self, "_preview_worker", None)
    if w is not None:
        w.request_stop()


'''
if s != -1 and e != -1 and e > s:
    t = t[:s] + new_stop + t[e:]
    print("3. _stop_preview delega al worker.")

# ---- 4. _check_preview_end inerte (el worker avisa solo) ----
s = t.find("def _check_preview_end")
e = t.find("\ndef ", s + 10)
if s != -1 and e != -1 and e > s:
    t = t[:s] + "def _check_preview_end(self):\n    return\n\n\n" + t[e:]
    print("4. _check_preview_end inerte.")

p.write_text(t, encoding="utf-8")

for name in ["_on_preview_finished"]:
    if f"def {name}(" in t and f"MainWindow.{name} = {name}" not in t:
        t += f"\nMainWindow.{name} = {name}\n"
p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
