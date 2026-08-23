from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

i = t.find("    page6 = QWidget()")
j = t.find("    self.pages.addWidget(page6)")
if i == -1 or j == -1:
    raise SystemExit("ERROR: region de Ajustes no encontrada")

region = t[i:j]
n = region.count("page5")
region = region.replace("page5", "page6")
t = t[:i] + region + t[j:]

p.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
print(f"OK: {n} referencias page5 -> page6 en el cuerpo de Ajustes")
