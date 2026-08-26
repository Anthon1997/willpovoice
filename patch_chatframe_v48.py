from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")

old = '''            _w = _it.widget()
            if _w is not None:
                _fl.addWidget(_w)
            else:
                _fl.addItem(_it)'''

new = '''            _w = _it.widget()
            if _w is not None:
                _fl.addWidget(_w)
            elif _it.layout() is not None:
                _fl.addLayout(_it.layout())
            else:
                _fl.addItem(_it)'''

if old in t:
    t = t.replace(old, new, 1)
    mw.write_text(t, encoding="utf-8", newline="\n")
    ast.parse(t)
    print("OK: encabezado re-encapsulado con addLayout")
else:
    print("AVISO: bloque no encontrado")
