from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# ---- 1. Espia en _select_voice (click en tarjeta) ----
old_sv = "def _select_voice(self"
i = t.find(old_sv)
if i != -1:
    # insertar al inicio del cuerpo
    j = t.find("\n", i)
    body_start = t.find("\n", j)  # tras la linea def
    # encontrar primera linea de codigo
    k = t.find("def ", i + 5)
    snippet = t[i:k if k != -1 else i + 600]
    if "DEBUG _select_voice" not in snippet:
        # insertar despues de la linea def
        nl = t.find("\n", i)
        indent = "\n    "
        spy = indent + 'import traceback'
        spy += indent + 'self.logger.info("DEBUG _select_voice: %s", " | ".join(x.strip() for x in traceback.format_stack()[-5:-1]))'
        t = t[:nl] + spy + t[nl:]
        print("1. Espia en _select_voice.")
else:
    print("AVISO: _select_voice no encontrado.")

# ---- 2. Log en rama 'terminado' con el state que la dispara ----
old_term = """    if state != 2:
        import time as _time
        if _time.time() - getattr(self, "_resume_at", 0.0) < 1.0:
            return
        self.player_timer.stop()"""
new_term = """    if state != 2:
        import time as _time
        if _time.time() - getattr(self, "_resume_at", 0.0) < 1.0:
            return
        self.logger.info("DEBUG terminado con state=%d secs=%.1f",
                        state, getattr(self, "_seconds", 0))
        self.player_timer.stop()"""
if old_term in t:
    t = t.replace(old_term, new_term, 1)
    print("2. Log en rama terminado.")

# ---- 3. Log de estado cada 10 ticks mientras reproduce ----
old_run = """    if state == 2:
        self._seconds = secs"""
new_run = """    if state == 2:
        self._run_log = getattr(self, "_run_log", 0) + 1
        if self._run_log % 10 == 0:
            self.logger.info("DEBUG reproduciendo: tick=%d secs=%.1f",
                            self._run_log, secs)
        self._seconds = secs"""
if old_run in t:
    t = t.replace(old_run, new_run, 1)
    print("3. Log de progreso cada 10 ticks.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
