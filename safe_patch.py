"""safe_patch.py - reemplazos con verificacion y rollback."""
import ast
import shutil
import subprocess
import sys
from pathlib import Path


def apply(path, replacements):
    """replacements = lista de (viejo, nuevo). Aborta si un ancla
    no aparece exactamente 1 vez. Rollback automatico si algo falla."""
    p = Path(path)
    bak = p.with_suffix(p.suffix + ".bak")
    shutil.copy2(p, bak)
    t = p.read_text(encoding="utf-8")

    for old, new in replacements:
        n = t.count(old)
        if n != 1:
            print(f"ABORT: ancla aparece {n} veces (debe ser 1):")
            print("   ", old[:70].replace("\n", " | "))
            return False
        t = t.replace(old, new, 1)

    try:
        ast.parse(t)
    except SyntaxError as exc:
        print(f"ABORT sintaxis: {exc}")
        return False

    p.write_text(t, encoding="utf-8", newline="\n")

    r = subprocess.run(
        [sys.executable, "-c",
         f"from {p.parent.name}.{p.stem} import MainWindow"],
        capture_output=True, text=True, cwd=str(p.parents[1]))
    if r.returncode != 0:
        print("ABORT import (rollback aplicado):")
        print(r.stderr.strip().splitlines()[-1] if r.stderr else "")
        shutil.copy2(bak, p)
        return False

    print("OK: aplicado + parse + import")
    return True
