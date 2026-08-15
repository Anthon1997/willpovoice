import pythoncom
import win32com.client
import winreg

pythoncom.CoInitialize()
sapi = win32com.client.Dispatch("SAPI.SpVoice")
print("GetVoices() ve:", sapi.GetVoices().Count, "voces")

print("\n=== Tokens en el registro ===")
paths = [
    (winreg.HKEY_LOCAL_MACHINE, "HKLM", r"SOFTWARE\Microsoft\Speech\Voices\Tokens"),
    (winreg.HKEY_LOCAL_MACHINE, "HKLM", r"SOFTWARE\WOW6432Node\Microsoft\Speech\Voices\Tokens"),
    (winreg.HKEY_CURRENT_USER, "HKCU", r"SOFTWARE\Microsoft\Speech\Voices\Tokens"),
    (winreg.HKEY_CURRENT_USER, "HKCU", r"SOFTWARE\WOW6432Node\Microsoft\Speech\Voices\Tokens"),
]
for root, tag, sub in paths:
    try:
        k = winreg.OpenKey(root, sub)
        n = winreg.QueryInfoKey(k)[0]
        print(f"{n:4d} tokens  [{tag}] {sub}")
        for i in range(min(4, n)):
            print("      -", winreg.EnumKey(k, i))
    except FileNotFoundError:
        print(f"   0 tokens  [{tag}] {sub} (no existe)")

print("\n=== NaturalVoiceSAPIAdapter en registro ===")
for root, tag in [(winreg.HKEY_LOCAL_MACHINE, "HKLM"),
                  (winreg.HKEY_CURRENT_USER, "HKCU")]:
    for sub in (r"SOFTWARE\NaturalVoiceSAPIAdapter",
                r"SOFTWARE\WOW6432Node\NaturalVoiceSAPIAdapter"):
        try:
            k = winreg.OpenKey(root, sub)
            print(f"EXISTE [{tag}] {sub} con {winreg.QueryInfoKey(k)[1]} valores")
        except FileNotFoundError:
            pass

print("\n=== Carpetas del adaptador en disco ===")
from pathlib import Path
for p in [r"C:\Program Files\NaturalVoiceSAPIAdapter",
          r"C:\Program Files (x86)\NaturalVoiceSAPIAdapter",
          Path.home() / "NaturalVoiceSAPIAdapter",
          Path.home() / "AppData/Local/NaturalVoiceSAPIAdapter"]:
    print("  ", "OK  " if Path(p).exists() else "NO  ", p)
