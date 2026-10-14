from pathlib import Path
import re, sys
sys.path.insert(0, ".")
from app.version import APP_VERSION

iss = Path("installer/NaturalVoiceTTS.iss")
c = iss.read_text(encoding="utf-8")

# El define de Inno NO lleva signo igual:  #define MyAppVersion "x.y.z"
new, n = re.subn(r'(?m)^#define MyAppVersion "\d+\.\d+\.\d+"',
                 '#define MyAppVersion "' + APP_VERSION + '"', c)
print("sustituciones:", n)
if n == 1:
    iss.write_text(new, encoding="utf-8")
    print("OK: define ->", APP_VERSION)
else:
    print("REVISAR: defines encontrados:", n)

for i, l in enumerate(new.split("\n"), 1):
    if "MyAppVersion" in l or "OutputBaseFilename" in l:
        print(i, ":", l.strip())
