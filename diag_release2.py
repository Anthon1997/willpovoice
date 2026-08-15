from pathlib import Path

t = Path("ui/modern_window.py").read_text(encoding="utf-8")

print("=== 1. Bloque de la portada (lineas 855-905) ===")
lines = t.splitlines()
for i in range(854, min(905, len(lines))):
    print(f"{i+1}: {lines[i]}")

print("\n=== 2. portada.png: tamano y frames ===")
try:
    from PySide6.QtGui import QImage
    p = Path("assets/icons/portada.png")
    if p.exists():
        img = QImage(str(p))
        print(f"  portada.png: {img.width()}x{img.height()}")
    else:
        print("  portada.png NO EXISTE")
    fr = Path("assets/icons/portada_frames")
    if fr.exists():
        n = len(list(fr.glob("*.png")))
        print(f"  portada_frames: {n} frames")
        first = sorted(fr.glob("*.png"))[:1]
        if first:
            img = QImage(str(first[0]))
            print(f"  frame[0]: {img.width()}x{img.height()}")
except Exception as e:
    print("  error:", e)

print("\n=== 3. Rastros de actualizador en modern y main ===")
for f in ["ui/modern_window.py", "ui/main_window.py"]:
    a = Path(f).read_text(encoding="utf-8")
    hits = []
    for i, ln in enumerate(a.splitlines(), 1):
        low = ln.lower()
        if any(k in low for k in ("updateworker", "downloadworker",
                                  "willpotech", "actualiz", "version.json")):
            hits.append(f"{i}: {ln.strip()[:110]}")
    print(f"\n--- {f}: {len(hits)} coincidencias ---")
    for h in hits[:25]:
        print(" ", h)
