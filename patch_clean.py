from pathlib import Path
import ast, re

# 1. Limpiar BOM de modern_window.py
p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8-sig")
t = t.replace("\ufeff", "")

# 2. super() no funciona en funciones a nivel de modulo
t = t.replace(
    "super().showEvent(event)",
    "QMainWindow.showEvent(self, event)",
    1,
)

p.write_text(t, encoding="utf-8")
try:
    ast.parse(t)
    print("modern_window.py limpio - SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)

# 3. Switch seguro en run.py (clon con fallback)
r = Path("run.py")
rt = r.read_text(encoding="utf-8-sig").replace("\ufeff", "")
if "modern_window" not in rt:
    rt2 = re.sub(
        r"(?m)^(\s*)from ui\.main_window import MainWindow\s*$",
        lambda m: (
            m.group(1) + "try:\n"
            + m.group(1) + "    from ui.modern_window import MainWindow\n"
            + m.group(1) + "except Exception:\n"
            + m.group(1) + "    from ui.main_window import MainWindow"
        ),
        rt,
        count=1,
    )
    if rt2 != rt:
        r.write_text(rt2, encoding="utf-8")
        print("run.py: clon con fallback agregado.")
    else:
        print("AVISO: no se encontro el import en run.py.")
else:
    print("run.py ya tenia el switch.")
