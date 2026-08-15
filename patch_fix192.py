from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

old = """            adapter = self.engine.adapter
            if self.voice:
                adapter.set_voice(self.voice)
            adapter.set_rate(self.rate)"""
new = """            adapter = self.engine.adapter
            if self.voice:
                try:
                    adapter.set_voice(self.voice)
                except Exception:
                    first = str(self.voice).split()[0].lower()
                    try:
                        for token in adapter.sapi.GetVoices():
                            if first in token.GetDescription().lower():
                                adapter.sapi.Voice = token
                                break
                    except Exception:
                        pass
            adapter.set_rate(self.rate)"""
if old in t:
    t = t.replace(old, new, 1)
    print("Fallback de voz por primera palabra aplicado (todas las voces).")
else:
    print("AVISO: ancla no encontrada.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
