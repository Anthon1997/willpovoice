"""Sistema de tokens para el modo prueba de WillpoVoice."""
import json
import os
import hashlib
from pathlib import Path

TRIAL_TOKENS = 10000
BASE_COST = 50
PER_CHARS = 20
_SALT = "willpovoice_tokens_v1"


def _machine():
    import getpass
    import socket
    raw = f"{socket.gethostname()}|{getpass.getuser()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _sig(bal, used):
    return hashlib.sha256(
        f"{bal}|{used}|{_machine()}|{_SALT}".encode("utf-8")).hexdigest()


def _path():
    d = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "WillpoVoice"
    d.mkdir(parents=True, exist_ok=True)
    return d / "trial_tokens.json"


def _save(bal, used, conv):
    _path().write_text(json.dumps(
        {"bal": bal, "used": used, "conv": conv,
         "sig": _sig(bal, used)}, indent=2), encoding="utf-8")


def _load():
    p = _path()
    if not p.exists():
        return None
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        if str(d.get("sig")) != _sig(int(d["bal"]), int(d["used"])):
            return {"bal": 0, "used": 0, "conv": 0, "tampered": True}
        return d
    except Exception:
        return None


def ensure_init():
    if _load() is None:
        _save(TRIAL_TOKENS, 0, 0)


def balance():
    d = _load()
    return TRIAL_TOKENS if d is None else int(d.get("bal", 0))


def cost_for(text):
    n = len(text or "")
    return BASE_COST + (n + PER_CHARS - 1) // PER_CHARS


def spend(text):
    ensure_init()
    d = _load() or {"bal": TRIAL_TOKENS, "used": 0, "conv": 0}
    c = cost_for(text)
    bal = int(d.get("bal", 0))
    if bal < c:
        return False, c, bal
    bal -= c
    _save(bal, int(d.get("used", 0)) + c, int(d.get("conv", 0)) + 1)
    return True, c, bal
