from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")
n = 0

# 1) Colores exactos del mockup en las 3 cards
r1 = [('self._card(v, "#4cc2ff", "flask", None, "Gratis", "S/ 0",',
       'self._card(v, "#00d0ff", "flask", None, "Gratis", "S/ 0",'),
      ('self._card(v, "#bc8cff", None, self._CAL, "Mensual", "S/ 10",',
       'self._card(v, "#a855f7", None, self._CAL, "Mensual", "S/ 10",'),
      ('self._card(v, "#f5b544", "star", None, "Lifetime", "S/ 30",',
       'self._card(v, "#ffb020", "star", None, "Lifetime", "S/ 30",'),
      ('bgs = {"#4cc2ff": "#0b1322", "#bc8cff": "#130e26",\n               "#f5b544": "#181007"}',
       'bgs = {"#00d0ff": "#0b1322", "#a855f7": "#130e26",\n               "#ffb020": "#181007"}'),
      ('bord = color if badge else color + "55"',
       'bord = color if badge else color + "B3"')]
for old, new in r1:
    if old in t:
        t = t.replace(old, new, 1); n += 1

# 2) Medalla profesional SVG (vector con gradiente y cintas)
if "def _medal_pixmap" not in t:
    i = t.find("class PlansDialog(QDialog):")
    medal = '''def _medal_pixmap(w=40, h=52):
    """Medalla con diamante, estilo profesional (SVG vectorial)."""
    from PySide6.QtSvg import QSvgRenderer
    from PySide6.QtCore import QByteArray
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 84">'
           '<defs><linearGradient id="mg" x1="0" y1="0" x2="1" y2="1">'
           '<stop offset="0" stop-color="#a78bfa"/>'
           '<stop offset="1" stop-color="#6d28d9"/>'
           '</linearGradient></defs>'
           '<path d="M18 44 L10 80 L22 70 L28 82 L32 56 Z" fill="#5b21b6"/>'
           '<path d="M46 44 L54 80 L42 70 L36 82 L32 56 Z" fill="#6d28d9"/>'
           '<circle cx="32" cy="30" r="24" fill="url(#mg)"/>'
           '<circle cx="32" cy="30" r="24" fill="none" '
           'stroke="#c4b5fd" stroke-width="2.5"/>'
           '<circle cx="32" cy="30" r="17" fill="none" '
           'stroke="#ede9fe" stroke-width="1.2" opacity="0.65"/>'
           '<path d="M24 24 h16 l6 7 -14 16 -14 -16 z" fill="#ffffff"/>'
           '<path d="M24 24 l8 7 8 -7 M32 31 v16 M18 31 h28" '
           'stroke="#c4b5fd" stroke-width="1.3" fill="none"/>'
           '</svg>')
    r = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    pm = QPixmap(w, h)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    r.render(p)
    p.end()
    return pm


'''
    t = t[:i] + medal + t[i:]
    n += 1

# 3) Usar la medalla en el ribbon (reemplaza el dibujo manual)
old_gem = '''            gem = QLabel(card)
            gem.setFixedSize(34, 42)
            gpm = QPixmap(34, 42)
            gpm.fill(Qt.GlobalColor.transparent)
            gp = QPainter(gpm)
            gp.setRenderHint(QPainter.RenderHint.Antialiasing)
            from PySide6.QtGui import QPolygon as _QP
            from PySide6.QtCore import QPoint as _QPt
            gp.setPen(Qt.PenStyle.NoPen)
            gp.setBrush(QColor("#5b21b6"))
            gp.drawPolygon(_QP([_QPt(8, 26), _QPt(13, 41), _QPt(17, 30)]))
            gp.drawPolygon(_QP([_QPt(26, 26), _QPt(21, 41), _QPt(17, 30)]))
            gp.setBrush(QColor("#7c3aed"))
            gp.drawEllipse(3, 2, 28, 28)
            gp.drawPixmap(10, 9, _chat_svg(self._GEM, "#ffffff", 14))
            gp.end()
            gem.setPixmap(gpm)'''
new_gem = '''            gem = QLabel(card)
            gem.setFixedSize(40, 52)
            gem.setPixmap(_medal_pixmap(40, 52))'''
if old_gem in t:
    t = t.replace(old_gem, new_gem, 1); n += 1

# 4) Ajustar posicion de la medalla al nuevo tamano
old_pos = '''                    if h is not None:
                        g.move(c.mapTo(h, QPoint(c.width() - 30, -16)))
                    else:
                        g.move(c.width() - 30, -16)'''
new_pos = '''                    if h is not None:
                        g.move(c.mapTo(h, QPoint(c.width() - 34, -18)))
                    else:
                        g.move(c.width() - 34, -18)'''
if old_pos in t:
    t = t.replace(old_pos, new_pos, 1); n += 1

mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
print(f"OK: {n} ajustes (colores exactos + medalla SVG)")
