from pathlib import Path
import ast, re

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# Des-indentar _build_ui y _connect_signals (estan a 4 espacios pero
# deben quedar a 0 para asignarlos a la clase al final)
t = t.replace("\n    # ===================== METODOS DE MainWindow =====================\ndef _build_ui(self):", "\n\ndef _build_ui(self):")
# Si _build_ui quedo con sangria, quitarla linea por linea hasta su def
m = re.search(r"\n(    )def _build_ui\(self\):", t)
if m:
    start = m.start()
    end = t.find("\ndef _connect_signals", start)
    block = t[start:end]
    block = block.replace("\n    ", "\n")
    t = t[:start] + block + t[end:]
m = re.search(r"\n(    )def _connect_signals\(self\):", t)
if m:
    start = m.start()
    end = t.find("\ndef _switch_page", start)
    block = t[start:end]
    block = block.replace("\n    ", "\n")
    t = t[:start] + block + t[end:]

p.write_text(t, encoding="utf-8")
try:
    ast.parse(t)
    print("Sangria normalizada - SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
