from pathlib import Path
t = Path("ui/modern_window.py").read_text(encoding="utf-8")

print("=== player_timer: conexion ===")
for i, ln in enumerate(t.splitlines(), 1):
    if "player_timer" in ln and "connect" in ln:
        print(f"{i}: {ln.strip()[:110]}")

print("\n=== Zona 1730-1870 (tick / offset / ratio) ===")
lines = t.splitlines()
for i in range(1729, min(1870, len(lines))):
    print(f"{i+1}: {lines[i]}")
