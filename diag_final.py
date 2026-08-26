import re
from pathlib import Path
t = Path("ui/modern_window.py").read_text(encoding="utf-8")
for name in ["_configure_groq_key", "_save_groq_key", "_delete_groq_key",
             "_send_chat_message", "_on_chat_response", "_add_chat_bubble"]:
    defs = [i+1 for i, l in enumerate(t.splitlines()) if l.startswith(f"def {name}(")]
    atts = [i+1 for i, l in enumerate(t.splitlines()) if l.strip() == f"MainWindow.{name} = {name}"]
    print(f"{name:22} def={defs} attach={atts}")

from ui.modern_window import MainWindow
for name in ["_configure_groq_key", "_save_groq_key", "_delete_groq_key",
             "_send_chat_message"]:
    print(f"hasattr {name}: {hasattr(MainWindow, name)}")
