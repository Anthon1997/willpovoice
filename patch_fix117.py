from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

old = """            voices.sort(key=lambda n: (not self._is_premium(n), n.lower()))
            self._voices = voices"""
new = """            voices.sort(key=lambda n: (not self._is_premium(n), n.lower()))
            lowered = [v.lower() for v in voices]
            multi_persons = {
                k for k in PREMIUM_PHOTOS
                if any(k in n and "multilingual" in n for n in lowered)
            }
            dedup = []
            for v in voices:
                low = v.lower()
                person = next((k for k in PREMIUM_PHOTOS if k in low), None)
                if person in multi_persons and "multilingual" not in low:
                    continue
                dedup.append(v)
            voices = dedup
            self._voices = voices"""

if old in t:
    t = t.replace(old, new, 1)
    print("Duplicados regionales eliminados (solo queda Multilingual).")
else:
    print("AVISO: anchor no encontrado.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
