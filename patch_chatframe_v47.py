from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")

anchor = "self.pages.addWidget(page5)"
wrap = '''    # Marco semi-transparente alrededor de todo el Chat IA
    try:
        _old_l = page5.layout()
        _old_l.setContentsMargins(10, 10, 10, 10)
        _frame = QFrame(page5)
        _frame.setObjectName("chatFrame")
        _frame.setStyleSheet(
            "#chatFrame { border: 1.5px solid rgba(139,117,255,80);"
            " border-radius: 18px; background: rgba(12,16,28,120); }")
        _fl = QVBoxLayout(_frame)
        _fl.setContentsMargins(14, 14, 14, 14)
        _fl.setSpacing(10)
        while _old_l.count():
            _it = _old_l.takeAt(0)
            _w = _it.widget()
            if _w is not None:
                _fl.addWidget(_w)
            else:
                _fl.addItem(_it)
        _old_l.addWidget(_frame)
    except Exception as _exc:
        print("chatFrame:", _exc)
    self.pages.addWidget(page5)'''

if "chatFrame" not in t and anchor in t:
    t = t.replace(anchor, wrap, 1)
    mw.write_text(t, encoding="utf-8", newline="\n")
    ast.parse(t)
    print("OK: marco chatFrame agregado")
else:
    print("nada que hacer")
