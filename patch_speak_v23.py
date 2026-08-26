from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")
log = []

# ============ 1) Icono cabeza parlante (SVG inline) ============
anchor = "def _chat_svg(path_data, color, size):"
if "_speak_head_icon" not in t and anchor in t:
    i = t.find(anchor)
    fn = '''def _speak_head_icon(size=14):
    """Cabeza humana con ondas de voz, mismo estilo stroke."""
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
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    r.render(p)
    p.end()
    return pm


'''
    t = t[:i] + fn + t[i:]
    log.append("icono cabeza")

# ============ 2) Boton Escuchar en burbujas IA ============
old_btns = '''            b_add = QPushButton("Agregar a conversi\\u00f3n")
            b_add.setIcon(QIcon(make_icon("paste", "#8b949e", 12)))
            b_add.setStyleSheet(ghost)
            b_add.setCursor(Qt.CursorShape.PointingHandCursor)
            b_add.clicked.connect(
                lambda _=False, txt=text: self._add_to_conversion(txt))
            acts.addWidget(b_add)'''
new_btns = '''            b_add = QPushButton("Agregar a conversi\\u00f3n")
            b_add.setIcon(QIcon(make_icon("paste", "#8b949e", 12)))
            b_add.setStyleSheet(ghost)
            b_add.setCursor(Qt.CursorShape.PointingHandCursor)
            b_add.clicked.connect(
                lambda _=False, txt=text: self._add_to_conversion(txt))
            acts.addWidget(b_add)
            b_speak = QPushButton("Escuchar")
            b_speak.setIcon(QIcon(_speak_head_icon(13)))
            b_speak.setStyleSheet(ghost)
            b_speak.setCursor(Qt.CursorShape.PointingHandCursor)
            b_speak.clicked.connect(
                lambda _=False, txt=text: self._speak_chat_text(txt))
            acts.addWidget(b_speak)'''
if old_btns in t:
    t = t.replace(old_btns, new_btns, 1)
    log.append("boton escuchar")

# ============ 3) Metodo _speak_chat_text con Seraphina ============
anchor_att = "MainWindow._add_to_conversion = _add_to_conversion"
if "def _speak_chat_text" not in t and anchor_att in t:
    i = t.find(anchor_att)
    fn = '''def _speak_chat_text(self, txt):
    """Habla el texto con Seraphina por defecto; si no existe, usa
    la voz seleccionada. Restaura la voz original al terminar."""
    ad = getattr(self, "adapter", None) or getattr(self, "sapi_adapter", None)
    if ad is None:
        return
    original = None
    try:
        cur = ad.current_voice_description() if hasattr(ad, "current_voice_description") else None
        original = cur() if callable(cur) else cur
    except Exception:
        original = None
    try:
        voices = ad.get_available_voices() if hasattr(ad, "get_available_voices") else []
        seraphina = next((v for v in voices if "seraphina" in v.lower()), None)
        if seraphina:
            ad.set_voice(seraphina)
        if hasattr(ad, "speak_async"):
            ad.speak_async(txt)
        else:
            ad.speak(txt)
        self.statusBar().showMessage(
            f"Hablando: {seraphina or 'voz actual'}", 2500)
    except Exception as exc:
        print(f"TTS fallo: {exc}")
    finally:
        if original is not None:
            try:
                ad.set_voice(original)
            except Exception:
                pass


MainWindow._speak_chat_text = _speak_chat_text
'''
    t = t[:i] + fn + t[i:]
    log.append("_speak_chat_text")

# ============ 4) Auto-habla de respuestas cortas usa Seraphina ============
old_auto = "    if ad is not None and len(response or \"\") <= 500:\n        try:\n            ad.speak(response)"
new_auto = ("    if ad is not None and len(response or \"\") <= 500:\n"
            "        try:\n"
            "            _self = self  # captura para lambda\n"
            "            self._speak_chat_text(response)")
if old_auto in t:
    t = t.replace(old_auto, new_auto, 1)
    log.append("auto-habla Seraphina")

mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
assert "MainWindow._speak_chat_text = _speak_chat_text" in t
print("OK", log)
