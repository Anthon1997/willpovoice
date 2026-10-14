import shutil
from pathlib import Path
from core import license_manager as lm

d = Path.home() / ".willpovoice"          # licencia activa
off = Path.home() / ".willpovoice_OFF"    # backup temporal

if d.exists():
    if off.exists():
        shutil.rmtree(off)
    d.rename(off)
    print(">> LICENCIA DESACTIVADA (temporal)")
    print("   backup guardado en:", off)
    print("   estado limpio ahora:", lm.check_status())
elif off.exists():
    if d.exists():
        shutil.rmtree(d)      # borra el estado "limpio" generado
    off.rename(d)
    print(">> LICENCIA RESTAURADA")
    print("   estado:", lm.check_status())
    print("   detalles:", lm.license_details())
else:
    print(">> no habia licencia ni backup")
    print("   estado:", lm.check_status())
