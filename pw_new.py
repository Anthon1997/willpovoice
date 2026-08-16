class PreviewWorker(QThread):
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


