from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")
log = []

# 1) Altura maxima = 92% de la pantalla (scroll interno)
old_w = '        self.setFixedWidth(540)\n        self.setWindowTitle("WillpoVoice Premium")'
new_w = ('        self.setFixedWidth(540)\n'
         '        try:\n'
         '            from PySide6.QtGui import QGuiApplication\n'
         '            _scr = QGuiApplication.primaryScreen()\n'
         '            if _scr is not None:\n'
         '                self.setMaximumHeight(\n'
         '                    int(_scr.availableSize().height() * 0.92))\n'
         '        except Exception:\n'
         '            pass\n'
         '        self.setWindowTitle("WillpoVoice Premium")')
if old_w in t:
    t = t.replace(old_w, new_w, 1)
    log.append("altura limitada")

# 2) Fondo sutil (opacidad 30%, sin overlay brillante)
old_bg = '''        p.drawPixmap((w - scaled.width()) // 2,
                     (h - scaled.height()) // 2, scaled)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(10, 12, 20, 210))
        p.drawRect(0, 0, w, h)
        p.end()'''
new_bg = '''        p.setOpacity(0.30)
        p.drawPixmap((w - scaled.width()) // 2,
                     (h - scaled.height()) // 2, scaled)
        p.end()'''
if old_bg in t:
    t = t.replace(old_bg, new_bg, 1)
    log.append("fondo sutil")

mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
print("OK", log)
