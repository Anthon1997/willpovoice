from pathlib import Path
sc = Path(".venv/Lib/site-packages/sitecustomize.py")
if sc.exists():
    print("✓ sitecustomize.py existe")
    print("Contenido:")
    print(sc.read_text(encoding="utf-8"))
else:
    print("✗ sitecustomize.py NO EXISTE - CRÍTICO")
