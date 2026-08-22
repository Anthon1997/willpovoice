from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")
log = []

# ---------- 1) Quitar "ACCESO LIMITADO" ----------
old_warn = '''    # ---------- HEADER marketing ----------
    top = QHBoxLayout()
    top.setSpacing(8)
    warn = QLabel()
    warn.setPixmap(_svg(IC_WARN, "#f5b544", 15))
    top.addWidget(warn)
    warn_t = QLabel("ACCESO LIMITADO")
    warn_t.setStyleSheet(
        "color: #bc8cff; font-size: 11px; font-weight: 700;"
        " letter-spacing: 2px;")
    top.addWidget(warn_t)
    top.addStretch(1)
    v.addLayout(top)
'''
if old_warn in t:
    t = t.replace(old_warn, "    v.addSpacing(6)\n", 1)
    log.append("sin acceso limitado")

# ---------- 2) Titulo mas grande ----------
if 'font-size: 42px; font-weight: 900;' in t:
    t = t.replace('font-size: 42px; font-weight: 900;',
                  'font-size: 50px; font-weight: 900;')
    log.append("titulo 50px")

# ---------- 3) Card tokens: "20,000 por un mes" ----------
old_tok = '("coins", "#f5b544", "Tokens", "20,000", "app"),'
new_tok = '("coins", "#f5b544", "Tokens", "20,000 por un mes", "app"),'
if old_tok in t:
    t = t.replace(old_tok, new_tok, 1)
    log.append("20,000 por un mes")

mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
for n in ("_trial_gate", "_show_no_tokens", "_refresh_token_chip"):
    assert f"MainWindow.{n} = {n}" in t, f"FALTA {n}"
print("OK", log)
