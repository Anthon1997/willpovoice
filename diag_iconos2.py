from pathlib import Path
import re

t = Path("ui/modern_window.py").read_text(encoding="utf-8")

print("=== Cuerpo de make_icon (el mapa de glifos) ===")
i = t.find("def make_icon")
if i != -1:
    j = t.find("\ndef ", i + 10)
    body = t[i:j if j != -1 else i + 3000]
    print(body[:2500])
    keys = re.findall(r'["\']([A-Za-z0-9_]+)["\']\s*:', body)
    print("\n--- claves del mapa:", len(keys), "---")
    print(sorted(set(keys)))

print("\n=== Primer argumento en constructores de iconos ===")
names = set()
for m in re.finditer(
        r'(?:make_icon|IconLabel|SquareButton|ToolButton|StatsCard)'
        r'\(\s*(?:[^)]*?)["\']([A-Za-z0-9_]+)["\']', t):
    names.add(m.group(1))
print(sorted(names))

print("\n=== Tuplas (icono, etiqueta) del sidebar ===")
for m in re.finditer(r'\(\s*["\']([a-z_]+)["\']\s*,\s*["\'][A-ZÁÉ]', t):
    print("  ", m.group(1))
