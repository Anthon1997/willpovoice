from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")
n = 0

# 1) Card: alpha-prefix + fondo degradado transparente
old = '''        bord = color if badge else color + "B3"
        bgs = {"#00d0ff": "#0b1322", "#a855f7": "#130e26",
               "#ffb020": "#181007"}
        bg = bgs.get(color, "#10141f")
        card.setStyleSheet(
            "#plancard_" + name + " { background: " + bg + ";"
            " border: 1.5px solid " + bord + "; border-radius: 16px; }")'''
new = '''        def _A(c, a):
            return "#" + a + c[1:]
        bord = color if badge else _A(color, "99")
        bgs = {"#00d0ff": "0b1322", "#a855f7": "130e26",
               "#ffb020": "181007"}
        rgb = bgs.get(color, "10141f")
        card.setStyleSheet(
            "#plancard_" + name + " { background: qlineargradient("
            "x1:0,y1:0,x2:0,y2:1, stop:0 #33" + rgb + ", stop:1 #14"
            + rgb + "); border: 1.5px solid " + bord +
            "; border-radius: 16px; }")'''
if old in t:
    t = t.replace(old, new, 1); n += 1

# 2) Price pill con alpha correcto
old = '"color: " + color + "; border: 1px solid " + color + "66;"'
new = '"color: " + color + "; border: 1px solid " + _A(color, "66") + ";"'
if old in t:
    t = t.replace(old, new, 1); n += 1

# 3) Separador punteado alpha correcto
old = '"border-top: 1px dashed " + color + "44;"'
new = '"border-top: 1px dashed " + _A(color, "44") + ";"'
if old in t:
    t = t.replace(old, new, 1); n += 1

# 4) Boton outline alpha correcto
old = ('"QPushButton { background: transparent; color: "\n                    + color + "; border: 1px solid " + color + "88;"')
new = ('"QPushButton { background: transparent; color: "\n                    + color + "; border: 1px solid " + _A(color, "88") + ";"')
if old in t:
    t = t.replace(old, new, 1); n += 1
old = '" QPushButton:hover { background: " + color + "22; }")'
new = '" QPushButton:hover { background: " + _A(color, "22") + "; }")'
if old in t:
    t = t.replace(old, new, 1); n += 1

# 5) Badge dorado alpha correcto
old = '"color: #f5b544; border: 1px solid #f5b54466;"'
new = '"color: #f5b544; border: 1px solid #66f5b544;"'
if old in t:
    t = t.replace(old, new, 1); n += 1

mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
print(f"OK: {n} fixes de alpha + degradados")
