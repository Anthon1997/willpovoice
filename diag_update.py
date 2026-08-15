from pathlib import Path

t = Path("ui/modern_window.py").read_text(encoding="utf-8")

print("=== UpdateWorker + DownloadWorker + dialogo (2290-2470) ===")
lines = t.splitlines()
for i in range(2289, min(2470, len(lines))):
    print(f"{i+1}: {lines[i]}")

print("\n=== Donde se arranca el chequeo de actualizacion ===")
for i, ln in enumerate(lines, 1):
    if "_update_worker" in ln or "check_update" in ln.lower() or "update" in ln.lower() and "start" in ln.lower():
        print(f"{i}: {ln.strip()[:110]}")
