import shutil
from pathlib import Path
from core import license_manager as lm

d = Path.home() / ".willpovoice"
bak = Path.home() / ".willpovoice_bak_clean"

print("carpeta de licencia:", d, "existe:", d.exists())
if d.exists():
    print("contenido actual:")
    for f in sorted(d.iterdir()):
        print("   ", f.name, f.stat().st_size, "bytes")
    if bak.exists():
        shutil.rmtree(bak)
    d.rename(bak)
    print("\nRESPALDADA y eliminada ->", bak)
else:
    print("no habia nada que eliminar")

print("\nestado nuevo (instalacion limpia):", lm.check_status())
print("machine_id:", lm.get_machine_id())
