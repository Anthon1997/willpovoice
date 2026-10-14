from pathlib import Path
import re
src = Path("ui/modern_window.py").read_text(encoding="utf-8")

print("=== _trial_gate ===")
i = src.find("def _trial_gate")
print(src[i:i+1200] if i >= 0 else "NO")

print("\n=== donde se muestra el dialogo tokens ===")
for pat in ("Mejora tu plan", "Compra", "Tokens", "OFERTA LIMITADA", "_open_upgrade", "_show_upgrade", "buy_dialog", "PlanDialog", "UpgradeDialog"):
    for m in list(re.finditer(re.escape(pat), src))[:6]:
        ln = src[:m.start()].count("\n")+1
        print(ln, ":", src.splitlines()[ln-1].strip()[:100])
