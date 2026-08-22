import winreg
from pathlib import Path

p = Path("installer/NaturalVoiceTTS.iss")
t = p.read_text(encoding="utf-8", errors="ignore")
if "sapi_adapter" in t:
    print("ISS ya parcheado"); raise SystemExit

DEV = r"C:\Program Files (x86)\Temp"

# --- cosechar config del adapter desde sus CLSIDs ---
clsids = []
base = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"CLSID")
i = 0
while True:
    try:
        sub = winreg.EnumKey(base, i)
    except OSError:
        break
    i += 1
    if sub.startswith("{") and sub.endswith("}"):
        try:
            k = winreg.OpenKey(base, sub + r"\InProcServer32")
            val = winreg.QueryValueEx(k, None)[0]
            winreg.CloseKey(k)
            if DEV.lower() in val.lower():
                clsids.append(sub)
        except OSError:
            pass
winreg.CloseKey(base)

reg_lines = []
for c in clsids:
    k = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, rf"CLSID\{c}")
    j = 0
    while True:
        try:
            nm, val, tp = winreg.EnumValue(k, j)
        except OSError:
            break
        j += 1
        if isinstance(val, str) and DEV.lower() in val.lower():
            continue
        vname = nm if nm else "(Default)"
        if tp == winreg.REG_SZ:
            reg_lines.append(f'Root: HKCR; Subkey: "CLSID\\{c}"; ValueType: string; ValueName: "{vname}"; ValueData: "{val}"; Flags: uninsdeletevalue')
        elif tp == winreg.REG_DWORD:
            reg_lines.append(f'Root: HKCR; Subkey: "CLSID\\{c}"; ValueType: dword; ValueName: "{vname}"; ValueData: "{val}"; Flags: uninsdeletevalue')
    winreg.CloseKey(k)
print("lineas registry config:", len(reg_lines))

add_files = 'Source: "sapi_adapter\\x64\\*"; DestDir: "{app}\\sapi\\x64"; Flags: ignoreversion recursesubdirs createallsubdirs\n'
add_run = 'Filename: "C:\\Windows\\Sysnative\\regsvr32.exe"; Parameters: "/s ""{app}\\sapi\\x64\\NaturalVoiceSAPIAdapter.dll"""; Flags: runhidden waituntilterminated\n'
add_unrun = 'Filename: "C:\\Windows\\Sysnative\\regsvr32.exe"; Parameters: "/u /s ""{app}\\sapi\\x64\\NaturalVoiceSAPIAdapter.dll"""; Flags: runhidden waituntilterminated\n'

i = t.find("[Files]")
j = t.find("\n", i) + 1
t = t[:j] + add_files + t[j:]

i = t.find("[Run]")
if i != -1:
    j = t.find("\n", i) + 1
    t = t[:j] + add_run + t[j:]
else:
    t += "\n[Run]\n" + add_run

if "[UninstallRun]" in t:
    i = t.find("[UninstallRun]")
    j = t.find("\n", i) + 1
    t = t[:j] + add_unrun + t[j:]
else:
    t += "\n[UninstallRun]\n" + add_unrun

if reg_lines:
    i = t.find("[Registry]")
    if i != -1:
        j = t.find("\n", i) + 1
        t = t[:j] + "\n".join(reg_lines) + "\n" + t[j:]
    else:
        t += "\n[Registry]\n" + "\n".join(reg_lines) + "\n"

p.write_text(t, encoding="utf-8")
print("ISS parcheado OK")
