from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

old = """def _on_combo_voice(self):
    data = self.voice_combo.currentData(Qt.ItemDataRole.UserRole)"""
new = """def _on_combo_voice(self):
    import traceback
    self.logger.info(
        "DEBUG combo disparado POR: %s",
        " | ".join(
            ln.strip() for ln in traceback.format_stack()[-6:-1]))
    data = self.voice_combo.currentData(Qt.ItemDataRole.UserRole)"""
if old in t:
    t = t.replace(old, new, 1)
    p.write_text(t, encoding="utf-8")
    print("Espia de pila de llamadas instalado en _on_combo_voice.")
else:
    print("AVISO: ancla no encontrada.")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
