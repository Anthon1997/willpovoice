import pythoncom
import win32com.client

pythoncom.CoInitialize()
sapi = win32com.client.Dispatch("SAPI.SpVoice")

# ---- Seleccion PRIORITARIA de voz premium espanola ----
voces = list(sapi.GetVoices())
elegida = None
prioridades = [
    lambda d: "seraphina" in d and "multilingual" in d,
    lambda d: "multilingual" in d and ("spanish" in d or "espan" in d),
    lambda d: "multilingual" in d,
    lambda d: ("natural" in d or "online" in d) and ("spanish" in d or "mexi" in d or "spain" in d),
    lambda d: "spanish" in d,
]
for prio in prioridades:
    for token in voces:
        d = token.GetDescription().lower()
        if prio(d):
            elegida = token
            break
    if elegida:
        break

if elegida is None:
    print("NO se encontro voz premium espanola. Disponibles:")
    for t in voces:
        print(" -", t.GetDescription())
    input("Enter para cerrar...")
    raise SystemExit(1)

sapi.Voice = elegida
print("VOZ DE PRUEBA:", elegida.GetDescription())

print("\nTEST 1: texto plano (el problema actual)")
sapi.Speak("Numero uno. Sale vacio. Numero dos.")

print("\nTEST 2: SSML base en espanol")
sapi.Speak(
    "<speak version='1.0' xml:lang='es-ES' "
    "xmlns='http://www.w3.org/2001/10/synthesis'>"
    "Numero uno. Sale vacio. Numero dos.</speak>"
)

print("\nTEST 3: SSML espanol + ingles marcado")
sapi.Speak(
    "<speak version='1.0' xml:lang='es-ES' "
    "xmlns='http://www.w3.org/2001/10/synthesis'>"
    "Sale vacio. Y ahora en ingles: "
    "<lang xml:lang='en-US'>Hello my friend, see you tomorrow.</lang> "
    "Y de vuelta al espanol con el numero ciento veintitres.</speak>"
)

print("\nFin de los tests.")
input("Pulsa Enter para cerrar...")
