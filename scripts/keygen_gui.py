import sys
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
