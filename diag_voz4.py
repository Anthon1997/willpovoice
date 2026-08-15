import time
import pythoncom
import win32com.client
from adapters.naturalvoice_adapter import NaturalVoiceAdapter

pythoncom.CoInitialize()

def estados(sapi, n=8, label=""):
    vivo = False
    for i in range(n):
        st = sapi.Status
        print(f"{label} t={i * 0.4:.1f}s state={st.RunningState} pos={st.InputWordPosition}")
        if st.RunningState == 2:
            vivo = True
        time.sleep(0.4)
    print(f"{label} VERDICTO:", "ARRANCA" if vivo else "MUERTO (state nunca 2)")

VOZ = "Microsoft Elvira Online (Natural) - Spanish (Spain)"
TEX = "Prueba de narracion larga para ver si el motor arranca bien."

print("=== A: set_voice x2 + speak (sin preview) ===")
ad = NaturalVoiceAdapter()
ad.set_voice(VOZ)
ad.set_voice(VOZ)
ad.speak(TEX, asynchronous=True)
estados(ad.sapi, 8, "A")

print("\n=== B: preview con 2a instancia + purge + set_voice + speak ===")
ad2 = NaturalVoiceAdapter()
ad2.set_voice(VOZ)
prev = win32com.client.Dispatch("SAPI.SpVoice")
prev.Voice = ad2.sapi.Voice
prev.Speak("Hola esta es mi voz", 1)
time.sleep(3)
prev.Speak("", 2)
ad2.set_voice(VOZ)
ad2.speak(TEX, asynchronous=True)
estados(ad2.sapi, 8, "B")

print("\n=== C: preview con 2a instancia + purge + speak SIN 2o set_voice ===")
ad3 = NaturalVoiceAdapter()
ad3.set_voice(VOZ)
prev3 = win32com.client.Dispatch("SAPI.SpVoice")
prev3.Voice = ad3.sapi.Voice
prev3.Speak("Hola esta es mi voz", 1)
time.sleep(3)
prev3.Speak("", 2)
ad3.speak(TEX, asynchronous=True)
estados(ad3.sapi, 8, "C")

print("\nFIN")
input("Enter para cerrar...")
