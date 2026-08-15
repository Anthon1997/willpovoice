from pathlib import Path
import sys
sys.path.insert(0, ".")

# Cargar config y motor igual que la app
from app.config import load_settings
from core.tts_engine import TTSEngine

eng = TTSEngine()
eng.refresh_voices()
vo = eng.get_available_voices()
if vo:
    eng.select_voice(vo[0])

adapter = eng.adapter
print("=== adapter ===")
print("tipo:", type(adapter).__name__)
print("attrs relevantes:")
for a in dir(adapter):
    if not a.startswith("__"):
        print("  -", a)

if hasattr(adapter, "sapi"):
    s = adapter.sapi
    print("=== sapi ===")
    print("tipo:", type(s).__name__)
    for a in dir(s):
        if not a.startswith("_") and a[0].isupper():
            print("  -", a)
    print("tiene Pause:", hasattr(s, "Pause"))
    print("tiene Resume:", hasattr(s, "Resume"))
    print("tiene Speak:", hasattr(s, "Speak"))

# Probar pause/resume real
try:
    s.Speak("hola prueba", 1)
    print("hablando...")
    import time; time.sleep(1)
    s.Pause()
    print("pausado. Status:", s.Status.RunningState)
    time.sleep(1)
    s.Resume()
    print("reanudado. Status:", s.Status.RunningState)
except Exception as e:
    print("ERROR:", type(e).__name__, e)
