from pathlib import Path
import re

t = Path("core/text_normalizer.py").read_text(encoding="utf-8")

print("=== Lineas con vocal duplicada / 'sign' / homografo ===")
for i, ln in enumerate(t.splitlines(), 1):
    if re.search(r"([aeiou])\1", ln) or "sign" in ln.lower() or "homogra" in ln.lower():
        print(f"{i}: {ln.rstrip()[:120]}")

from core.text_normalizer import normalize_for_tts, needs_homograph_guard

tests = [
    "Esto significa que la palabra significa algo importante.",
    "La palabra significa lo contrario.",
    "El codigo significa un avance.",
]
for desc in ["Microsoft AvaMultilingual Online (Natural) - English (United States)",
             "Microsoft Dalia Online (Natural) - Spanish (Mexico)"]:
    guard = needs_homograph_guard(desc)
    print(f"\nVOZ: {desc}\nguard: {guard}")
    for tx in tests:
        out = normalize_for_tts(tx, guard=guard)
        marca = "  <== CAMBIO SOSPECHOSO" if out != tx and "signifi" not in out else ""
        print(f"  IN : {tx}")
        print(f"  OUT: {out}{marca}")
