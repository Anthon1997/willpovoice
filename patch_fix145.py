from pathlib import Path
import re, ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# ---- 1. RECOPILACION ----
for m in ("player_play.clicked.connect", "def _tick_player",
          "start(200)", "def stop_speech"):
    print(f"--- {m!r} indice:", t.find(m))

# ---- 2. Icono pause en make_icon ----
if '"pause"' not in t:
    old_else = """    else:
        p.setBrush(QColor(color))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(int(s * 0.3), int(s * 0.3), int(s * 0.4), int(s * 0.4))"""
    new_pause = """    elif kind == "pause":
        p.setBrush(QColor(color))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(int(s * 0.3), int(s * 0.25), int(s * 0.14), int(s * 0.5), 2, 2)
        p.drawRoundedRect(int(s * 0.56), int(s * 0.25), int(s * 0.14), int(s * 0.5), 2, 2)
""" + old_else
    t = t.replace(old_else, new_pause, 1)
    print("2. Icono pause agregado.")

# ---- 3. Conexion toggle del play del reproductor ----
old_conn = "    self.player_play.clicked.connect(self.speak_text)"
new_conn = "    self.player_play.clicked.connect(self._player_play_clicked)"
if old_conn in t:
    t = t.replace(old_conn, new_conn, 1)
    print("3. Play del reproductor con toggle.")

# ---- 4. Icono activo al reproducir ----
old_play = """        self.player_timer.start(200)
        self.statusBar().showMessage("Reproduciendo...")"""
new_play = """        self.player_timer.start(200)
        self._set_player_icon(True)
        self.statusBar().showMessage("Reproduciendo...")"""
if old_play in t:
    t = t.replace(old_play, new_play, 1)
    print("4. Icono pausa al reproducir.")

# ---- 5. Icono play al terminar ----
old_done = """    if done:
        self.player_timer.stop()
        self._started = False
        self.time_cur.setText(self._fmt_time(est))
        self.progress_slider.setValue(100)"""
new_done = old_done + "\n        self._set_player_icon(False)"
if old_done in t:
    t = t.replace(old_done, new_done, 1)
    print("5. Icono play al terminar.")

# ---- 6. Icono play al detener ----
old_stop = """        self.player_timer.stop()
        self._seconds = 0
        self._started = False"""
new_stop = """        self.player_timer.stop()
        self._seconds = 0
        self._started = False
        self._set_player_icon(False)"""
if old_stop in t:
    t = t.replace(old_stop, new_stop, 1)
    print("6. Icono play al detener.")

# ---- 7. Metodos nuevos ----
if "def _player_play_clicked" not in t:
    t += '''

def _player_play_clicked(self):
    if getattr(self, "_started", False):
        self._pause_playback()
    else:
        self.speak_text()


def _pause_playback(self):
    try:
        self.engine.stop()
    except Exception:
        pass
    self.player_timer.stop()
    self._started = False
    self._set_player_icon(False)
    self.statusBar().showMessage("Reproduccion pausada.")


def _set_player_icon(self, playing):
    self.player_play.icon.setPixmap(
        make_icon("pause" if playing else "play", TEXT, 15))


MainWindow._player_play_clicked = _player_play_clicked
MainWindow._pause_playback = _pause_playback
MainWindow._set_player_icon = _set_player_icon
'''
    print("7. Metodos toggle agregados.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
