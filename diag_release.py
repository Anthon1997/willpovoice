from pathlib import Path
import re

t = Path("ui/modern_window.py").read_text(encoding="utf-8")

print("=== 1. ASSETS REFERENCIADOS (banner/portada) ===")
assets = sorted(set(re.findall(r"assets[/\'\"\\][A-Za-z0-9_/\-\\. ]+\.(?:png|jpg|jpeg|gif|mp4|ico)", t)))
for m in assets:
    print("  ", m)

print("\n=== 2. Lineas con banner/portada/cover ===")
for i, ln in enumerate(t.splitlines(), 1):
    low = ln.lower()
    if any(k in low for k in ("banner", "portada", "cover", "hero")):
        print(f"{i}: {ln.strip()[:110]}")

print("\n=== 3. Tamano actual de las imagenes ===")
try:
    from PySide6.QtGui import QImage
    seen = set()
    for c in assets:
        p = Path(c.replace("\\", "/"))
        if p in seen or not p.exists():
            continue
        seen.add(p)
        img = QImage(str(p))
        if not img.isNull():
            print(f"  {p}: {img.width()}x{img.height()}")
except Exception as e:
    print("  no se pudo leer:", e)

print("\n=== 4. Donde aparece la version 1.2.1 ===")
for f in ["ui/modern_window.py", "ui/main_window.py", "installer.iss",
          "run.py", "core/tts_engine.py", "WillpoVoice.spec"]:
    p = Path(f)
    if p.exists():
        for i, ln in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if "1.2.1" in ln:
                print(f"  {f}:{i}: {ln.strip()[:100]}")

print("\n=== 5. Codigo del update checker (version.json) ===")
i = t.find("version.json")
if i != -1:
    start = t.rfind("\ndef ", 0, i)
    print(t[start if start != -1 else max(0, i - 800): i + 1800])
else:
    print("  version.json NO encontrado en modern_window")
