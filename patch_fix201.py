from pathlib import Path
import ast

# ---- 1. Adapter: set_voice purga el stream antes de cambiar ----
pa = Path("adapters/sapi_adapter.py")
a = pa.read_text(encoding="utf-8")
old_sv = """    def set_voice(self, query: str) -> bool:
        \"\"\"
        Selecciona una voz por coincidencia parcial.
        \"\"\"
        token = self._get_voice_token(query)"""
new_sv = """    def set_voice(self, query: str) -> bool:
        \"\"\"
        Selecciona una voz por coincidencia parcial.
        \"\"\"
        self.stop()
        token = self._get_voice_token(query)"""
if old_sv in a:
    a = a.replace(old_sv, new_sv, 1)
    pa.write_text(a, encoding="utf-8")
    print("1. set_voice purga el stream antes de cambiar (adapter).")
else:
    print("AVISO: set_voice no encontrado exacto.")

# ---- 2. speak_text: purga antes de hablar (anti-zombie) ----
pm = Path("ui/modern_window.py")
t = pm.read_text(encoding="utf-8")
old_st = """        voice_data = self.voice_combo.currentData(Qt.ItemDataRole.UserRole)"""
new_st = """        try:
            self.engine.stop()
        except Exception:
            pass
        voice_data = self.voice_combo.currentData(Qt.ItemDataRole.UserRole)"""
if old_st in t:
    t = t.replace(old_st, new_st, 1)
    pm.write_text(t, encoding="utf-8")
    print("2. speak_text purga stream zombie antes de hablar.")
else:
    print("AVISO: ancla speak_text no encontrada.")

try:
    ast.parse(pm.read_text(encoding="utf-8"))
    ast.parse(pa.read_text(encoding="utf-8"))
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
