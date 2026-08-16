from pathlib import Path
import re, ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")
log = []

# ============ A) PreviewWorker persistente ============
s = t.find("class PreviewWorker")
e = t.find("\ndef _check_preview_end")
if s != -1 and e != -1 and "preview_done" not in t[s:e]:
    new = '''class PreviewWorker(QThread):
    """Hilo UNICO y persistente: reutiliza una instancia SAPI."""
    preview_done = Signal(str)

    def __init__(self):
        super().__init__()
        import queue
        self._q = queue.Queue()
        self._stopflag = False

    def request(self, desc):
        self._stopflag = True
        while not self._q.empty():
            try:
                self._q.get_nowait()
            except Exception:
                break
        self._stopflag = False
        self._q.put(desc)

    def request_stop(self):
        self._stopflag = True
        while not self._q.empty():
            try:
                self._q.get_nowait()
            except Exception:
                break

    def shutdown(self):
        self.request_stop()
        self._q.put(None)

    def run(self):
        import pythoncom
        import win32com.client
        import queue as _q
        pythoncom.CoInitialize()
        sapi = None
        try:
            sapi = win32com.client.Dispatch("SAPI.SpVoice")
        except Exception:
            sapi = None
        while True:
            try:
                item = self._q.get(timeout=0.2)
            except _q.Empty:
                continue
            if item is None:
                break
            try:
                if sapi is not None:
                    tok = None
                    for tk in sapi.GetVoices():
                        if tk.GetDescription() == item:
                            tok = tk
                            break
                    if tok is not None:
                        sapi.Voice = tok
                        sapi.Speak("Hola esta es mi voz", 1)
                        saw = False
                        for _ in range(300):
                            if self._stopflag:
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
            self.preview_done.emit(item)
        try:
            pythoncom.CoUninitialize()
        except Exception:
            pass


def _get_preview_worker(self):
    w = getattr(self, "_preview_worker", None)
    if w is None:
        w = PreviewWorker()
        w.preview_done.connect(self._on_preview_finished)
        self._preview_worker = w
        w.start()
    return w


def _on_preview_finished(self, name):
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


def _toggle_preview(self, name):
    if getattr(self, "_preview_name", "") == name and getattr(
            self, "_preview_playing", False):
        self._get_preview_worker().request_stop()
        return
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
    w = self._get_preview_worker()
    self._preview_name = name
    self._preview_playing = True
    self.preview_changed.emit(name, True)
    self.statusBar().showMessage(f"Previsualizando: {name}")
    w.request(name)


def _stop_preview(self):
    w = getattr(self, "_preview_worker", None)
    if w is not None:
        w.request_stop()

'''
    t = t[:s] + new + t[e:]
    log.append("A preview persistente")

ce = t.find("def closeEvent")
if ce != -1 and "_preview_worker" not in t[ce:ce + 400]:
    nl = t.find("\n", ce)
    t = (t[:nl + 1] +
         "    w = getattr(self, \"_preview_worker\", None)\n"
         "    if w is not None:\n"
         "        w.shutdown()\n"
         "        w.wait(2000)\n" + t[nl + 1:])
    log.append("A2 closeEvent shutdown")

# ============ B) Idiomas: orden + corona + default ============
t2 = re.sub(r'self\.lang_combo\.addItems\(\[[^\]]*\]\)',
            'self.lang_combo.addItems(["Multilingüe Premium", '
            '"Español (España)", "Inglés (EEUU)", "Todos"])', t, count=1)
if t2 != t:
    t = t2; log.append("B1 orden")

pat = re.compile(
    r'self\.lang_combo\.setItemIcon\(0.*?self\.lang_combo\.setStyleSheet', re.S)
rep = ('self.lang_combo.setItemIcon(0, QIcon(make_icon("crown", "#f5b544", 16)))\n'
       '        self.lang_combo.setItemIcon(1, QIcon(self._flag_pixmap("es")))\n'
       '        self.lang_combo.setItemIcon(2, QIcon(self._flag_pixmap("us")))\n'
       '        self.lang_combo.setItemIcon(3, QIcon(self._flag_pixmap("world")))\n'
       '        self.lang_combo.currentIndexChanged.connect(\n'
       '            lambda _i: self._on_lang_changed())\n'
       '        self.lang_combo.setCurrentIndex(0)\n'
       '        self.lang_combo.setStyleSheet')
if pat.search(t):
    t = pat.sub(lambda m: rep, t, count=1); log.append("B2 corona+default")

# ============ C) Metodos de filtrado ============
if "def _voice_lang" not in t:
    anchor = "def _rebuild_cards(self):"
    methods = '''def _voice_lang(self, name):
    low = name.lower()
    if "multilingual" in low:
        return "multi"
    if "spanish" in low or "espa" in low or "es-" in low or "(es)" in low:
        return "es"
    if "english" in low or "ingl" in low or "en-" in low or "(en)" in low:
        return "en"
    return "otro"


def _lang_filtered(self, names):
    lang = self.lang_combo.currentText()
    out = []
    for name in names:
        vl = self._voice_lang(name)
        if lang.startswith("Espa") and vl != "es":
            continue
        if lang.startswith("Ingl") and vl != "en":
            continue
        if lang.startswith("Multiling") and not self._is_premium(name):
            continue
        out.append(name)
    return out


def _refill_combo(self):
    cur = self.voice_combo.currentData(Qt.ItemDataRole.UserRole)
    names = self._lang_filtered(getattr(self, "_voices", []))
    self.voice_combo.blockSignals(True)
    self.voice_combo.clear()
    for v in names:
        self.voice_combo.addItem(self._display_voice_name(v))
        idx = self.voice_combo.count() - 1
        self.voice_combo.setItemData(idx, v, Qt.ItemDataRole.UserRole)
    self.voice_combo.blockSignals(False)
    if cur in names:
        self.voice_combo.setCurrentIndex(names.index(cur))
    elif names:
        self.voice_combo.setCurrentIndex(0)
    self._icon_queue = list(range(self.voice_combo.count()))
    if hasattr(self, "_icon_timer"):
        self._icon_timer.start(60)


def _on_lang_changed(self):
    self._refill_combo()
    self._rebuild_cards()


'''
    if anchor in t:
        t = t.replace(anchor, methods + anchor, 1); log.append("C metodos")

# ============ D) Filtro dentro de _rebuild_cards ============
old = """        if q and q not in name.lower():
            continue
        self._rec_names.append(name)"""
new = """        if q and q not in name.lower():
            continue
        vl = self._voice_lang(name)
        lang = self.lang_combo.currentText()
        if lang.startswith("Espa") and vl != "es":
            continue
        if lang.startswith("Ingl") and vl != "en":
            continue
        if lang.startswith("Multiling") and not premium:
            continue
        self._rec_names.append(name)"""
if old in t and 'lang.startswith("Espa")' not in t.split("def _rebuild_cards")[1].split("def _append")[0]:
    t = t.replace(old, new, 1); log.append("D filtro tarjetas")

# ============ E) _load_voices con refill ============
old = """        self._voices = voices
        self.voice_combo.blockSignals(True)
        self.voice_combo.clear()
        for v in voices:
            self.voice_combo.addItem(self._display_voice_name(v))
            idx = self.voice_combo.count() - 1
            self.voice_combo.setItemData(idx, v, Qt.ItemDataRole.UserRole)
        last = self.settings.get("last_voice", "")
        if last in voices:
            self._select_voice(last)
        elif voices:
            pref = next((v for v in voices if "SeraphinaMultilingual" in v),
                        voices[0])
            self._select_voice(pref)
        self.voice_combo.blockSignals(False)
        self.stat_voices.value_label.setText(f"{len(voices)}+")"""
new = """        self._voices = voices
        self._refill_combo()
        names = self._lang_filtered(voices)
        last = self.settings.get("last_voice", "")
        if last in names:
            self._select_voice(last)
        elif names:
            pref = next((v for v in names if "SeraphinaMultilingual" in v),
                        names[0])
            self._select_voice(pref)
        self.stat_voices.value_label.setText(f"{len(voices)}+")"""
if old in t:
    t = t.replace(old, new, 1); log.append("E load_voices")

# ============ F) Asignaciones ============
for m in ["_get_preview_worker", "_voice_lang", "_lang_filtered",
          "_refill_combo", "_on_lang_changed"]:
    tag = f"MainWindow.{m} = {m}"
    if tag not in t:
        t += f"\n{tag}\n"; log.append("F " + m)

p.write_text(t, encoding="utf-8")
print("APLICADO:", log)
try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as ex:
    print("ERROR:", ex.lineno, ex.msg)
