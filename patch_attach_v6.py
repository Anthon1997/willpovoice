from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")
log = []

anchor = "MainWindow._show_no_tokens = _show_no_tokens"
names = ["_trial_active", "_trial_gate", "_trial_spend",
         "_update_token_chip", "_refresh_token_chip"]

missing = [n for n in names if f"MainWindow.{n} = {n}" not in t]
if missing:
    block = "\n".join(f"MainWindow.{n} = {n}" for n in missing) + "\n"
    idx = t.find(anchor)
    if idx != -1:
        eol = t.find("\n", idx)
        t = t[:eol+1] + block + t[eol+1:]
    else:
        t = t.rstrip() + "\n" + block
    log.append(f"attach agregado: {missing}")

mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)

for n in names + ["_show_no_tokens"]:
    assert f"MainWindow.{n} = {n}" in t, f"FALTA {n}"
assert "class PaymentDialog" in t
print("SINTAXIS OK + TODOS LOS ATTACHES OK")
print("parches:", log)
