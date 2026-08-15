from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# ---- 1. Import multimedia a nivel de modulo ----
imp = "from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput"
head_end = t.find("class ")
if imp not in t[:head_end]:
    anchor = t.find("from PySide6.QtGui import")
    if anchor != -1:
        eol = t.find("\n", anchor) + 1
        t = t[:eol] + imp + "\n" + t[eol:]
        print("1. Import QMediaPlayer/QAudioOutput a nivel de modulo.")

# ---- 2. SynthWorker: metodo correcto + normalizacion ----
old_run = """            self.engine.save_to_wav(
                text=self.text,
                output_path=tmp,
                voice_query=self.voice,
                rate=self.rate,
                volume=self.volume,
            )"""
new_run = """            from core.text_normalizer import (
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
            )"""
if old_run in t:
    t = t.replace(old_run, new_run, 1)
    print("2. SynthWorker: save_text_to_wav + normalizacion.")

# ---- 3. Spinner de carga dibujado inline (sin depender de make_icon) ----
old_icon = """def _set_player_icon(self, playing, loading=False):
    if loading:
        self.player_play.icon.setPixmap(
            make_icon("loading", TEXT, 15))
    else:
        self.player_play.icon.setPixmap(
            make_icon("pause" if playing else "play", TEXT, 15))"""
new_icon = """def _set_player_icon(self, playing, loading=False):
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
if old_icon in t:
    t = t.replace(old_icon, new_icon, 1)
    print("3. Spinner de carga dibujado inline.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
