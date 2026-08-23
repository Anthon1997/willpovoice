from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")
log = []

# 1) El fondo siempre llena el area (sin costuras)
old_outer = '''        self._chat_bg.setGeometry(0, 0, w, h)
        self._chat_bg.setPixmap(
            self._chat_bg_pix.scaled(
                w, h, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation))'''
new_outer = '''        self._chat_bg.setGeometry(0, 0, w, h)
        self._chat_bg.setPixmap(self._chat_bg_pix)
        self._chat_bg.setScaledContents(True)'''
if old_outer in t:
    t = t.replace(old_outer, new_outer, 1)
    log.append("scaled contents")

# 2) Referencia a la pagina para el hook de resize
anchor_p5 = '    page5.setStyleSheet("background: transparent;")'
if "self._chat_page = page5" not in t and anchor_p5 in t:
    t = t.replace(anchor_p5, anchor_p5 + "\n    self._chat_page = page5", 1)
    log.append("ref pagina")

# 3) Hook: re-dibujar fondo al redimensionar la pagina
anchor_ef = "def eventFilter(self, obj, event):"
if "_chat_page" not in t[t.find(anchor_ef):t.find(anchor_ef)+400] if t.find(anchor_ef) != -1 else True:
    i = t.find(anchor_ef)
    if i != -1:
        j = t.find("\n", i) + 1
        hook = ('''        try:
            from PySide6.QtCore import QEvent
            if obj is getattr(self, "_chat_page", None) and \\
                    event.type() == QEvent.Type.Resize:
                self._layout_chat_bg()
        except Exception:
            pass
''')
        t = t[:j] + hook + t[j:]
        log.append("hook resize")
        # instalar el filtro sobre la pagina
        anchor_inst = "    self._chat_page = page5"
        if "installEventFilter(self._chat_page" not in t:
            t = t.replace(anchor_inst,
                          anchor_inst + "\n    page5.installEventFilter(self)", 1)
            log.append("installEventFilter")

p.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
print("OK", log)
