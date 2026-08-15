from pathlib import Path
import os

appdata = Path(os.environ["LOCALAPPDATA"]) / "NaturalVoiceSAPIAdapter"
print(f"=== Contenido de {appdata} ===")
if appdata.exists():
    for item in sorted(appdata.rglob("*"))[:50]:
        if item.is_file():
            size = item.stat().st_size
            print(f"  {item.relative_to(appdata):60s} {size:>10,} bytes")
        else:
            print(f"  {item.relative_to(appdata)}/")
else:
    print("  Carpeta no existe")

print("\n=== Buscando ejecutables del adaptador ===")
exes = list(appdata.rglob("*.exe")) if appdata.exists() else []
for exe in exes[:10]:
    print(f"  {exe}")

print("\n=== Buscando scripts de registro ===")
scripts = []
for ext in ("*.bat", "*.cmd", "*.ps1", "*.vbs"):
    scripts.extend(appdata.rglob(ext) if appdata.exists() else [])
for s in scripts[:10]:
    print(f"  {s}")
