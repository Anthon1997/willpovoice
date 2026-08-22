from __future__ import annotations

import base64
import getpass
import hashlib
import hmac
import json
import secrets
import socket
from datetime import datetime, timedelta
from pathlib import Path

SECRET = b"willpovoice-2026-secret"
SECRET_V2 = b"willpovoice-v2-tiered-2026"
TRIAL_DAYS = 7
DATA_DIR = Path.home() / ".willpovoice"
DATA_FILE = DATA_DIR / "license.json"

TIER_LABELS = {"M": "Pro Mensual", "A": "Pro Anual", "L": "Pro de por vida"}
TIER_DAYS = {"M": 30, "A": 365, "L": None}


def get_machine_id() -> str:
    raw = ""
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography"
        )
        raw, _ = winreg.QueryValueEx(key, "MachineGuid")
        winreg.CloseKey(key)
    except Exception:
        raw = f"{socket.gethostname()}|{getpass.getuser()}|willpo"
    return hashlib.sha256(raw.encode()).hexdigest()[:8].upper()


# ---------------- Legacy (vinculada a maquina) ----------------
def generate_key(machine_id: str) -> str:
    digest = hmac.new(SECRET, machine_id.upper().encode(), hashlib.sha256).hexdigest()
    body = digest[:16].upper()
    return f"WVP-{body[0:4]}-{body[4:8]}-{body[8:12]}-{body[12:16]}"


# ---------------- V2 (claves de venta por nivel) ----------------
def generate_key_v2(tier: str) -> str:
    if tier not in TIER_DAYS:
        raise ValueError("Nivel invalido. Usa M, A o L.")
    now = datetime.now()
    days = TIER_DAYS[tier]
    payload = [
        tier,
        now.strftime("%Y%m%d"),
        "" if days is None else (now + timedelta(days=days)).strftime("%Y%m%d"),
        secrets.token_hex(3).upper(),
    ]
    pb = base64.b32encode(
        json.dumps(payload, separators=(",", ":")).encode()
    ).decode().rstrip("=")
    sig = hmac.new(SECRET_V2, pb.encode(), hashlib.sha256).hexdigest()[:12].upper()
    full = pb + sig
    return "WVP2-" + "-".join(full[i:i + 4] for i in range(0, len(full), 4))


def _parse_v2(key: str) -> dict | None:
    clean = "".join(key.strip().upper().split())
    if not clean.startswith("WVP2"):
        return None
    body = clean[4:].lstrip("-")
    if len(body) <= 12:
        return None
    pb, sig = body[:-12], body[-12:]
    calc = hmac.new(SECRET_V2, pb.encode(), hashlib.sha256).hexdigest()[:12].upper()
    if not hmac.compare_digest(calc, sig):
        return None
    pad = "=" * ((8 - len(pb) % 8) % 8)
    try:
        payload = json.loads(base64.b32decode(pb + pad).decode())
        tier, iss, exp, _rnd = payload
    except Exception:
        return None
    if tier not in TIER_DAYS:
        return None
    return {"clean": "WVP2" + pb + sig, "t": tier, "iss": iss, "exp": exp}


def validate_key_v2(key: str, bind: bool = True) -> dict | None:
    info = _parse_v2(key)
    if info is None:
        return None
    machine_id = get_machine_id()
    data = load_data()
    binds = data.get("bindings", {})
    expected = hmac.new(
        SECRET_V2, (info["clean"] + "|" + machine_id).encode(), hashlib.sha256
    ).hexdigest()[:16]
    stored = binds.get(info["clean"], "")
    if stored:
        if not hmac.compare_digest(stored, expected):
            return None
    elif bind:
        binds[info["clean"]] = expected
        data["bindings"] = binds
        save_data(data)
    return info


def validate_key(key: str, machine_id: str) -> bool:
    clean = "".join(key.strip().upper().split())
    if clean.startswith("WVP2"):
        return validate_key_v2(key) is not None
    return hmac.compare_digest(clean, generate_key(machine_id))


def load_data() -> dict:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_data(data: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def check_status() -> tuple:
    data = load_data()
    machine_id = get_machine_id()
    key = data.get("license_key", "")
    if key:
        clean = "".join(key.strip().upper().split())
        if clean.startswith("WVP2"):
            info = validate_key_v2(key)
            if info:
                if not info["exp"]:
                    return "licensed", 0
                days_left = (
                    datetime.strptime(info["exp"], "%Y%m%d") - datetime.now()
                ).days
                if days_left >= 0:
                    return "licensed", days_left
                return "expired", 0
        elif validate_key(key, machine_id):
            return "licensed", 0
    first_run = data.get("first_run", "")
    now = datetime.now()
    if not first_run:
        first_run = now.isoformat()
        data["first_run"] = first_run
        save_data(data)
    days_left = TRIAL_DAYS - (now - datetime.fromisoformat(first_run)).days
    if days_left >= 0:
        return "trial", days_left
    return "expired", 0


def license_details() -> dict:
    state, days = check_status()
    key = data_key = load_data().get("license_key", "")
    tier = ""
    if state == "licensed" and data_key:
        clean = "".join(data_key.strip().upper().split())
        if clean.startswith("WVP2"):
            info = _parse_v2(data_key)
            tier = TIER_LABELS.get(info["t"], "Pro") if info else "Pro"
        else:
            tier = "Licencia clasica"
    return {"state": state, "days_left": days, "tier": tier}

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

