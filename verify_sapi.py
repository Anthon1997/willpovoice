from pathlib import Path
import re

src = Path("adapters/sapi_adapter.py").read_text(encoding="utf-8")
print("LONG:", len(src))
print("\n=== TODOS los metodos def ===")
for m in re.finditer(r"def (\w+)\([^)]*\):", src):
    ln = src[:m.start()].count("\n")+1
    print(f"L{ln}: {m.group(0)}")
print("\n=== Primeros 2500 chars ===")
print(src[:2500])
print("\n=== Ultimos 1500 chars ===")
print(src[-1500:])
