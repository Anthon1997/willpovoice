from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")
log = []

# ---------- 1) _svg con fill-rule opcional ----------
old_svg = '''    def _svg(path_data, color, size):
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
               f'<path fill="{color}" d="{path_data}"/></svg>')'''
new_svg = '''    def _svg(path_data, color, size, rule="nonzero"):
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
               f'<path fill="{color}" fill-rule="{rule}" d="{path_data}"/></svg>')'''
if old_svg in t:
    t = t.replace(old_svg, new_svg, 1); log.append("svg rule")

# ---------- 2) IC_TOKEN (moneda con 1) ----------
anchor_gift = '               "12 17 10.83 14.92 8H20v6z")'
if "IC_TOKEN" not in t and anchor_gift in t:
    i = t.find(anchor_gift) + len(anchor_gift)
    t = t[:i] + '\n    IC_TOKEN = ("M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm0 3a7 7"\n                " 0 1 1 0 14 7 7 0 0 1 0-14zm-1 3h2v6h-2z")' + t[i:]
    log.append("IC_TOKEN")

# ---------- 3) Titulo grande + degradado por letra ----------
old_title = '''    t1 = QLabel("Compra")
    t1.setStyleSheet("color: #ffffff; font-size: 32px; font-weight: 900;")
    v.addWidget(t1)
    t2 = QLabel("Tokens")
    t2.setStyleSheet("color: #6f8cff; font-size: 32px; font-weight: 900;")
    v.addWidget(t2)'''
new_title = '''    tbox = QVBoxLayout()
    tbox.setSpacing(0)
    t1 = QLabel("Compra")
    t1.setStyleSheet("color: #ffffff; font-size: 42px; font-weight: 900;")
    tbox.addWidget(t1)
    trow = QHBoxLayout()
    trow.setSpacing(1)
    _grad = ["#8b5cf6", "#7d6ffb", "#6f83fb", "#6196fc", "#53a9fc", "#45bcfd"]
    for _ch, _cc in zip("Tokens", _grad):
        _l = QLabel(_ch)
        _l.setStyleSheet(
            f"color: {_cc}; font-size: 42px; font-weight: 900;")
        trow.addWidget(_l)
    trow.addStretch(1)
    tbox.addLayout(trow)
    v.addLayout(tbox)'''
if old_title in t:
    t = t.replace(old_title, new_title, 1); log.append("titulo degradado")

# ---------- 4) Cards: 5 elementos + token card ----------
old_loop = "for path, color, ctitle, cdesc in ["
new_loop = "for path, color, ctitle, cdesc, crule in ["
if old_loop in t:
    t = t.replace(old_loop, new_loop, 1); log.append("loop 5")

old_zap = r'(IC_ZAP, "#bc8cff", "M\u00e1s conversiones", "Convierte m\u00e1s texto en voz"),'
new_zap = r'(IC_ZAP, "#bc8cff", "M\u00e1s conversiones", "Convierte m\u00e1s texto en voz", "nonzero"),'
if old_zap in t:
    t = t.replace(old_zap, new_zap, 1)

old_sh = r'(IC_SHIELD, "#58a6ff", "Seguro y r\u00e1pido", "Transacciones 100% seguras"),'
new_sh = r'(IC_SHIELD, "#58a6ff", "Seguro y r\u00e1pido", "Transacciones 100% seguras", "nonzero"),'
if old_sh in t:
    t = t.replace(old_sh, new_sh, 1)

old_gift = '(IC_GIFT, "#f5b544", "Bonos exclusivos", "Tokens extra en cada compra"),'
new_gift = '(IC_TOKEN, "#f5b544", "Tokens", "20,000", "evenodd"),'
if old_gift in t:
    t = t.replace(old_gift, new_gift, 1); log.append("card tokens")

old_icl = "icl.setPixmap(_svg(path, color, 18))"
new_icl = "icl.setPixmap(_svg(path, color, 18, crule))"
if old_icl in t:
    t = t.replace(old_icl, new_icl, 1)

mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
for n in ("_trial_gate", "_show_no_tokens", "_refresh_token_chip"):
    assert f"MainWindow.{n} = {n}" in t, f"FALTA {n}"
print("OK", log)
