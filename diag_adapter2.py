from pathlib import Path
import os

appdata = Path(os.environ["LOCALAPPDATA"]) / "NaturalVoiceSAPIAdapter"
print(f"=== Contenido de {appdata} ===")
if appdata.exists():
    for item in sorted(appdata.rglob("*"))[:80]:
        if item.is_file():
            size = item.stat().st_size
            print(f"  {str(item.relative_to(appdata)):60s} {size:>10,} bytes")
        else:
            print(f"  {str(item.relative_to(appdata))}/")
else:
    print("  Carpeta no existe")

print("\n=== Ejecutables del adaptador ===")
exes = list(appdata.rglob("*.exe")) if appdata.exists() else []
for exe in exes[:10]:
    print(f"  {exe}")

print("\n=== Scripts de registro (bat/cmd/ps1/vbs/reg) ===")
scripts = []
for ext in ("*.bat", "*.cmd", "*.ps1", "*.vbs", "*.reg"):
    scripts.extend(appdata.rglob(ext) if appdata.exists() else [])
for s in scripts[:10]:
    print(f"  {s}")

print("\n=== DLLs del adaptador ===")
dlls = list(appdata.rglob("*.dll")) if appdata.exists() else []
for d in dlls[:10]:
    print(f"  {d} ({d.stat().st_size:,} bytes)")
