from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# ---- 1. speak_text: log de entrada y salida ----
old_s = """        self.engine.speak_async(text)
        self.player_timer.start(100)"""
new_s = """        self.logger.info("DEBUG speak_text: voz=%s texto_len=%d",
                        self.engine.adapter.current_voice_description, len(text))
        self.engine.speak_async(text)
        self.logger.info("DEBUG speak_text: speak_async lanzado")
        self.player_timer.start(100)
        self._tick_log_counter = 0"""
if old_s in t:
    t = t.replace(old_s, new_s, 1)
    print("1. speak_text loggea voz y texto.")

# ---- 2. _tick_player: log cada 5 ticks mientras carga ----
old_t = """    if not getattr(self, "_saw_running", False):
        if state == 2:
            self._saw_running = True
            self._set_player_icon(True, loading=False)
            self.statusBar().showMessage("Reproduciendo...")
        else:
            self.statusBar().showMessage(
                f"Cargando voz... (state={state})")
            return"""
new_t = """    if not getattr(self, "_saw_running", False):
        cnt = getattr(self, "_tick_log_counter", 0) + 1
        self._tick_log_counter = cnt
        if cnt % 5 == 0 or state == 2:
            try:
                desc = self.engine.adapter.current_voice_description
            except Exception:
                desc = "?"
            self.logger.info(
                "DEBUG tick cargando: cnt=%d state=%d voz=%s",
                cnt, state, desc)
        if state == 2:
            self._saw_running = True
            self._set_player_icon(True, loading=False)
            self.statusBar().showMessage("Reproduciendo...")
            self._tick_log_counter = 0
        else:
            self.statusBar().showMessage(
                f"Cargando voz... (state={state}, tick={cnt})")
            return"""
if old_t in t:
    t = t.replace(old_t, new_t, 1)
    print("2. _tick_player loggea state cada 5 ticks.")

# ---- 3. _on_combo_voice: log al cambiar voz ----
old_c = """    try:
        self.engine.adapter.set_voice(desc)
        self.statusBar().showMessage(f"Voz cambiada: {voz_texto}")
        self._last_synth_key = None
    except Exception as exc:
        self.statusBar().showMessage(f"Error al cambiar voz: {exc}")"""
new_c = """    try:
        self.engine.adapter.set_voice(desc)
        self.logger.info("DEBUG cambio voz: %s -> %s",
                        voz_texto,
                        self.engine.adapter.current_voice_description)
        self.statusBar().showMessage(f"Voz cambiada: {voz_texto}")
        self._last_synth_key = None
    except Exception as exc:
        self.statusBar().showMessage(f"Error al cambiar voz: {exc}")"""
if old_c in t:
    t = t.replace(old_c, new_c, 1)
    print("3. _on_combo_voice loggea cambio.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
