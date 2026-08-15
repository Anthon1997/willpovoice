from pathlib import Path

t = Path("ui/main_window.py").read_text(encoding="utf-8")
lines = t.split("\n")

print("=== LicenseDialog (490-590) ===")
print("\n".join(f"{i+1:5} | {ln}" for i, ln in enumerate(lines[489:590])))

r = Path("run.py").read_text(encoding="utf-8")
print("=== run.py completo ===")
print(r)
