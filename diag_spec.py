from pathlib import Path

spec = Path("WillpoVoice.spec").read_text(encoding="utf-8")

print("=== Lineas con assets en el .spec ===")
for i, ln in enumerate(spec.splitlines(), 1):
    if "assets" in ln.lower() or "datas" in ln.lower():
        print(f"{i}: {ln}")
