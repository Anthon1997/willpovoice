from pathlib import Path
import re

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

# Eliminar desde el label "Paleta:" hasta el gif de la paleta
t, n = re.subn(
    r"\n\s*palette_layout\.addWidget\(QLabel\(\"Paleta:\"\)\).*?palette_layout\.addWidget\(self\.gif_label\)",
    "",
    t,
    count=1,
    flags=re.S,
)
print(f"1. Paleta + Personalizar + gif eliminados: {n}")

# Limpiar métodos muertos de la paleta (opcional, por limpieza)
t = re.sub(
    r"\n    def on_swatch_clicked\(self\) -> None:.*?self\._apply_theme\(\)",
    "",
    t,
    count=1,
    flags=re.S,
)
t = re.sub(
    r"\n    def pick_custom_color\(self\) -> None:.*?self\._apply_theme\(\)",
    "",
    t,
    count=1,
    flags=re.S,
)
print("2. Métodos de paleta limpiados.")

p.write_text(t, encoding="utf-8")
print("Listo.")
