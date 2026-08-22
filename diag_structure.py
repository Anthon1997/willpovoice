from pathlib import Path
import re

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")

print("=== DEFINICIONES DE TRIAL ===")
for name in ("_trial_gate", "_show_no_tokens", "_trial_spend",
             "_trial_active", "_refresh_token_chip", "_update_token_chip"):
    matches = list(re.finditer(rf"def {name}\(self", t))
    for m in matches:
        print(f"  {name} -> offset {m.start()}")

print("\n=== ATTACHES DE MAINWINDOW ===")
for pat in (r"MainWindow\._\w+\s*=", r"_trial_\w+\s*=\s*_trial_\w+",
            r"_show_no_tokens\s*=\s*_show_no_tokens"):
    for m in re.finditer(pat, t):
        print(f"  {m.group()} (offset {m.start()})")

print("\n=== FUNCIONES EXTERNAS CON ATTACH ===")
# buscar bloques como "def _xxx(self): ... MainWindow._xxx = _xxx"
for m in re.finditer(r"^def (_\w+)\(self", t, re.M):
    name = m.group(1)
    if re.search(rf"MainWindow\.{name}\s*=", t):
        print(f"  ✅ {name} (externa + attached)")

print("\n=== ESTRUCTURA class MainWindow ===")
cls_start = t.find("class MainWindow")
print(f"  class MainWindow en offset {cls_start}")
if cls_start != -1:
    # buscar si _trial_gate esta dentro de la clase
    cls_end = t.find("\nclass ", cls_start + 1)
    if cls_end == -1: cls_end = len(t)
    chunk = t[cls_start:cls_end]
    for name in ("_trial_gate", "_show_no_tokens", "_refresh_token_chip"):
        if f"def {name}(self" in chunk:
            print(f"  {name} DENTRO de class MainWindow")
        else:
            print(f"  {name} FUERA de class MainWindow")
