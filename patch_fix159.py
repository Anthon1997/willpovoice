from pathlib import Path

# ================= core/license_manager.py (nuevo) =================
lm = r'''from __future__ import annotations

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
'''
Path("core/license_manager.py").write_text(lm, encoding="utf-8")
print("license_manager.py V2 escrito.")

# ================= scripts/keygen.py =================
kg = r'''from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.license_manager import generate_key, generate_key_v2


def main() -> None:
    args = [a.strip().upper() for a in sys.argv[1:]]
    if args and args[0] in ("M", "A", "L"):
        print(f"Clave de venta ({args[0]}): {generate_key_v2(args[0])}")
    else:
        mid = args[0] if args else input("ID de maquina: ").strip().upper()
        print(f"Clave legacy para {mid}: {generate_key(mid)}")


if __name__ == "__main__":
    main()
'''
Path("scripts/keygen.py").write_text(kg, encoding="utf-8")
print("keygen.py actualizado.")

# ================= scripts/keygen_gui.py =================
kgui = r'''import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import tkinter as tk

from core.license_manager import TIER_LABELS, generate_key, generate_key_v2


def main() -> None:
    root = tk.Tk()
    root.title("WillpoVoice - Generador de Licencias")
    root.geometry("620x400")
    root.resizable(False, False)
    root.configure(bg="#0d2b26")

    tk.Label(
        root, text="WillpoVoice - Generador de Licencias",
        font=("Segoe UI", 12, "bold"), bg="#0d2b26", fg="#4de3b0",
    ).pack(pady=(12, 6))

    tk.Label(
        root, text="Claves de venta V2 (sin ID de maquina):",
        font=("Segoe UI", 10, "bold"), bg="#0d2b26", fg="white",
    ).pack()

    tier_var = tk.StringVar(value="A")
    row = tk.Frame(root, bg="#0d2b26")
    row.pack(pady=(4, 6))
    for code in ("M", "A", "L"):
        tk.Radiobutton(
            row, text=TIER_LABELS[code], variable=tier_var, value=code,
            bg="#0d2b26", fg="white", selectcolor="#134e42",
            activebackground="#0d2b26", font=("Segoe UI", 9),
        ).pack(side=tk.LEFT, padx=8)

    key_var = tk.StringVar(value="")
    tk.Button(
        root, text="Generar clave de venta",
        command=lambda: key_var.set(generate_key_v2(tier_var.get())),
        width=28,
    ).pack()

    txt = tk.Text(root, height=3, width=70, font=("Consolas", 9))
    txt.pack(pady=(6, 4))

    def show_key(*_):
        txt.delete("1.0", tk.END)
        txt.insert(tk.END, key_var.get())

    key_var.trace_add("write", show_key)

    tk.Button(
        root,
        text="Copiar al portapapeles",
        command=lambda: (root.clipboard_clear(), root.clipboard_append(key_var.get())),
        width=28,
    ).pack()

    tk.Label(
        root, text="Clave legacy por ID de maquina:",
        font=("Segoe UI", 10, "bold"), bg="#0d2b26", fg="white",
    ).pack(pady=(10, 2))
    id_var = tk.StringVar()
    tk.Entry(root, textvariable=id_var, width=32, font=("Consolas", 11)).pack()
    legacy_var = tk.StringVar(value="")

    def generate_legacy() -> None:
        mid = id_var.get().strip().upper()
        legacy_var.set(generate_key(mid) if len(mid) >= 4 else "ID invalido")

    tk.Button(root, text="Generar clave legacy", command=generate_legacy, width=28).pack(pady=(2, 4))
    tk.Label(
        root, textvariable=legacy_var, font=("Consolas", 11, "bold"),
        bg="#0d2b26", fg="#ffd75e",
    ).pack()

    root.mainloop()


if __name__ == "__main__":
    main()
'''
Path("scripts/keygen_gui.py").write_text(kgui, encoding="utf-8")
print("keygen_gui.py actualizado.")
