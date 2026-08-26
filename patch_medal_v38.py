from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")
n = 0

# 1) Nueva medalla: cinta colgante + circulo encima (como la foto)
s = t.find("def _medal_pixmap")
e = t.find("class PlansDialog(QDialog):")
if s != -1 and e != -1:
    new_fn = '''def _medal_pixmap(w=34, h=50):
    """Medalla colgante: cinta vertical con muesca V y circulo con diamante."""
    from PySide6.QtSvg import QSvgRenderer
    from PySide6.QtCore import QByteArray
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 72">'
           '<defs>'
           '<linearGradient id="rb" x1="0" y1="0" x2="0" y2="1">'
           '<stop offset="0" stop-color="#8b5cf6"/>'
           '<stop offset="1" stop-color="#6d28d9"/>'
           '</linearGradient>'
           '<linearGradient id="cg" x1="0" y1="0" x2="1" y2="1">'
           '<stop offset="0" stop-color="#a78bfa"/>'
           '<stop offset="1" stop-color="#7c3aed"/>'
           '</linearGradient>'
           '</defs>'
           '<path d="M14 2 h20 v58 l-10 -9 -10 9 z" fill="url(#rb)"/>'
           '<path d="M14 2 h20 v6 h-20 z" fill="#5b21b6" opacity="0.55"/>'
           '<circle cx="24" cy="20" r="15" fill="url(#cg)"/>'
           '<circle cx="24" cy="20" r="15" fill="none" '
           'stroke="#e9d5ff" stroke-width="2"/>'
           '<path d="M18 17 h12 l4 5 -10 11 -10 -11 z" fill="#ffffff"/>'
           '<path d="M18 17 l6 5 6 -5 M24 22 v11 M14 22 h20" '
           'stroke="#ddd6fe" stroke-width="1" fill="none" opacity="0.8"/>'
           '</svg>')
    r = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    pm = QPixmap(w, h)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    r.render(p)
    p.end()
    return pm


'''
    t = t[:s] + new_fn + t[e:]
    n += 1

# 2) Tamano contenido + posicion colgando de la esquina
repl = [
    ('gem.setFixedSize(46, 60)\n            gem.setPixmap(_medal_pixmap(46, 60))',
     'gem.setFixedSize(34, 50)\n            gem.setPixmap(_medal_pixmap(34, 50))'),
    ('g.move(c.mapTo(h, QPoint(c.width() - 40, -22)))',
     'g.move(c.mapTo(h, QPoint(c.width() - 30, -12)))'),
    ('g.move(c.width() - 40, -22)', 'g.move(c.width() - 30, -12)'),
]
for old, new in repl:
    if old in t:
        t = t.replace(old, new, 1); n += 1

mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
print(f"OK: {n} ajustes (medalla colgante como la foto)")
