from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")
cambios = 0

# ---- 1. Espia de _on_combo_voice ----
old = """    import traceback
    self.logger.info(
        "DEBUG combo disparado POR: %s",
        " | ".join(
            ln.strip() for ln in traceback.format_stack()[-6:-1]))
    data = self.voice_combo.currentData(Qt.ItemDataRole.UserRole)"""
new = """    data = self.voice_combo.currentData(Qt.ItemDataRole.UserRole)"""
if old in t:
    t = t.replace(old, new, 1); cambios += 1
    print("1. Espia de combo eliminado.")

# ---- 2. Espia de _select_voice ----
old = """    import traceback
    self.logger.info("DEBUG _select_voice: %s", " | ".join(x.strip() for x in traceback.format_stack()[-5:-1]))
"""
if old in t:
    t = t.replace(old, "", 1); cambios += 1
    print("2. Espia de _select_voice eliminado.")

# ---- 3. speak_text ----
old = """        self.logger.info("DEBUG speak_text: voz=%s texto_len=%d",
                        self.engine.adapter.current_voice_description, len(text))
        self.engine.speak_async(text)
        self.logger.info("DEBUG speak_text: speak_async lanzado")
        self.player_timer.start(100)
        self._tick_log_counter = 0"""
new = """        self.engine.speak_async(text)
        self.player_timer.start(100)"""
if old in t:
    t = t.replace(old, new, 1); cambios += 1
    print("3. Logs de speak_text eliminados.")

# ---- 4. Tick: rama de carga limpia ----
old = """    if not getattr(self, "_saw_running", False):
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
new = """    if not getattr(self, "_saw_running", False):
        if state == 2:
            self._saw_running = True
            self._set_player_icon(True, loading=False)
            self.statusBar().showMessage("Reproduciendo...")
        else:
            return"""
if old in t:
    t = t.replace(old, new, 1); cambios += 1
    print("4. Tick de carga limpio.")

# ---- 5. Tick: terminado sin log ----
old = """        self.logger.info("DEBUG terminado con state=%d secs=%.1f",
                        state, getattr(self, "_seconds", 0))
        self.player_timer.stop()"""
new = """        self.player_timer.stop()"""
if old in t:
    t = t.replace(old, new, 1); cambios += 1
    print("5. Log de terminado eliminado.")

# ---- 6. Tick: progreso sin log ----
old = """    if state == 2:
        self._run_log = getattr(self, "_run_log", 0) + 1
        if self._run_log % 10 == 0:
            self.logger.info("DEBUG reproduciendo: tick=%d secs=%.1f",
                            self._run_log, secs)
        self._seconds = secs"""
new = """    if state == 2:
        self._seconds = secs"""
if old in t:
    t = t.replace(old, new, 1); cambios += 1
    print("6. Log de progreso eliminado.")

p.write_text(t, encoding="utf-8")
print(f"Limpieza completada: {cambios}/6 bloques.")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
