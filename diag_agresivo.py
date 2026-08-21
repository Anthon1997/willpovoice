import winreg

# 1) Buscar CLSIDs con NaturalVoice
print("=== CLSIDs con NaturalVoice ===")
base = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"CLSID")
found = 0
i = 0
while True:
    try:
        sub = winreg.EnumKey(base, i)
    except OSError:
        break
    i += 1
    if not (sub.startswith("{") and sub.endswith("}")):
        continue
    try:
        k = winreg.OpenKey(base, sub + r"\InProcServer32")
        val = winreg.QueryValueEx(k, None)[0]
        winreg.CloseKey(k)
        if "naturalvoice" in val.lower():
            print(f"  {sub} -> {val}")
            found += 1
    except OSError:
        continue
winreg.CloseKey(base)
print(f"Total CLSIDs: {found}\n")

# 2) Buscar TODOS los tokens (sin filtro)
print("=== TODOS los tokens SAPI ===")
for hive_name, hk in [("HKLM", winreg.HKEY_LOCAL_MACHINE), ("HKCU", winreg.HKEY_CURRENT_USER)]:
    for br in [r"SOFTWARE\Microsoft\Speech\Voices\Tokens",
               r"SOFTWARE\Microsoft\Speech_OneCore\Voices\Tokens",
               r"SOFTWARE\WOW6432Node\Microsoft\Speech\Voices\Tokens",
               r"SOFTWARE\WOW6432Node\Microsoft\Speech_OneCore\Voices\Tokens"]:
        try:
            tk = winreg.OpenKey(hk, br)
        except OSError:
            continue
        names, j = [], 0
        while True:
            try:
                names.append(winreg.EnumKey(tk, j))
            except OSError:
                break
            j += 1
        if names:
            print(f"{hive_name} {br}: {len(names)} tokens")
            # Mostrar 2 tokens de ejemplo
            for nm in names[:2]:
                print(f"  - {nm}")
        winreg.CloseKey(tk)
