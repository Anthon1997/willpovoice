from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")
log = []

# 1) Congelar el tick mientras el usuario arrastra la barra
old = """    if getattr(self, "_paused", False):
        return
    try:
        st = self.engine.adapter.sapi.Status"""
new = """    if getattr(self, "_paused", False):
        return
    if getattr(self, "_seeking", False):
        return
    try:
        st = self.engine.adapter.sapi.Status"""
if old in t:
    t = t.replace(old, new, 1)
    log.append("1 freeze tick")

# 2) Seek real: re-sintetizar desde el offset de texto
old = """def _on_slider_released(self):
    self._seeking = False
    self._on_slider_moved(self.progress_slider.value())"""
new = '''def _on_slider_released(self):
    self._seeking = False
    if not getattr(self, "_started", False):
        return
    texto = getattr(self, "_texto_para_ratio", "") or \\
        self.text_edit.toPlainText()
    if not texto:
        return
    ratio = self.progress_slider.value() / 100.0
    off = int(ratio * len(texto))
    if 0 < off < len(texto):
        nxt = texto.find(" ", off)
        off = (nxt + 1) if nxt != -1 else off
    off = max(0, min(off, len(texto) - 1))
    sub = texto[off:]
    if not sub.strip():
        return
    try:
        self.engine.stop()
    except Exception:
        pass
    import time as _time
    self._resume_offset = off
    self._saw_running = False
    self._paused = False
    self._resume_at = _time.time()
    self._seconds = ratio * max(1.0, getattr(self, "_est_seconds", 1.0))
    self.engine.speak_async(sub)
    self.player_timer.start(100)
    self._set_player_icon(True, loading=False)
    self.statusBar().showMessage(
        f"Reproduciendo desde {self._fmt_time(self._seconds)}")'''
if old in t:
    t = t.replace(old, new, 1)
    log.append("2 seek real")

p.write_text(t, encoding="utf-8", newline="\n")
print("SEEK:", log)
try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as ex:
    print("ERROR:", ex.lineno, ex.msg)
