from pathlib import Path
import re
src = Path("ui/modern_window.py").read_text(encoding="utf-8")
print("=== asignaciones settings theme ===")
for m in re.finditer(r".*settings\[.theme.\]\s*=.*", src):
    ln = src[:m.start()].count("\n")+1
    print(ln, ":", m.group(0).strip())
print("\n=== def que manejan tema ===")
for m in re.finditer(r"def \w*(tema|theme)\w*\(self[^)]*\):", src):
    ln = src[:m.start()].count("\n")+1
    print(ln, ":", m.group(0).strip())
print("\n=== botones tema en Ajustes (Oscuro/Claro/Sistema) ===")
for m in re.finditer(r".*(Oscuro|Claro|Sistema).*(connect|clicked).*( )?", src):
    ln = src[:m.start()].count("\n")+1
    print(ln, ":", m.group(0).strip())
