import re, sys
from pathlib import Path

# ---- 1) bump de version 1.3.0 -> 1.3.1 ----
vp = Path("app/version.py")
t = vp.read_text(encoding="utf-8")
old = 'APP_VERSION = "1.3.0"'
new = 'APP_VERSION = "1.3.1"'
if t.count(old) == 1:
    vp.write_text(t.replace(old, new, 1), encoding="utf-8", newline="\n")
    print("OK: version -> 1.3.1")
else:
    print("SALTADO version count=", t.count(old))

sys.path.insert(0, ".")
from app.version import APP_VERSION
print("APP_VERSION ahora:", APP_VERSION)

# ---- 2) clean_iss.py (regla anti-redist de la guia) ----
p = Path("installer/NaturalVoiceTTS.iss")
lines = p.read_text(encoding="utf-8", errors="ignore").split("\n")
out, removed = [], 0
for l in lines:
    low = l.lower()
    if "redist" in low:
        removed += 1
        continue
    if low.strip().startswith("source") and "readme" in low:
        removed += 1
        continue
    out.append(l)
t = "\n".join(out)
t, n1 = re.subn(r'(MyAppVersion\s*=\s*")\d+\.\d+\.\d+(")',
                rf"\g<1>{APP_VERSION}\g<2>", t)
t, n2 = re.subn(r'(OutputBaseFilename\s*=\s*WillpoVoice-Setup-)\d+\.\d+\.\d+',
                rf"\g<1>{APP_VERSION}", t)
p.write_text(t, encoding="utf-8")
print("lineas redist/readme eliminadas:", removed)
print("version sync en .iss:", n1, n2)
for l in t.split("\n"):
    if any(k in l for k in ("MyAppVersion", "OutputBaseFilename",
                            "redist", "README")):
        print("   ", l.strip()[:110])
