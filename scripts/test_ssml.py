import pythoncom
import win32com.client

pythoncom.CoInitialize()
sapi = win32com.client.Dispatch("SAPI.SpVoice")

for token in sapi.GetVoices():
    desc = token.GetDescription()
    if "Multilingual" in desc or "Natural" in desc:
        sapi.Voice = token
        print("Voz de prueba:", desc)
        break

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
    "Y de vuelta al espanol.</speak>"
)

print("\nFin de los tests.")
input("Pulsa Enter para cerrar...")
