from pathlib import Path
t = Path("ui/modern_window.py").read_text(encoding="utf-8")

print("=== Combo de idioma y su conexion ===")
for i, ln in enumerate(t.splitlines(), 1):
    if "lang" in ln.lower() or "idioma" in ln.lower():
        print(f"{i}: {ln.strip()[:100]}")

print("\n=== Funciones que construyen tarjetas ===")
for name in ["_append_rec_cards", "_append_all_cards", "_rebuild_cards", "_filter"]:
    i = t.find(f"def {name}")
    if i != -1:
        j = t.find("\ndef ", i + 10)
        print(f"\n----- def {name} -----")
        print(t[i:j if j != -1 else i+1800])
