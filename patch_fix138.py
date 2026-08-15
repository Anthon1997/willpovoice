from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# ---- 1. RECOPILACION ----
for m in ("Hola, este es mi voz.", "QColor(0, 0, 0, 160)"):
    print(f"--- {m!r} indice:", t.find(m))

# ---- 2. Nuevo texto de muestra ----
t = t.replace(
    'self._preview_sapi.Speak("Hola, este es mi voz.", 1)',
    'self._preview_sapi.Speak("Hola esta es mi voz", 1)',
    1,
)
print("2. Texto de muestra actualizado.")

# ---- 3. Overlay mas semitransparente ----
t = t.replace(
    "p.setBrush(QColor(0, 0, 0, 160))",
    "p.setBrush(QColor(0, 0, 0, 110))",
    1,
)
print("3. Overlay semitransparente (alpha 110).")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
