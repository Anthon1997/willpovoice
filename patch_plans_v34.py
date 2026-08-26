from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")
n = 0

# 1) Footer: stylesheet por objectName (no se filtra a labels)
old = '''foot.setStyleSheet(
            "QFrame { background: #10141f; border: 1px solid #1c2333;"
            " border-radius: 12px; }")'''
new = '''foot.setObjectName("plansFooter")
        foot.setStyleSheet(
            "#plansFooter { background: #10141f; border: 1px solid #1c2333;"
            " border-radius: 12px; }")'''
if old in t:
    t = t.replace(old, new, 1); n += 1

# 2) Fondos con tinte por plan (opacos, como el mockup)
old = '''        bord = color if badge else color + "44"
        card.setStyleSheet(
            "#plancard_" + name + " { background: rgba(13,17,29,200);"
            " border: 1.5px solid " + bord + "; border-radius: 16px; }")'''
new = '''        bord = color if badge else color + "55"
        bgs = {"#4cc2ff": "#0b1322", "#bc8cff": "#130e26",
               "#f5b544": "#181007"}
        bg = bgs.get(color, "#10141f")
        card.setStyleSheet(
            "#plancard_" + name + " { background: " + bg + ";"
            " border: 1.5px solid " + bord + "; border-radius: 16px; }")'''
if old in t:
    t = t.replace(old, new, 1); n += 1

# 3) Medalla incrustada sin recorte (anclada al contenido)
old = '''            gem.setStyleSheet("background: transparent;")
            QTimer.singleShot(
                0, lambda c=card, g=gem: g.move(c.width() - 22, -14))'''
new = '''            gem.setStyleSheet("background: transparent;")
            host = v.parent()
            if host is not None:
                gem.setParent(host)

            def _place(g=gem, c=card, h=host):
                try:
                    from PySide6.QtCore import QPoint
                    if h is not None:
                        g.move(c.mapTo(h, QPoint(c.width() - 30, -16)))
                    else:
                        g.move(c.width() - 30, -16)
                    g.raise_()
                    g.show()
                except Exception:
                    pass
            QTimer.singleShot(0, _place)'''
if old in t:
    t = t.replace(old, new, 1); n += 1

mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
print(f"OK: {n}/3 ajustes aplicados")
