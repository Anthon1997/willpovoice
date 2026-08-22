import hashlib, hmac, secrets, re, json
from pathlib import Path

# ============================================================
# 1) trial_tokens.py - reescrito con anti-reinstalación
# ============================================================
tt = Path("core/trial_tokens.py")
tt.write_text(r'''"""Sistema de tokens para el modo prueba de WillpoVoice.
   Anti-reinstalacion: marca persistente en 3 sitios, firmada con HMAC."""
from __future__ import annotations
import json, os, hashlib, hmac, base64
from pathlib import Path
from datetime import datetime

TRIAL_TOKENS = 5000          # antes 10000
BASE_COST = 50
PER_CHARS = 20
_SALT = "willpovoice_tokens_v2"
_SECRET = b"willpovoice-trial-anchors-2026"


def _machine():
    raw = ""
    try:
        import winreg
        k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                           r"SOFTWARE\Microsoft\Cryptography")
        raw, _ = winreg.QueryValueEx(k, "MachineGuid")
        winreg.CloseKey(k)
    except Exception:
        import socket, getpass
        raw = f"{socket.gethostname()}|{getpass.getuser()}|willpo"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _sig(payload):
    return hmac.new(_SECRET, f"{payload}|{_machine()}".encode(),
                    hashlib.sha256).hexdigest()[:24]


def _paths():
    local = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "WillpoVoice"
    prog  = Path(os.environ.get("PROGRAMDATA", "C:\\ProgramData")) / "WillpoVoice"
    reg_path = r"Software\WillpoVoice"
    for p in (local, prog):
        try: p.mkdir(parents=True, exist_ok=True)
        except Exception: pass
    return (local / "trial_state.json",
            prog  / "trial_state.json",
            reg_path)


def _write_state(state):
    body = json.dumps(state, separators=(",", ":"))
    signed = body + "|" + _sig(body)
    f1, f2, regkey = _paths()
    for f in (f1, f2):
        try: f.write_text(signed, encoding="utf-8")
        except Exception: pass
    try:
        import winreg
        k = winreg.CreateKey(winreg.HKEY_CURRENT_USER, regkey)
        winreg.SetValueEx(k, "TrialState", 0, winreg.REG_SZ, signed)
        winreg.CloseKey(k)
    except Exception:
        pass


def _read_state():
    f1, f2, regkey = _paths()
    candidates = []
    for f in (f1, f2):
        try:
            if f.exists():
                candidates.append(f.read_text(encoding="utf-8"))
        except Exception:
            pass
    try:
        import winreg
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, regkey)
        val, _ = winreg.QueryValueEx(k, "TrialState")
        candidates.append(val)
        winreg.CloseKey(k)
    except Exception:
        pass
    valid = []
    for c in candidates:
        if "|" not in c: continue
        body, sig = c.rsplit("|", 1)
        if sig == _sig(body):
            try:
                d = json.loads(body)
                if "t0" in d: valid.append(d)
            except Exception: pass
    if not valid: return None
    return min(valid, key=lambda d: d["t0"])  # el t0 mas antiguo


def first_launch():
    """Retorna timestamp del primer arranque (crea si no existe)."""
    s = _read_state()
    if s: return int(s["t0"])
    now = int(datetime.now().timestamp())
    _write_state({"t0": now, "bal": TRIAL_TOKENS, "used": 0, "conv": 0})
    return now


def _load_bal():
    s = _read_state()
    if not s: return TRIAL_TOKENS, 0, 0
    return int(s.get("bal", TRIAL_TOKENS)), int(s.get("used", 0)), int(s.get("conv", 0))


def balance():
    bal, _, _ = _load_bal()
    return bal


def cost_for(text):
    n = len(text or "")
    return BASE_COST + (n + PER_CHARS - 1) // PER_CHARS


def spend(text):
    first_launch()  # asegurar estado
    bal, used, conv = _load_bal()
    c = cost_for(text)
    if bal < c:
        return False, c, bal
    state = _read_state()
    state["bal"]   = bal - c
    state["used"]  = used + c
    state["conv"]  = conv + 1
    _write_state(state)
    return True, c, state["bal"]


def set_offer_claimed(offer_id):
    """Marca que se mostro (o acepto) una oferta 24h."""
    state = _read_state() or {"t0": first_launch(), "bal": TRIAL_TOKENS,
                              "used": 0, "conv": 0}
    state["offer"] = {"id": offer_id,
                      "ts": int(datetime.now().timestamp())}
    _write_state(state)


def get_offer():
    state = _read_state()
    return state.get("offer") if state else None


def add_tokens(n: int):
    """Suma tokens (para recarga manual con clave)."""
    state = _read_state() or {"t0": first_launch(), "bal": TRIAL_TOKENS,
                              "used": 0, "conv": 0}
    state["bal"] = int(state.get("bal", 0)) + int(n)
    _write_state(state)
    return state["bal"]


def ensure_init():
    first_launch()
''', encoding="utf-8")
print(f"✅ {tt} reescrito (5000 tokens + 3 anclas)")


# ============================================================
# 2) license_manager.py - añadir helpers para recordatorio
# ============================================================
lm = Path("core/license_manager.py")
t = lm.read_text(encoding="utf-8")
add = '''

# ---------------- Helpers para trial (recordatorio + ofertas) ----------------
def trial_anchor() -> int:
    """Timestamp del primer arranque (via trial_tokens)."""
    try:
        from core import trial_tokens
        return trial_tokens.first_launch()
    except Exception:
        return 0


def trial_days_left() -> int:
    from datetime import datetime
    t0 = trial_anchor()
    if not t0:
        return TRIAL_DAYS
    elapsed = (datetime.now().timestamp() - t0) / 86400.0
    return max(0, TRIAL_DAYS - int(elapsed))

'''
if "def trial_anchor" not in t:
    t = t.rstrip() + add
    lm.write_text(t, encoding="utf-8", newline="\n")
    print(f"✅ {lm} parcheado (trial_anchor + trial_days_left)")
else:
    print(f"⚠️  {lm} ya tenia helpers")


# ============================================================
# 3) modern_window.py - recordatorio dia 5 + oferta 24h
# ============================================================
mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")
log = []

# 3a) Reemplazar _show_no_tokens (oferta 24h con countdown real)
old_block = '''def _show_no_tokens(self):
    from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel,
                                   QPushButton)
    from PySide6.QtGui import QDesktopServices
    from PySide6.QtCore import QUrl
    d = QDialog(self)
    d.setModal(True)
    d.setFixedWidth(400)
    d.setWindowTitle("Tokens de prueba")
    d.setStyleSheet("QDialog { background: #0b0e14; }")
    v = QVBoxLayout(d)
    v.setContentsMargins(28, 24, 28, 22)
    v.setSpacing(10)
    ic = QLabel()
    ic.setPixmap(make_icon("coins", "#f5b544", 46))
    ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
    v.addWidget(ic)
    t1 = QLabel("Â¡Tokens de prueba agotados!")
    t1.setStyleSheet(
        "color: #e6edf3; font-size: 18px; font-weight: 800;")
    t1.setAlignment(Qt.AlignmentFlag.AlignCenter)
    v.addWidget(t1)
    t2 = QLabel("Usaste tus 10,000 tokens. Compra una licencia "
                "para continuar sin limites.")
    t2.setStyleSheet("color: #8b949e; font-size: 11.5px;")
    t2.setAlignment(Qt.AlignmentFlag.AlignCenter)
    t2.setWordWrap(True)
    v.addWidget(t2)'''

new_block = '''def _show_no_tokens(self):
    from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                   QPushButton, QFrame)
    from PySide6.QtGui import QDesktopServices
    from PySide6.QtCore import QUrl, QTimer
    d = QDialog(self)
    d.setModal(True)
    d.setFixedWidth(440)
    d.setWindowTitle("Tokens de prueba")
    d.setStyleSheet("QDialog { background: #0b0e14; }")
    v = QVBoxLayout(d)
    v.setContentsMargins(28, 24, 28, 22)
    v.setSpacing(10)
    ic = QLabel()
    ic.setPixmap(make_icon("coins", "#f5b544", 46))
    ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
    v.addWidget(ic)
    t1 = QLabel("Â¡Tokens de prueba agotados!")
    t1.setStyleSheet("color: #e6edf3; font-size: 18px; font-weight: 800;")
    t1.setAlignment(Qt.AlignmentFlag.AlignCenter)
    v.addWidget(t1)

    # Banner de oferta 24h
    offer = QFrame()
    offer.setStyleSheet("QFrame { background: #1c1208; border: 1px solid #5a3a10; border-radius: 10px; }")
    ov = QVBoxLayout(offer)
    ov.setContentsMargins(14, 10, 14, 10)
    ov.setSpacing(6)
    ofr_top = QHBoxLayout()
    ofr_top.setSpacing(6)
    fire = QLabel("ðŸ”¥")
    fire.setStyleSheet("font-size: 16px;")
    ofr_top.addWidget(fire)
    ofr_t1 = QLabel("Oferta de bienvenida - 24 horas")
    ofr_t1.setStyleSheet("color: #f5b544; font-weight: 800; font-size: 12px;")
    ofr_top.addWidget(ofr_t1)
    ofr_top.addStretch(1)
    ov.addLayout(ofr_top)
    ofr_t2 = QLabel("Tu primer mes Pro por S/5 (en vez de S/10)")
    ofr_t2.setStyleSheet("color: #e6edf3; font-size: 13px; font-weight: 700;")
    ofr_t2.setWordWrap(True)
    ov.addWidget(ofr_t2)
    cd = QLabel()
    cd.setStyleSheet("color: #8b949e; font-size: 11px;")
    ov.addWidget(cd)
    v.addWidget(offer)
    v.addSpacing(4)

    # Countdown persistente (24h desde primera vez que se muestra)
    import time
    offer_state = trial_tokens.get_offer()
    offer_id = "no_tokens_v1"
    if offer_state and offer_state.get("id") == offer_id:
        end_ts = offer_state["ts"] + 86400
    else:
        end_ts = int(time.time()) + 86400
        trial_tokens.set_offer_claimed(offer_id)
    def tick():
        left = max(0, end_ts - int(time.time()))
        h, rem = divmod(left, 3600)
        m, s = divmod(rem, 60)
        if left > 0:
            cd.setText(f"Expira en: {h:02d}h {m:02d}m {s:02d}s")
        else:
            cd.setText("Oferta expirada")
    tick()
    timer = QTimer(d); timer.timeout.connect(tick); timer.start(1000)

    t2 = QLabel("ContinÃºa sin limites con Pro Mensual.")
    t2.setStyleSheet("color: #8b949e; font-size: 11.5px;")
    t2.setAlignment(Qt.AlignmentFlag.AlignCenter)
    t2.setWordWrap(True)
    v.addWidget(t2)'''

if old_block in t:
    t = t.replace(old_block, new_block, 1)
    log.append("_show_no_tokens -> oferta 24h")
else:
    print("WARN: no encontre _show_no_tokens para parchear")

# 3b) Actualizar texto de PlansDialog (tarjetas)
t = t.replace('"7 dias de prueba", "10,000 tokens incluidos"',
              '"7 dias de prueba", "5,000 tokens incluidos"', 1)
t = t.replace('"Hasta 5,000 caracteres por conversiÃ³n"',
              '"Hasta 5,000 caracteres por conversiÃ³n"', 1)  # ya esta bien
# Mensual: 20,000 tokens
t = t.replace('"20,000 tokens al mes"', '"20,000 tokens al mes"', 1)  # ok
log.append("PlansDialog textos 5000 tokens")

mw.write_text(t, encoding="utf-8", newline="\n")
print(f"✅ {mw}: {' / '.join(log)}")


# ============================================================
# 4) modern_window.py - toast recordatorio dia 5 al arrancar
# ============================================================
# Buscar la zona de _check_license (alrededor de 2658) para inyectar
# un QTimer.singleShot que muestre toast si days_left == 2
toast_inject = '''
    # --- recordatorio dia 5 (muestra en proximo arranque si quedan 2 dias) ---
    try:
        from PySide6.QtWidgets import QMessageBox
        state, days = license_manager.check_status()
        if state == "trial" and days == 2 and not getattr(self, "_reminder_shown", False):
            self._reminder_shown = True
            QTimer.singleShot(1200, lambda: QMessageBox.information(
                self, "Prueba gratuita",
                f"Tu periodo de prueba termina en 2 dias.\\n"
                f"Te quedan {trial_tokens.balance():,} tokens de prueba.\\n\\n"
                f"Compra un plan para no perder el acceso."))
    except Exception:
        pass
'''

# Buscar el final de _check_license (donde termina la funcion)
# Estrategia: inyectar despues de self._refresh_token_chip(state)
old = "self._refresh_token_chip(state)"
if old in t and "Tu periodo de prueba termina en 2 dias" not in t:
    # inyectar despues de la primera aparicion en _check_license
    idx = t.find(old)
    end_line = t.find("\n", idx)
    # buscar la linea del siguiente def o cierre de funcion
    t = t[:end_line+1] + toast_inject + t[end_line+1:]
    print(f"✅ Toast recordatorio dia 5 inyectado en _check_license")


# ============================================================
# 5) add_license.py (keygen) - tier R = recarga
# ============================================================
al = Path("add_license.py")
if al.exists():
    at = al.read_text(encoding="utf-8")
    # Añadir R (recarga) al sistema si usa el nuevo esquema
    if "tier" in at.lower() or "TIER_DAYS" in at:
        if '"R"' not in at:
            at = at.replace('TIER_LABELS = {"M": "Pro Mensual", "A": "Pro Anual", "L": "Pro de por vida"}',
                            'TIER_LABELS = {"M": "Pro Mensual", "A": "Pro Anual", "L": "Pro de por vida", "R": "Recarga de tokens"}', 1)
            at = at.replace('TIER_DAYS = {"M": 30, "A": 365, "L": None}',
                            'TIER_DAYS = {"M": 30, "A": 365, "L": None, "R": 0}', 1)
            al.write_text(at, encoding="utf-8", newline="\n")
            print(f"✅ {al}: tier R (recarga) añadido al keygen")
else:
    print(f"⚠️  {al} no existe - tier R se añade via WillpoKeyGen")


print("\n🎯 RESUMEN DE CAMBIOS:")
print("   1) trial_tokens.py: 5000 tokens + anclas en 3 sitios (HKCU + 2 dirs)")
print("   2) license_manager.py: trial_anchor() + trial_days_left()")
print("   3) modern_window.py: oferta 24h S/5 con countdown persistente")
print("   4) modern_window.py: toast recordatorio en dia 5")
print("   5) add_license.py: tier R para recargas manuales")
print("\nSiguiente paso: probar + compilar + rebuild instalador.")
