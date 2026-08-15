from pathlib import Path
import re, ast

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

creates = re.findall(r"self\.(\w+)\s*=\s*QComboBox\(\)", t)
print("Combos creados:", creates)

m = re.search(
    r"Voz seleccionada[\s\S]{0,400}?addWidget\(self\.(\w+)", t
)
visible = m.group(1) if m else None
print("Combo visible tras 'Voz seleccionada':", visible)

if "voice_combo" not in creates:
    if visible and visible != "voice_combo":
        old = f"self.{visible}"
        t = t.replace(old, "self.voice_combo")
        print(f"Renombrado {old} -> self.voice_combo en todo el archivo.")
    else:
        if "self.lang_combo = QComboBox()" in t:
            t = t.replace(
                "self.lang_combo = QComboBox()",
                "self.lang_combo = QComboBox()\n"
                "        self.voice_combo = QComboBox()",
                1,
            )
            print("voice_combo creado junto a lang_combo.")
        else:
            t = t.replace(
                "def _build_ui(self):",
                "def _build_ui(self):\n"
                "        self.voice_combo = QComboBox()",
                1,
            )
            print("voice_combo creado al inicio de _build_ui.")
else:
    print("voice_combo ya existia.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
