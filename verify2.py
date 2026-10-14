from pathlib import Path
src = Path("ui/modern_window.py").read_text(encoding="utf-8")

i = src.find("class PlansDialog")
print("=== entre clase y __init__ ===")
print(repr(src[i:i+300]))

j = src.find("def _card(self, v")
print("\n=== _card de planes ===")
print(src[j:j+2600] if j >= 0 else "NO ENCONTRADO")
