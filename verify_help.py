from pathlib import Path
import re
src = Path("ui/modern_window.py").read_text(encoding="utf-8")
for pat in ("Ayuda de WillpoVoice", "Elige una voz", "Marka", "coraz"):
    for m in list(re.finditer(re.escape(pat), src))[:4]:
        ln = src[:m.start()].count("\n")+1
        print("=== ", pat, " L", ln, " ===")
        print(src[m.start()-400:m.start()+600])
        print("-"*70)
