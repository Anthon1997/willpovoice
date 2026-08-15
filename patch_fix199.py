from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# ---- 1. _on_combo_voice: aceptar string O dict ----
old_c = """    # Extraer description del dict y usar el matcher del adapter
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
new_c = """    # UserRole puede ser string (descripcion) o dict
    if isinstance(token, dict):
        desc = token.get("description", "") or voz_texto
    else:
        desc = token or voz_texto
    try:
        self.engine.adapter.set_voice(desc)
        self.statusBar().showMessage(f"Voz cambiada: {voz_texto}")
        self._last_synth_key = None
    except Exception as exc:
        self.statusBar().showMessage(f"Error al cambiar voz: {exc}")"""
if old_c in t:
    t = t.replace(old_c, new_c, 1)
    print("1. _on_combo_voice acepta string o dict.")

# ---- 2. speak_text: aceptar string O dict ----
old_s = """        voice_data = self.voice_combo.currentData(Qt.ItemDataRole.UserRole)
        if voice_data and isinstance(voice_data, dict):
            desc = voice_data.get("description", "")
            try:
                self.engine.adapter.set_voice(desc)
            except Exception:
                pass"""
new_s = """        voice_data = self.voice_combo.currentData(Qt.ItemDataRole.UserRole)
        if isinstance(voice_data, dict):
            desc = voice_data.get("description", "") or ""
        else:
            desc = voice_data or ""
        if desc:
            try:
                self.engine.adapter.set_voice(desc)
            except Exception:
                pass"""
if old_s in t:
    t = t.replace(old_s, new_s, 1)
    print("2. speak_text acepta string o dict.")

# ---- 3. Debug vivo: mostrar state mientras carga ----
old_d = """    if not getattr(self, "_saw_running", False):
        if state == 2:
            self._saw_running = True
            self._set_player_icon(True, loading=False)
            self.statusBar().showMessage("Reproduciendo...")
        else:
            return"""
new_d = """    if not getattr(self, "_saw_running", False):
        if state == 2:
            self._saw_running = True
            self._set_player_icon(True, loading=False)
            self.statusBar().showMessage("Reproduciendo...")
        else:
            self.statusBar().showMessage(
                f"Cargando voz... (state={state})")
            return"""
if old_d in t:
    t = t.replace(old_d, new_d, 1)
    print("3. Debug vivo de state en barra de estado.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
