from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")
log = []

# 1) Card 1: bolt.svg del sistema
old_zap = r'(IC_ZAP, "#bc8cff", "M\u00e1s conversiones", "Convierte m\u00e1s texto en voz", "nonzero"),'
new_zap = r'("bolt", "#bc8cff", "M\u00e1s conversiones", "Convierte m\u00e1s texto en voz", "app"),'
if old_zap in t:
    t = t.replace(old_zap, new_zap, 1); log.append("bolt.svg")

# 2) Card 3: coins.svg del sistema (el icono real de tokens)
old_tok = '(IC_TOKEN, "#f5b544", "Tokens", "20,000", "evenodd"),'
new_tok = '("coins", "#f5b544", "Tokens", "20,000", "app"),'
if old_tok in t:
    t = t.replace(old_tok, new_tok, 1); log.append("coins.svg")

# 3) Render: make_icon para cards "app", _svg para el resto
old_pix = "        icl.setPixmap(_svg(path, color, 18, crule))"
new_pix = ('''        if crule == "app":
            icl.setPixmap(make_icon(path, color, 18))
        else:
            icl.setPixmap(_svg(path, color, 18, crule))''')
if old_pix in t:
    t = t.replace(old_pix, new_pix, 1); log.append("make_icon")

mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
for n in ("_trial_gate", "_show_no_tokens", "_refresh_token_chip"):
    assert f"MainWindow.{n} = {n}" in t, f"FALTA {n}"
print("OK", log)
