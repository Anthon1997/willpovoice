import pythoncom
import win32com.client

pythoncom.CoInitialize()
sapi = win32com.client.Dispatch("SAPI.SpVoice")

texto = (
    "Numero uno. Sale vacio. Numero dos. "
    "Hello my friend, see you tomorrow. "
    "Ciento veintitres."
)

voces = list(sapi.GetVoices())
objetivos = ["alonso", "dalia", "elvira", "seraphina"]

for obj in objetivos:
    for token in voces:
        d = token.GetDescription()
        if obj in d.lower():
            sapi.Voice = token
            print("\n=== VOZ A PRUEBA:", d, "===")
            sapi.Speak(texto)
            break
    else:
        print(f"\n=== {obj}: no encontrada en el sistema ===")

print("\nFin de la comparativa.")
input("Pulsa Enter para cerrar...")
