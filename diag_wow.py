import winreg
branches = [
    r"SOFTWARE\WOW6432Node\Microsoft\Speech\Voices\Tokens",
    r"SOFTWARE\WOW6432Node\Microsoft\Speech_OneCore\Voices\Tokens",
]
for br in branches:
    try:
        tk = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, br)
    except OSError:
        print(br, "-> no existe")
        continue
    names, i = [], 0
    while True:
        try:
            names.append(winreg.EnumKey(tk, i))
        except OSError:
            break
        i += 1
    print(f"{br} -> {len(names)} tokens")
    for nm in names[:5]:
        print("  ", nm)
    winreg.CloseKey(tk)
