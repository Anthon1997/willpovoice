"""Sistema de tokens para el modo prueba de WillpoVoice.
   Anti-reinstalacion: marca persistente en 3 sitios, firmada con HMAC."""
from __future__ import annotations
import json, os, hashlib, hmac, base64
from pathlib import Path
from datetime import datetime

TRIAL_TOKENS = 5000          
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

