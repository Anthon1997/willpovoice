from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# ---- 1. _on_combo_voice: extraer description del dict ----
old_combo = """    # Asignar el token COM directamente al adapter (salta el matcher)
    if token:
        try:
            self.engine.adapter.sapi.Voice = token
            self.statusBar().showMessage(f"Voz cambiada: {voz_texto}")
            # Invalidar la ultima sintesis para que Play resintetice
            self._last_synth_key = None
        except Exception as exc:
            self.statusBar().showMessage(f"Error al cambiar voz: {exc}")
    else:
        self.statusBar().showMessage(f"Voz: {voz_texto} (sin token)")"""
new_combo = """    # Extraer description del dict y usar el matcher del adapter
    if token and isinstance(token, dict):
        desc = token.get("description", voz_texto)
        try:
            self.engine.adapter.set_voice(desc)
            self.statusBar().showMessage(f"Voz cambiada: {voz_texto}")
            self._last_synth_key = None
        except Exception as exc:
            self.statusBar().showMessage(f"Error al cambiar voz: {exc}")
    else:
        self.statusBar().showMessage(f"Voz: {voz_texto} (formato inesperado)")"""
if old_combo in t:
    t = t.replace(old_combo, new_combo, 1)
    print("1. _on_combo_voice extrae description del dict.")

# ---- 2. speak_text: extraer description del dict ----
old_speak = """        voice_token = self.voice_combo.currentData(Qt.ItemDataRole.UserRole)
        if voice_token:
            try:
                self.engine.adapter.sapi.Voice = voice_token
            except Exception:
                pass"""
new_speak = """        voice_data = self.voice_combo.currentData(Qt.ItemDataRole.UserRole)
        if voice_data and isinstance(voice_data, dict):
            desc = voice_data.get("description", "")
            try:
                self.engine.adapter.set_voice(desc)
            except Exception:
                pass"""
if old_speak in t:
    t = t.replace(old_speak, new_speak, 1)
    print("2. speak_text extrae description del dict.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
