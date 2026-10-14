from pathlib import Path
import re

iss = Path("installer/NaturalVoiceTTS.iss")
content = iss.read_text(encoding="utf-8")
lines = content.split("\n")

print("=== Líneas con MyAppVersion y OutputBaseFilename ===")
for i, line in enumerate(lines, 1):
    if "MyAppVersion" in line or "OutputBaseFilename" in line:
        print(f"{i}: {line}")

import sys
sys.path.insert(0, ".")
from app.version import APP_VERSION
print(f"\nAPP_VERSION actual = {APP_VERSION}")

# Corregir si no coincide
if APP_VERSION not in content:
    print(f"\nACTUALIZANDO .iss a {APP_VERSION}...")
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
    print(f"\n✓ .iss ya tiene versión {APP_VERSION}")

# Verificar de nuevo
content2 = iss.read_text(encoding="utf-8")
for i, line in enumerate(content2.split("\n"), 1):
    if "MyAppVersion" in line or "OutputBaseFilename" in line:
        print(f"{i}: {line}")
