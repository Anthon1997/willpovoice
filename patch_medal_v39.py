from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")
n = 0

# 1) Bajar el circulo/diamante dentro del SVG (cinta queda arriba)
repl = [
    ('<circle cx="24" cy="20" r="15" fill="url(#cg)"/>',
     '<circle cx="24" cy="24" r="15" fill="url(#cg)"/>'),
    ('<circle cx="24" cy="20" r="15" fill="none" ',
     '<circle cx="24" cy="24" r="15" fill="none" '),
    ('<path d="M18 17 h12 l4 5 -10 11 -10 -11 z" fill="#ffffff"/>',
     '<path d="M18 21 h12 l4 5 -10 11 -10 -11 z" fill="#ffffff"/>'),
    ('<path d="M18 17 l6 5 6 -5 M24 22 v11 M14 22 h20" ',
     '<path d="M18 21 l6 5 6 -5 M24 26 v11 M14 26 h20" '),
    # 2) Posicion: cinta nace del borde hacia ADENTRO
    ('g.move(c.mapTo(h, QPoint(c.width() - 30, -12)))',
     'g.move(c.mapTo(h, QPoint(c.width() - 30, 2)))'),
    ('g.move(c.width() - 30, -12)', 'g.move(c.width() - 30, 2)'),
]
for old, new in repl:
    if old in t:
        t = t.replace(old, new, 1); n += 1

mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
print(f"OK: {n} ajustes (medalla colgada dentro del borde)")
