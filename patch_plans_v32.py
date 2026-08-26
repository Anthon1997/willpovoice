from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")

old = "        scroll.setWidget(content)\n        outer.addWidget(scroll)"
new = '''        scroll.setWidget(content)
        outer.addWidget(scroll)
        content.adjustSize()
        try:
            from PySide6.QtGui import QGuiApplication
            _scr = QGuiApplication.primaryScreen()
            maxh = int(_scr.availableSize().height() * 0.92) if _scr else 900
        except Exception:
            maxh = 900
        want = content.sizeHint().height() + 46
        self.resize(540, min(want, maxh))
        scroll.setMinimumHeight(320)'''

if old in t:
    t = t.replace(old, new, 1)
    mw.write_text(t, encoding="utf-8", newline="\n")
    ast.parse(t)
    print("OK: altura del dialogo = contenido o 92% pantalla")
else:
    print("AVISO: ancla no encontrada")
