from core import license_manager as lm
import shutil

p = lm.DATA_FILE
print("archivo:", p)
print("existe:", p.exists())

if p.exists():
    bak = p.with_name(p.name + ".bak")
    shutil.copy2(p, bak)
    print("backup creado en:", bak)
    p.unlink()
    print("licencia eliminada de esta maquina")
else:
    print("no habia licencia guardada")

print("machine_id:", lm.get_machine_id())
print("estado nuevo:", lm.check_status())
