from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# ---- 1. Import QMediaPlayer y QAudioOutput ----
old_import = "from PySide6.QtCore import Qt, QTimer"
new_import = """from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput"""
if old_import in t and "QMediaPlayer" not in t:
    t = t.replace(old_import, new_import, 1)
    print("1. Imports de QMediaPlayer agregados.")

# ---- 2. Worker para sintetizar WAV en segundo plano ----
if "class SynthWorker" not in t:
    worker = '''class SynthWorker(QThread):
    ready = Signal(str)
    error = Signal(str)

    def __init__(self, engine, text, voice, rate, volume):
        super().__init__()
        self.engine = engine
        self.text = text
        self.voice = voice
        self.rate = rate
        self.volume = volume

    def run(self):
        try:
            import tempfile
            from pathlib import Path as _P
            tmp = str(_P(tempfile.gettempdir()) / "willpovoice_player.wav")
            self.engine.save_to_wav(
                text=self.text,
                output_path=tmp,
                voice_query=self.voice,
                rate=self.rate,
                volume=self.volume,
            )
            self.ready.emit(tmp)
        except Exception as exc:
            self.error.emit(str(exc))


'''
    anchor = t.find("def _connect_signals")
    if anchor != -1:
        t = t[:anchor] + worker + t[anchor:]
        print("2. SynthWorker agregado.")

# ---- 3. Inicializar QMediaPlayer en __init__ ----
old_init = "    self.player_timer = QTimer(self)"
new_init = """    self.player = QMediaPlayer(self)
    self.audio_out = QAudioOutput(self)
    self.player.setAudioOutput(self.audio_out)
    self.audio_out.setVolume(1.0)
    self._synth_worker = None
    self._media_ready = False
    self.player_timer = QTimer(self)"""
if old_init in t:
    t = t.replace(old_init, new_init, 1)
    print("3. QMediaPlayer inicializado.")

# ---- 4. Reemplazar _tick_player con señales de QMediaPlayer ----
old_tick = """def _tick_player(self):
    elapsed = -1.0
    state = -1
    try:
        st = self.engine.adapter.sapi.Status
        state = st.RunningState
        elapsed = max(0.0, float(st.AudioPosition)) / 1000.0
    except Exception:
        pass
    if not getattr(self, "_started", False):
        return
    if state == 1:
        self._saw_running = True
        if elapsed >= 0:
            self._seconds = elapsed
        else:
            self._seconds += 0.2
    else:
        self._seconds += 0.2
    self.time_cur.setText(self._fmt_time(self._seconds))
    est = max(1.0, getattr(self, "_est_seconds", 1.0))
    self.progress_slider.setValue(
        min(100, int(self._seconds / est * 100)))
    done = (getattr(self, "_saw_running", False) and state == 0
            and self._seconds > 0.5) or self._seconds >= est
    if done:
        self.player_timer.stop()
        self._started = False
        self._paused = False
        self.time_cur.setText(self._fmt_time(est))
        self.progress_slider.setValue(100)
        self._set_player_icon(False)"""

new_tick = """def _tick_player(self):
    pass

def _on_position_changed(self, pos):
    if not getattr(self, "_media_ready", False):
        return
    secs = pos / 1000.0
    self._seconds = secs
    self.time_cur.setText(self._fmt_time(secs))
    dur = self.player.duration()
    if dur > 0:
        pct = int(pos * 100 / dur)
        self.progress_slider.setValue(pct)

def _on_duration_changed(self, dur):
    if dur > 0:
        self.time_tot.setText(self._fmt_time(dur / 1000.0))
        self.progress_slider.setRange(0, 100)

def _on_media_status_changed(self, status):
    if int(status) == 7:
        self._started = False
        self._paused = False
        self._set_player_icon(False)
        self.statusBar().showMessage("Reproduccion terminada.")"""

if old_tick in t:
    t = t.replace(old_tick, new_tick, 1)
    print("4. _tick_player reemplazado por señales de QMediaPlayer.")

# ---- 5. Reemplazar speak_text para usar SynthWorker ----
old_speak = """def speak_text(self):
    try:
        text = self.text_edit.toPlainText().strip()
        if not text:
            self.statusBar().showMessage("Escribe un texto antes de reproducir.")
            return
        voice = self.voice_combo.currentData(Qt.ItemDataRole.UserRole)
        if voice:
            self.engine.select_voice(voice)
        self.engine.set_rate(self.rate_slider.value())
        self.engine.set_volume(self.volume_slider.value())
        self.engine.speak_async(text)
        self._add_to_history(text)
        self.settings["conv_today"] = int(self.settings.get("conv_today", 0)) + 1
        self.stat_conv.value_label.setText(str(self.settings["conv_today"]))
        words = len(text.split()) or 1
        factor = 1.0 + self.rate_slider.value() / 20.0
        self._est_seconds = words / (2.8 * factor) + 0.6
        self._seconds = 0
        self._started = True
        self._saw_running = False
        self._paused = False
        self.time_tot.setText(self._fmt_time(self._est_seconds))
        self.time_cur.setText("0:00")
        self.progress_slider.setValue(0)
        self.player_timer.start(200)
        self._set_player_icon(True)
        self.statusBar().showMessage("Reproduciendo...")
    except Exception as exc:
        QMessageBox.warning(self, "Error", f"No se pudo reproducir: {exc}")"""

new_speak = """def speak_text(self):
    try:
        text = self.text_edit.toPlainText().strip()
        if not text:
            self.statusBar().showMessage("Escribe un texto antes de reproducir.")
            return
        voice = self.voice_combo.currentData(Qt.ItemDataRole.UserRole)
        if voice:
            self.engine.select_voice(voice)
        self._add_to_history(text)
        self.settings["conv_today"] = int(self.settings.get("conv_today", 0)) + 1
        self.stat_conv.value_label.setText(str(self.settings["conv_today"]))
        self._seconds = 0
        self._started = True
        self._paused = False
        self._media_ready = False
        self.time_cur.setText("0:00")
        self.time_tot.setText("0:00")
        self.progress_slider.setValue(0)
        self._set_player_icon(True, loading=True)
        self.statusBar().showMessage("Preparando audio...")
        self._synth_worker = SynthWorker(
            self.engine, text, voice,
            self.rate_slider.value(), self.volume_slider.value()
        )
        self._synth_worker.ready.connect(self._on_synth_ready)
        self._synth_worker.error.connect(self._on_synth_error)
        self._synth_worker.start()
    except Exception as exc:
        QMessageBox.warning(self, "Error", f"No se pudo reproducir: {exc}")

def _on_synth_ready(self, wav_path):
    from PySide6.QtCore import QUrl
    self.player.setSource(QUrl.fromLocalFile(wav_path))
    self._media_ready = True
    self.player.play()
    self._set_player_icon(True, loading=False)
    self.statusBar().showMessage("Reproduciendo...")

def _on_synth_error(self, msg):
    self._set_player_icon(False)
    QMessageBox.warning(self, "Error", f"No se pudo sintetizar: {msg}")"""

if old_speak in t:
    t = t.replace(old_speak, new_speak, 1)
    print("5. speak_text usa SynthWorker + QMediaPlayer.")

# ---- 6. Reemplazar _player_play_clicked con QMediaPlayer ----
old_play = """def _player_play_clicked(self):
    if getattr(self, "_started", False) and not getattr(
            self, "_paused", False):
        try:
            self.engine.adapter.sapi.Pause()
        except Exception:
            pass
        self.player_timer.stop()
        self._paused = True
        self._set_player_icon(False)
        self.statusBar().showMessage("Reproduccion pausada.")
    elif getattr(self, "_paused", False):
        try:
            self.engine.adapter.sapi.Resume()
        except Exception:
            pass
        self.player_timer.start(200)
        self._paused = False
        self._set_player_icon(True)
        self.statusBar().showMessage("Reanudando reproduccion...")
    else:
        self.speak_text()"""

new_play = """def _player_play_clicked(self):
    if not getattr(self, "_media_ready", False):
        self.speak_text()
        return
    state = self.player.playbackState()
    if state == QMediaPlayer.PlaybackState.PlayingState:
        self.player.pause()
        self._paused = True
        self._set_player_icon(False)
        self.statusBar().showMessage("Reproduccion pausada.")
    else:
        self.player.play()
        self._paused = False
        self._set_player_icon(True)
        self.statusBar().showMessage("Reproduciendo...")"""

if old_play in t:
    t = t.replace(old_play, new_play, 1)
    print("6. _player_play_clicked usa QMediaPlayer.")

# ---- 7. Conectar señales de QMediaPlayer ----
old_connect = "    self.player_timer.timeout.connect(self._tick_player)"
new_connect = """    self.player_timer.timeout.connect(self._tick_player)
    self.player.positionChanged.connect(self._on_position_changed)
    self.player.durationChanged.connect(self._on_duration_changed)
    self.player.mediaStatusChanged.connect(self._on_media_status_changed)
    self.progress_slider.sliderMoved.connect(self._on_slider_moved)
    self.vol_slider.valueChanged.connect(self._on_volume_changed)"""

if old_connect in t:
    t = t.replace(old_connect, new_connect, 1)
    print("7. Señales de QMediaPlayer conectadas.")

# ---- 8. Agregar _on_slider_moved y _on_volume_changed ----
if "def _on_slider_moved" not in t:
    methods = """

def _on_slider_moved(self, pos):
    if getattr(self, "_media_ready", False):
        dur = self.player.duration()
        if dur > 0:
            self.player.setPosition(int(pos * dur / 100))

def _on_volume_changed(self, value):
    self.audio_out.setVolume(value / 100.0)

"""
    anchor = t.find("MainWindow._set_player_icon = _set_player_icon")
    if anchor != -1:
        t = t[:anchor] + methods + t[anchor:]
        print("8. Seek y volumen agregados.")

# ---- 9. Modificar _set_player_icon para spinner ----
old_icon = """def _set_player_icon(self, playing):
    self.player_play.icon.setPixmap(
        make_icon("pause" if playing else "play", TEXT, 15))"""

new_icon = """def _set_player_icon(self, playing, loading=False):
    if loading:
        self.player_play.icon.setPixmap(
            make_icon("loading", TEXT, 15))
    else:
        self.player_play.icon.setPixmap(
            make_icon("pause" if playing else "play", TEXT, 15))"""

if old_icon in t:
    t = t.replace(old_icon, new_icon, 1)
    print("9. _set_player_icon soporta loading.")

# ---- 10. Agregar icono de loading a make_icon ----
if "elif kind == \"loading\":" not in t:
    old_make = "    elif kind == \"x\":"
    new_make = """    elif kind == "loading":
        path = QPainterPath()
        path.arcMoveTo(3, 3, 12, 12, 0, 270)
        painter.setPen(QPen(QColor(color), 2))
        painter.drawPath(path)
    elif kind == "x":"""
    if old_make in t:
        t = t.replace(old_make, new_make, 1)
        print("10. Icono 'loading' agregado a make_icon.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
