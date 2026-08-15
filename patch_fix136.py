from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# ---- 1. RECOPILACION ----
i = t.find("tl.addWidget(n)")
print("--- zona textos actual ---")
print(t[i - 400:i + 200])

# ---- 2. Nombre 13px ----
old_n = """        n = QLabel(window._display_voice_name(name))
        n.setStyleSheet(
            f"color: {TEXT}; font-size: 12px; font-weight: 600;"
            " background: transparent;"
        )"""
new_n = """        n = QLabel(window._display_voice_name(name))
        n.setStyleSheet(
            f"color: {TEXT}; font-size: 13px; font-weight: 600;"
            " background: transparent;"
        )"""
if old_n in t:
    t = t.replace(old_n, new_n, 1)
    print("2. Nombre 13px.")

# ---- 3. Dorado 10px ----
t = t.replace(
    '"color: #f5b301; font-size: 9px; font-weight: 600;"',
    '"color: #f5b301; font-size: 10px; font-weight: 600;"',
    1,
)
print("3. Dorado 10px.")

# ---- 4. Acento 11px (solo en VoiceCard) ----
old_s = """        s = QLabel(window._voice_subtitle(name, premium))
        s.setStyleSheet(
            f"color: {MUTED}; font-size: 10px; background: transparent;"
        )"""
new_s = """        s = QLabel(window._voice_subtitle(name, premium))
        s.setStyleSheet(
            f"color: {MUTED}; font-size: 11px; background: transparent;"
        )"""
if old_s in t:
    t = t.replace(old_s, new_s, 1)
    print("4. Acento 11px.")

# ---- 5. Tarjeta 74px y espaciado 1 ----
t = t.replace("self.setFixedHeight(78)", "self.setFixedHeight(74)", 1)
t = t.replace("tl.setSpacing(2)", "tl.setSpacing(1)", 1)
print("5. Tarjeta 74px, espaciado 1.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
