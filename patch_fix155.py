from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# ---- 1. RECOPILACION ----
print("deferred actual:", t.find("def _deferred_rebuilds"))

# ---- 2. Rebuilds -> update in-place ----
old = """def _deferred_rebuilds(self):
    self._rebuild_cards()
    self._rebuild_all_page()
    self._rebuild_fav_page()"""
new = """def _deferred_rebuilds(self):
    for w in self.findChildren(VoiceCard):
        w.set_selected(w.voice_name == self._selected_voice)"""
if old in t:
    t = t.replace(old, new, 1)
    print("2. Seleccion in-place (sin reconstruir tarjetas).")

# ---- 3. Menos latencia ----
t = t.replace(
    "QTimer.singleShot(250, self._deferred_rebuilds)",
    "QTimer.singleShot(60, self._deferred_rebuilds)",
    1,
)
print("3. Latencia 250ms -> 60ms.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
