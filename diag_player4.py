from pathlib import Path
import time

t = Path("ui/modern_window.py").read_text(encoding="utf-8")

print("=" * 70)
print("PARTE 1: HANDLER DE CAMBIO DE VOZ")
print("=" * 70)

for name in ("def _on_combo_voice", "def _voice_changed",
             "def _combo_voice", "def _on_voice_changed"):
    i = t.find(name)
    if i != -1:
        j = t.find("\ndef ", i + 10)
        print(f"\n----- {name} -----")
        print(t[i:j if j != -1 else i + 1200])

print("\n" + "=" * 70)
print("PARTE 2: TODAS LAS PROPIEDADES DE SAPI.Status (reales)")
print("=" * 70)
import pythoncom
import win32com.client
pythoncom.CoInitialize()
sapi = win32com.client.Dispatch("SAPI.SpVoice")

print("\nVoz por defecto:", sapi.Voice.GetDescription())
print("Propiedades de sapi:", [p for p in dir(sapi) if not p.startswith("_")])

sapi.Speak("Hola probando", 1)
time.sleep(0.5)
st = sapi.Status
print("\nPropiedades de sapi.Status:", [p for p in dir(st) if not p.startswith("_")])

print("\nValores REALES de RunningState durante sintesis:")
try:
    sapi.Speak("Texto de prueba mas largo para capturar estados.", 1)
    for i in range(20):
        st = sapi.Status
        line = f"t={i * 0.2:.1f}s  RunningState={st.RunningState}"
        # Intentar cada propiedad conocida
        for prop in ("AudioPosition", "InputWordLength", "InputWordPosition",
                     "LastResult", "LastBookmark", "LastStreamNumber",
                     "PhonemeId", "SentenceLength", "SentencePosition",
                     "StreamNumber", "StreamPosition", "VisemeId"):
            try:
                v = getattr(st, prop)
                line += f"  {prop}={v}"
            except Exception:
                pass
        print(line)
        time.sleep(0.2)
except Exception as e:
    print("ERROR en sondeo:", e)

print("\n----- Pausa/Resume -----")
try:
    sapi.Speak("Texto pausable muy largo para probar pausas.", 1)
    time.sleep(1)
    sapi.Pause()
    print("Pause OK, RunningState =", sapi.Status.RunningState)
    time.sleep(1)
    sapi.Resume()
    print("Resume OK, RunningState =", sapi.Status.RunningState)
    time.sleep(2)
except Exception as e:
    print("ERROR Pausa/Resume:", e)

print("\n----- Cambio de voz a una Multilingual -----")
try:
    for token in sapi.GetVoices():
        d = token.GetDescription()
        if "Multilingual" in d:
            print("Cambiando a:", d)
            sapi.Voice = token
            sapi.Speak("Prueba con voz multilingual real.")
            print("Sintesis con Multilingual OK")
            break
    else:
        print("No se encontro voz Multilingual")
except Exception as e:
    print("ERROR al cambiar voz:", type(e).__name__, e)

print("\nFIN DEL DIAGNOSTICO")
input("Enter para cerrar...")
