from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")
log = []

# ============ 1) Reemplazar _speak_chat_text con maquina de estados ============
s = t.find("def _speak_chat_text(self, txt):")
e = t.find("MainWindow._speak_chat_text = _speak_chat_text")
if s == -1 or e == -1:
    raise SystemExit("ERROR: _speak_chat_text no encontrado")
e += len("MainWindow._speak_chat_text = _speak_chat_text")

new_block = '''def _speak_head_svg(size=14):
    """Cabeza parlante (Escuchar)."""
    from PySide6.QtSvg import QSvgRenderer
    from PySide6.QtCore import QByteArray
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
        'fill="none" stroke="#ffffff" stroke-width="1.7" '
        'stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M12 2a7 7 0 0 0-7 7v2c0 1.5-.6 2.5-1 3v2a1 1 0 0 0 1 1h2v4a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2v-4h2a1 1 0 0 0 1-1v-2c-.4-.5-1-1.5-1-3V9a7 7 0 0 0-7-7z"/>'
        '<path d="M18 10a2 2 0 1 1 4 0"/>'
        '<path d="M19 7a5 5 0 0 1 0 6"/>'
        '</svg>')
    r = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    pm = QPixmap(size, size); pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm); r.render(p); p.end()
    return pm


def _pause_svg(size=14):
    from PySide6.QtSvg import QSvgRenderer
    from PySide6.QtCore import QByteArray
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
           'fill="#ffffff">'
           '<rect x="6" y="5" width="4" height="14" rx="1"/>'
           '<rect x="14" y="5" width="4" height="14" rx="1"/></svg>')
    r = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    pm = QPixmap(size, size); pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm); r.render(p); p.end()
    return pm


def _play_svg(size=14):
    from PySide6.QtSvg import QSvgRenderer
    from PySide6.QtCore import QByteArray
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
           'fill="#ffffff"><path d="M7 4l12 8-12 8z"/></svg>')
    r = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    pm = QPixmap(size, size); pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm); r.render(p); p.end()
    return pm


def _spinner_pixmap(size=14, angle=0):
    """Arco que rota (spinner de carga)."""
    from PySide6.QtCore import QRectF
    from PySide6.QtGui import QPen
    pm = QPixmap(size, size); pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.translate(size / 2, size / 2)
    p.rotate(angle)
    pen = QPen(QColor("#cfe3ff"))
    pen.setWidthF(max(1.2, size / 11))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    p.setPen(pen)
    margin = max(1.5, size / 10)
    r = QRectF(-size / 2 + margin, -size / 2 + margin,
               size - 2 * margin, size - 2 * margin)
    p.drawArc(r, 90 * 16, 270 * 16)
    p.end()
    return pm


class _SpinnerWidget(QLabel):
    def __init__(self, size=13, parent=None):
        super().__init__(parent)
        self._size = size
        self._angle = 0
        self.setFixedSize(size + 6, size + 6)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(35)
        self._tick()

    def _tick(self):
        self._angle = (self._angle + 18) % 360
        self.setPixmap(_spinner_pixmap(self._size, self._angle))

    def stop(self):
        try:
            self._timer.stop()
        except Exception:
            pass


def _toggle_speak_btn(self, btn, text):
    """Maquina de estados: ESCUCHAR -> SPINNER -> PAUSA <-> PLAY -> ESCUCHAR."""
    # Inicializar registro si no existe
    if not hasattr(self, "_chat_speakers"):
        self._chat_speakers = {}
    state = self._chat_speakers.get(id(btn), {}).get("state", "idle")

    # ===== IDLE: iniciar narracion =====
    if state == "idle":
        self._chat_speakers[id(btn)] = {
            "state": "loading", "text": text,
            "spinner": None, "poll": None, "was_paused": False,
        }
        btn.setIcon(QIcon())
        sp = _SpinnerWidget(13, btn)
        btn.layout() if btn.layout() else None
        btn.setText("")
        self._chat_speakers[id(btn)]["spinner"] = sp
        # Centrar spinner en el boton
        g = btn.geometry()
        sp.setParent(btn)
        sp.move((btn.width() - sp.width()) // 2,
                (btn.height() - sp.height()) // 2)
        sp.raise_()
        sp.show()

        eng = getattr(self, "engine", None)
        if eng is None:
            self._chat_reset_btn(btn); return
        try:
            try:
                eng.select_voice("Seraphina")
            except Exception:
                pass
            eng.speak_async(text)
        except Exception as exc:
            print(f"TTS fallo: {exc}")
            self._chat_reset_btn(btn); return

        # Quitar spinner y pasar a PAUSA tras ~400ms (arranca el audio)
        def _to_pausing():
            entry = self._chat_speakers.get(id(btn))
            if not entry: return
            sp = entry.get("spinner")
            if sp is not None:
                sp.stop(); sp.setParent(None); sp.deleteLater()
            entry["spinner"] = None
            entry["state"] = "speaking"
            btn.setIcon(QIcon(_pause_svg(13)))
            btn.setText("Pausa")
            # Poller: detecta fin del audio via SAPI Status
            poll = QTimer(btn)
            poll.timeout.connect(lambda: self._chat_poll_sapi(btn))
            poll.start(250)
            entry["poll"] = poll
        QTimer.singleShot(450, _to_pausing)
        self.statusBar().showMessage("Hablando con Seraphina", 2500)
        return

    # ===== SPEAKING (PAUSA visible): pausar =====
    if state == "speaking":
        eng = getattr(self, "engine", None)
        try:
            if eng and eng.adapter and eng.adapter.sapi is not None:
                eng.adapter.sapi.Pause()
        except Exception:
            pass
        self._chat_speakers[id(btn)]["state"] = "paused"
        self._chat_speakers[id(btn)]["was_paused"] = True
        btn.setIcon(QIcon(_play_svg(13)))
        btn.setText("Reanudar")
        return

    # ===== PAUSED (PLAY visible): reanudar =====
    if state == "paused":
        eng = getattr(self, "engine", None)
        try:
            if eng and eng.adapter and eng.adapter.sapi is not None:
                eng.adapter.sapi.Resume()
        except Exception:
            pass
        self._chat_speakers[id(btn)]["state"] = "speaking"
        btn.setIcon(QIcon(_pause_svg(13)))
        btn.setText("Pausa")
        return


def _chat_poll_sapi(self, btn):
    """Revisa si el audio termino para volver a IDLE."""
    entry = self._chat_speakers.get(id(btn))
    if not entry:
        return
    eng = getattr(self, "engine", None)
    if eng is None:
        self._chat_reset_btn(btn); return
    try:
        sapi = eng.adapter.sapi
        rs = sapi.Status.RunningState  # 0=done 1=waiting 2=speaking
    except Exception:
        rs = 0
    if rs == 0:  # termino
        self._chat_reset_btn(btn)


def _chat_reset_btn(self, btn):
    """Vuelve el boton a estado ESCUCHAR (idle) y limpia recursos."""
    entry = self._chat_speakers.get(id(btn))
    if not entry: return
    sp = entry.get("spinner")
    if sp is not None:
        try:
            sp.stop(); sp.setParent(None); sp.deleteLater()
        except Exception:
            pass
    poll = entry.get("poll")
    if poll is not None:
        try:
            poll.stop()
        except Exception:
            pass
    self._chat_speakers[id(btn)] = {"state": "idle"}
    btn.setIcon(QIcon(_speak_head_svg(13)))
    btn.setText("Escuchar")


MainWindow._toggle_speak_btn = _toggle_speak_btn
MainWindow._chat_poll_sapi = _chat_poll_sapi
MainWindow._chat_reset_btn = _chat_reset_btn
MainWindow._speak_chat_text = _toggle_speak_btn'''

t = t[:s] + new_block + t[e:]
log.append("maquina de estados")

# ============ 2) Cambiar el click del boton a _toggle_speak_btn ============
old_click = ('            b_speak.clicked.connect(\n'
             '                lambda _=False, txt=text: self._speak_chat_text(txt))')
new_click = ('            b_speak.clicked.connect(\n'
             '                lambda _=False, btn=b_speak, txt=text: self._toggle_speak_btn(btn, txt))')
if old_click in t:
    t = t.replace(old_click, new_click, 1)
    log.append("click -> toggle")
else:
    print("WARN: click de b_speak no encontrado tal cual")

# ============ 3) Auto-habla de respuestas cortas usa el mismo flujo ============
old_auto = ('    if ad is not None and len(response or "") <= 500:\n'
            '        try:\n'
            '            _self = self  # captura para lambda\n'
            '            self._speak_chat_text(response)')
new_auto = ('    # Auto-habla ya la maneja _toggle_speak_btn en el boton')
if old_auto in t:
    t = t.replace(old_auto, new_auto, 1)
    log.append("auto-habla delegada")

mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
assert "MainWindow._toggle_speak_btn = _toggle_speak_btn" in t
print("OK", log)
