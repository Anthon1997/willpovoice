from __future__ import annotations

import getpass
import hashlib
import hmac
import json
import socket
from datetime import datetime
from pathlib import Path

SECRET = b"willpovoice-2026-secret"
TRIAL_DAYS = 7
DATA_DIR = Path.home() / ".willpovoice"
DATA_FILE = DATA_DIR / "license.json"


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


def generate_key(machine_id: str) -> str:
    digest = hmac.new(SECRET, machine_id.upper().encode(), hashlib.sha256).hexdigest()
    body = digest[:16].upper()
    return f"WVP-{body[0:4]}-{body[4:8]}-{body[8:12]}-{body[12:16]}"


def validate_key(key: str, machine_id: str) -> bool:
    clean = "".join(key.strip().upper().split())
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

    if key and validate_key(key, machine_id):
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
