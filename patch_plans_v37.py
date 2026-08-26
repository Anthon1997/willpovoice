from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")
n = 0

# 1) Corona DORADA en el boton Comprar de Lifetime
old = 'b.setIcon(QIcon(make_icon("crown", "#ffffff", 16)))'
new = 'b.setIcon(QIcon(make_icon("crown", "#fbbf24", 16)))'
if old in t:
    t = t.replace(old, new, 1); n += 1

# 2) Medalla mas grande y viva (colores foto 2)
repl = [
    ('stop-color="#a78bfa"', 'stop-color="#c084fc"'),
    ('stop-color="#6d28d9"', 'stop-color="#7c3aed"'),
    ('fill="#5b21b6"', 'fill="#7c3aed"'),
    ('fill="#6d28d9"', 'fill="#8b5cf6"'),
    ('stroke="#c4b5fd" stroke-width="2.5"', 'stroke="#e9d5ff" stroke-width="2.5"'),
    ('gem.setFixedSize(40, 52)\n            gem.setPixmap(_medal_pixmap(40, 52))',
     'gem.setFixedSize(46, 60)\n            gem.setPixmap(_medal_pixmap(46, 60))'),
    ('g.move(c.mapTo(h, QPoint(c.width() - 34, -18)))',
     'g.move(c.mapTo(h, QPoint(c.width() - 40, -22)))'),
    ('g.move(c.width() - 34, -18)', 'g.move(c.width() - 40, -22)'),
]
for old, new in repl:
    if old in t:
        t = t.replace(old, new, 1); n += 1

mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
print(f"OK: {n} ajustes (corona dorada + medalla viva)")
