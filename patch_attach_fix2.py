from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")

line = "MainWindow._configure_groq_key = _configure_groq_key"
exists = any(l.strip() == line for l in t.splitlines())
print("attach existe como linea:", exists)

if not exists:
    t = t.rstrip("\n") + "\n\n" + line + "\n"
    mw.write_text(t, encoding="utf-8", newline="\n")
    ast.parse(t)
    print("OK: attach agregado al final del modulo")

from ui.modern_window import MainWindow
print("hasattr _configure_groq_key:", hasattr(MainWindow, "_configure_groq_key"))
