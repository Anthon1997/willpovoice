from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")
n = 0

repl = [
    # Cinta nace en y=0 del SVG (sin padding superior)
    ('<path d="M14 2 h20 v58 l-10 -9 -10 9 z" fill="url(#rb)"/>',
     '<path d="M14 0 h20 v60 l-10 -9 -10 9 z" fill="url(#rb)"/>'),
    ('<path d="M14 2 h20 v6 h-20 z" fill="#5b21b6" opacity="0.55"/>',
     '<path d="M14 0 h20 v5 h-20 z" fill="#5b21b6" opacity="0.55"/>'),
    # Anclaje: justo sobre la linea del borde del plan
    ('g.move(c.mapTo(h, QPoint(c.width() - 30, 2)))',
     'g.move(c.mapTo(h, QPoint(c.width() - 30, 0)))'),
    ('g.move(c.width() - 30, 2)', 'g.move(c.width() - 30, 0)'),
]
for old, new in repl:
    if old in t:
        t = t.replace(old, new, 1); n += 1

mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
print(f"OK: {n} ajustes (cinta encajada al borde)")
