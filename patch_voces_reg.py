import winreg
import pythoncom
import win32com.client

# 1. Escribir los flags en el registro (sin regedit manual)
path = r"SOFTWARE\NaturalVoiceSAPIAdapter\Enumerator"
key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, path)
values = {
    "EdgeVoiceAllLanguages": 1,
    "EdgeVoiceAllMultilingual": 1,
    "NoEdgeVoices": 0,
    "NoNarratorVoices": 0,
    "NoAzureVoices": 1,
}
for name, val in values.items():
    winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, val)
winreg.CloseKey(key)
print("1. Registro escrito.")

# 2. Verificar lectura
key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path)
for name in values:
    v, _ = winreg.QueryValueEx(key, name)
    print(f"   {name} = {v}")
winreg.CloseKey(key)

# 3. Comprobar si el adaptador expone las voces nuevas
pythoncom.CoInitialize()
sapi = win32com.client.Dispatch("SAPI.SpVoice")
voices = sapi.GetVoices()
found = []
for i in range(voices.Count):
    desc = voices.Item(i).GetDescription()
    low = desc.lower()
    if any(k in low for k in ("elvira", "dalia", "alonso")):
        found.append(desc)
print("2. Voces espanol/mexico detectadas por SAPI:")
if found:
    for f in found:
        print("   ✓", f)
else:
    print("   (ninguna aun - ver nota abajo)")
pythoncom.CoUninitialize()
