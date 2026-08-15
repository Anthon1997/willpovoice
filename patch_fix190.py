from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# ---- 1. SynthWorker: seleccionar voz por nombre en su propia instancia ----
old_voice = """            tmp = str(_P(tempfile.gettempdir()) / "willpovoice_player.wav")
            adapter = self.engine.adapter
            if self.voice:
                adapter.set_voice(self.voice)
            sapi = win32com.client.Dispatch("SAPI.SpVoice")
            try:
                sapi.Voice = adapter.sapi.Voice
            except Exception:
                pass
            sapi.Rate = max(-10, min(10, int(self.rate)))"""
new_voice = """            tmp = str(_P(tempfile.gettempdir()) / "willpovoice_player.wav")
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
            sapi.Rate = max(-10, min(10, int(self.rate)))"""
if old_voice in t:
    t = t.replace(old_voice, new_voice, 1)
    print("1. SynthWorker selecciona voz por nombre (sin copiar token).")

# ---- 2. speak_text: pasar el texto visible para emparejar la voz ----
old_st = """        voice = self.voice_combo.currentData(Qt.ItemDataRole.UserRole)
        if voice:
            self.engine.select_voice(voice)"""
new_st = """        voice_data = self.voice_combo.currentData(Qt.ItemDataRole.UserRole)
        voice_text = self.voice_combo.currentText().strip()
        if voice_data:
            self.engine.select_voice(voice_data)"""
if old_st in t:
    t = t.replace(old_st, new_st, 1)
    print("2. speak_text captura voz visible para SynthWorker.")

old_sw = """        self._synth_worker = SynthWorker(
            self.engine, text, voice,
            self.rate_slider.value(), self.volume_slider.value()
        )"""
new_sw = """        self._synth_worker = SynthWorker(
            self.engine, text, voice_text,
            self.rate_slider.value(), self.volume_slider.value()
        )"""
if old_sw in t:
    t = t.replace(old_sw, new_sw, 1)
    print("3. SynthWorker recibe nombre visible de la voz.")

# ---- 4. Spinner animado (gira con QTimer) ----
old_icon = """def _set_player_icon(self, playing, loading=False):
    if loading:
        from PySide6.QtGui import QPainter, QPen
        from PySide6.QtCore import QRectF
        pix = QPixmap(16, 16)
        pix.fill(Qt.GlobalColor.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(QPen(QColor(TEXT), 2))
        p.drawArc(QRectF(1, 1, 14, 14), 30 * 16, 300 * 16)
        p.end()
        self.player_play.icon.setPixmap(pix)
    else:
        self.player_play.icon.setPixmap(
            make_icon("pause" if playing else "play", TEXT, 15))"""
new_icon = """def _set_player_icon(self, playing, loading=False):
    if loading:
        self._spin_angle = 0
        if getattr(self, "_spin_timer", None) is None:
            self._spin_timer = QTimer(self)
            self._spin_timer.timeout.connect(self._spin_tick)
        self._draw_spin()
        self._spin_timer.start(60)
    else:
        st = getattr(self, "_spin_timer", None)
        if st is not None:
            st.stop()
        self.player_play.icon.setPixmap(
            make_icon("pause" if playing else "play", TEXT, 15))

def _spin_tick(self):
    self._spin_angle = (getattr(self, "_spin_angle", 0) + 40) % 360
    self._draw_spin()

def _draw_spin(self):
    from PySide6.QtGui import QPainter, QPen
    from PySide6.QtCore import QRectF
    pix = QPixmap(16, 16)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(QPen(QColor(TEXT), 2))
    p.drawArc(QRectF(1, 1, 14, 14),
              getattr(self, "_spin_angle", 0) * 16, 300 * 16)
    p.end()
    self.player_play.icon.setPixmap(pix)"""
if old_icon in t:
    t = t.replace(old_icon, new_icon, 1)
    print("4. Spinner animado con QTimer.")

# ---- 5. Asignar nuevos metodos ----
anchor = "MainWindow._on_synth_error = _on_synth_error"
extra = """MainWindow._on_synth_error = _on_synth_error
MainWindow._spin_tick = _spin_tick
MainWindow._draw_spin = _draw_spin"""
if anchor in t and "MainWindow._spin_tick" not in t:
    t = t.replace(anchor, extra, 1)
    print("5. Metodos de spinner asignados.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
