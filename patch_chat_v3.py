from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")
log = []

# Renombrar señal finished -> resultado (no se puede sobreescribir finished)
if "finished = _pyqtSignal(str)" in t:
    t = t.replace("finished = _pyqtSignal(str)", "resultado = _pyqtSignal(str)", 1)
    t = t.replace("self.finished.emit(resp)", "self.resultado.emit(resp)", 1)
    t = t.replace("worker.finished.connect(", "worker.resultado.connect(", 1)
    log.append("senal renombrada")

p.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
print("OK", log)
