from pathlib import Path
import re

# 1) Leer version actual de app/version.py
import sys
sys.path.insert(0, ".")
from app.version import APP_VERSION
print(f"APP_VERSION actual: {APP_VERSION}")

# 2) Verificar contenido del .iss
iss = Path("installer/NaturalVoiceTTS.iss")
content = iss.read_text(encoding="utf-8")

print("\n=== Versiones en el .iss ===")
for line in content.split("\n"):
    if "MyAppVersion" in line or "OutputBaseFilename" in line:
        print(line.strip())

# 3) Actualizar a la version correcta si es necesario
if APP_VERSION not in content:
    print(f"\nACTUALIZANDO .iss a version {APP_VERSION}...")
    content = re.sub(
        r'(MyAppVersion\s*=\s*")[^"]+(")',
        rf'\g<1>{APP_VERSION}\g<2>',
        content
    )
    content = re.sub(
        r'(OutputBaseFilename\s*=\s*WillpoVoice-Setup-)\d+\.\d+\.\d+',
        rf'\g<1>{APP_VERSION}',
        content
    )
    iss.write_text(content, encoding="utf-8")
    print("✓ .iss actualizado")
else:
    print(f"\n✓ .iss ya tiene version {APP_VERSION}")

# 4) Verificar que no haya redist
if "redist" in content.lower():
    print("\n⚠ ADVERTENCIA: el .iss contiene referencias a 'redist'")
    print("Esto puede causar que el instalador pese >130 MB")
