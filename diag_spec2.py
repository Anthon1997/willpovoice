from pathlib import Path
spec = Path("WillpoVoice.spec").read_text(encoding="utf-8")
print("=== datas del .spec ===")
for i, ln in enumerate(spec.splitlines(), 1):
    if "datas" in ln or "assets" in ln.lower():
        print(f"{i}: {ln.strip()}")
print("\nSVG mencionado:", "svg" in spec)
