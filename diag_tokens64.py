import winreg
for br in (r"SOFTWARE\Microsoft\Speech\Voices\Tokens",
           r"SOFTWARE\Microsoft\Speech_OneCore\Voices\Tokens"):
    try:
        tk = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, br)
    except OSError:
        print(br, "-> no existe"); continue
    n, i = 0, 0
    while True:
        try:
            winreg.EnumKey(tk, i)
        except OSError:
            break
        i += 1; n += 1
    print(f"{br} -> {n} tokens")
    winreg.CloseKey(tk)
