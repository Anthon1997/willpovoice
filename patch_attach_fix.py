from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")

anchor = "MainWindow._save_groq_key = _save_groq_key"
line = "MainWindow._configure_groq_key = _configure_groq_key"
if line not in t and anchor in t:
    t = t.replace(anchor, anchor + "\n" + line, 1)
    mw.write_text(t, encoding="utf-8", newline="\n")
    ast.parse(t)
    print("OK: attach de _configure_groq_key agregado")
else:
    print("nada que hacer")

from ui.modern_window import MainWindow
print("hasattr _configure_groq_key:", hasattr(MainWindow, "_configure_groq_key"))
