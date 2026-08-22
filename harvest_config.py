import winreg
for hive_name, hive in [("HKCU", winreg.HKEY_CURRENT_USER), ("HKLM", winreg.HKEY_LOCAL_MACHINE)]:
    for base in [r"SOFTWARE\NaturalVoiceSAPIAdapter",
                 r"SOFTWARE\WOW6432Node\NaturalVoiceSAPIAdapter"]:
        try:
            k = winreg.OpenKey(hive, base)
        except OSError:
            continue
        print(f"[{hive_name}\\{base}]")
        i = 0
        while True:
            try:
                nm, val, tp = winreg.EnumValue(k, i)
            except OSError:
                break
            i += 1
            print(f"  {nm} (tipo {tp}) = {val}")
        winreg.CloseKey(k)
print("fin")
