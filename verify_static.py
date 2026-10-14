from pathlib import Path
import re

p = Path("ui/modern_window.py")
src = p.read_text(encoding="utf-8")

print("=== A) marcadores ===")
print("_LIGHT_SUSPEND presente:", "_LIGHT_SUSPEND" in src)
print("wrap __init__ aplicado:", "_plans_init_orig" in src)
print("flag en monkeypatch:", "globals().get(\"_LIGHT_SUSPEND\"" in src)

print("\n=== B) linea de clase PlansDialog ===")
m = re.search(r"class PlansDialog[^\n]*", src)
print(repr(m.group(0)) if m else "NO ENCONTRADA")

print("\n=== C) cuerpo de _card (qss real) ===")
i = src.find("def _card(self")
print(src[i:i+2200] if i >= 0 else "NO ENCONTRADO")
