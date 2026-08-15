from pathlib import Path

t = Path("ui/main_window.py").read_text(encoding="utf-8")
lines = t.split("\n")

print("=== _check_license() ===")
for i, ln in enumerate(lines, 1):
    if "def _check_license" in ln:
        print(f"\n--- {i}: {ln} ---")
        # Imprimir hasta el siguiente def
        end = i + 50
        for j in range(i, min(len(lines), end)):
            if j > i and lines[j].startswith("    def "):
                break
            print(f"{j+1:5} | {lines[j]}")
