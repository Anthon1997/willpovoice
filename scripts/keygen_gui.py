import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import tkinter as tk

try:
    from core.license_manager import generate_key
except Exception:
    import hashlib
    import hmac

    SECRET = b"willpovoice-2026-secret"

    def generate_key(machine_id: str) -> str:
        digest = hmac.new(
            SECRET, machine_id.upper().encode(), hashlib.sha256
        ).hexdigest()
        body = digest[:16].upper()
        return f"WVP-{body[0:4]}-{body[4:8]}-{body[8:12]}-{body[12:16]}"


def main() -> None:
    root = tk.Tk()
    root.title("WillpoVoice - Generador de Licencias")
    root.geometry("430x230")
    root.resizable(False, False)
    root.configure(bg="#0d2b26")

    tk.Label(
        root,
        text="WillpoVoice - Generador de Licencias",
        font=("Segoe UI", 12, "bold"),
        bg="#0d2b26",
        fg="#4de3b0",
    ).pack(pady=(14, 8))

    tk.Label(
        root,
        text="ID de maquina del cliente:",
        font=("Segoe UI", 10),
        bg="#0d2b26",
        fg="white",
    ).pack()

    id_var = tk.StringVar()
    entry = tk.Entry(
        root, textvariable=id_var, width=32, font=("Consolas", 11)
    )
    entry.pack(pady=(4, 8))

    key_var = tk.StringVar(value="")

    def generate() -> None:
        mid = id_var.get().strip().upper()

        if len(mid) < 4:
            key_var.set("ID invalido")
            return

        key_var.set(generate_key(mid))

    def copy_key() -> None:
        if key_var.get() and key_var.get() != "ID invalido":
            root.clipboard_clear()
            root.clipboard_append(key_var.get())

    tk.Button(
        root, text="Generar clave", command=generate, width=22
    ).pack(pady=(0, 8))

    tk.Label(
        root,
        textvariable=key_var,
        font=("Consolas", 13, "bold"),
        bg="#0d2b26",
        fg="#ffd75e",
    ).pack()

    tk.Button(
        root, text="Copiar al portapapeles", command=copy_key, width=22
    ).pack(pady=(6, 12))

    root.mainloop()


if __name__ == "__main__":
    main()

