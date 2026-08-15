from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# ---- 1. RECOPILACION de paginas (para optimizar despues) ----
for m in ("def _rebuild_all_page", "def _rebuild_fav_page",
          "def _rebuild_cards"):
    i = t.find(m)
    j = t.find("\ndef ", i + 10)
    print(f"===== {m} =====")
    print(t[i:j if j != -1 else i + 900])

# ---- 2. Seleccion instantanea (sin timer) ----
t = t.replace(
    "QTimer.singleShot(60, self._deferred_rebuilds)",
    "self._deferred_rebuilds()",
    1,
)
print("2. Seleccion inmediata (sin singleShot).")

# ---- 3. Solo repintar tarjetas que cambian ----
old = """def _deferred_rebuilds(self):
    for w in self.findChildren(VoiceCard):
        w.set_selected(w.voice_name == self._selected_voice)"""
new = """def _deferred_rebuilds(self):
    for w in self.findChildren(VoiceCard):
        sel = (w.voice_name == self._selected_voice)
        if getattr(w, "_is_sel", None) != sel:
            w._is_sel = sel
            w.set_selected(sel)"""
if old in t:
    t = t.replace(old, new, 1)
    print("3. Repintado diferencial (2 tarjetas por click).")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
