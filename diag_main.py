from pathlib import Path

t = Path("ui/main_window.py").read_text(encoding="utf-8")
lines = t.split("\n")

print("=== MainWindow __init__ y show ===")
for i, ln in enumerate(lines, 1):
    if "def __init__" in ln and "class " not in ln:
        print(f"\n--- {i}: {ln} ---")
        print("\n".join(f"{j+1:5} | {lines[j]}" for j in range(i-1, min(i+60, len(lines)))))
    elif "def show" in ln and i > 400:
        print(f"\n--- {i}: {ln} ---")
        print("\n".join(f"{j+1:5} | {lines[j]}" for j in range(i-1, min(i+20, len(lines)))))

print("\n=== Llamadas a LicenseDialog ===")
for i, ln in enumerate(lines, 1):
    if "LicenseDialog(" in ln or ".exec(" in ln and "LicenseDialog" in "".join(lines[max(0,i-3):i]):
        print(f"{i:5} | {ln}")
