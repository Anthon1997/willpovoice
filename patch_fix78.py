from pathlib import Path

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

old = "\n        last_voice = self.settings.get(\"last_voice\", \"\")"
new = "\n            last_voice = self.settings.get(\"last_voice\", \"\")"

if old in t:
    t = t.replace(old, new, 1)
    p.write_text(t, encoding="utf-8")
    print("Indentacion de last_voice corregida (8 -> 12 espacios).")
else:
    print("AVISO: patron no encontrado.")
