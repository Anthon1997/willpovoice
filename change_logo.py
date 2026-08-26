from pathlib import Path
import shutil
import re
import sys

root = Path(".")
new = None
for cand in ["assets/logo_new.png", "assets/logo_new.jpg",
             "assets/logo_new.jpeg", "assets/nuevo_logo.png"]:
    p = root / cand
    if p.exists():
        new = p
        break
if new is None:
    print("ERROR: guarda tu nueva foto como assets\\logo_new.png")
    sys.exit(1)

targets = set()

# A) Archivos de logo existentes en assets
for f in root.glob("assets/**/*"):
    if not f.is_file():
        continue
    b = f.name.lower()
    if b.startswith("logo_new"):
        continue
    if f.suffix.lower() not in (".png", ".ico", ".jpg", ".jpeg"):
        continue
    if ("logo" in b or "icono" in b or
            b in ("icon.ico", "icon.png", "app.ico", "app.png",
                  "app_icon.png", "icono.png", "willpo.png")):
        targets.add(f)

# B) Logos referenciados en el codigo (ui/*.py y *.spec)
for src in list(root.glob("ui/*.py")) + list(root.glob("*.spec")):
    t = src.read_text(encoding="utf-8", errors="ignore")
    for m in re.finditer(r'assets[/\\][A-Za-z0-9_\-./\\]+?\.(?:png|ico|jpg)', t):
        rel = m.group(0).replace("\\", "/")
        base = rel.split("/")[-1].lower()
        if ("logo" in base or "icono" in base or
                base in ("icon.ico", "icon.png", "app.ico", "app.png")):
            p = root / rel.replace("/", "\\")
            if p.exists():
                targets.add(p)

if not targets:
    tgt = root / "assets" / "icons" / "logo.png"
    tgt.parent.mkdir(parents=True, exist_ok=True)
    targets = {tgt}
    print("sin logos previos: creo assets/icons/logo.png como estandar")

for tgt in sorted(targets):
    if tgt.suffix.lower() == ".ico":
        try:
            from PIL import Image
            im = Image.open(new)
            im.save(tgt, sizes=[(16, 16), (32, 32), (48, 48), (256, 256)])
            print("ico convertido :", tgt)
            continue
        except Exception:
            pass
    shutil.copy2(new, tgt)
    print("logo reemplazado:", tgt)

print("LISTO: el logo nuevo ya vive en todos los puntos del app")
