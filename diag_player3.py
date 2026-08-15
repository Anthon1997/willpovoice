from pathlib import Path
import time

t = Path("ui/modern_window.py").read_text(encoding="utf-8")

print("=" * 70)
print("PARTE 1: CODIGO ACTUAL DEL REPRODUCTOR Y VOCES")
print("=" * 70)

for name in ("def speak_text", "def _tick_player", "def _player_play_clicked",
             "def _set_player_icon", "def _spin_tick", "def _draw_spin",
             "def _on_voice_changed", "def _voice_changed",
             "def _on_position_changed", "def _on_synth_ready"):
    i = t.find(name)
    if i != -1:
        j = t.find("\ndef ", i + 10)
        print(f"\n----- {name} -----")
        print(t[i:j if j != -1 else i + 1200])

print("\n----- conexiones voice_combo -----")
for ln in t.splitlines():
    if "voice_combo" in ln and ("connect" in ln or "IndexChanged" in ln):
        print(ln)

print("\n----- conexiones player -----")
for ln in t.splitlines():
    if ("player" in ln or "vol_slider" in ln or "progress_slider" in ln) and "connect" in ln:
        print(ln)

te = Path("core/tts_engine.py").read_text(encoding="utf-8")
for name in ("def select_voice",):
    i = te.find(name)
    if i != -1:
        j = te.find("\ndef ", i + 10)
        print(f"\n----- tts_engine {name} -----")
        print(te[i:j if j != -1 else i + 600])

import glob
ad = glob.glob("adapters/*.py")
print("\nadapters:", ad)
for f in ad:
    a = Path(f).read_text(encoding="utf-8")
    i = a.find("def set_voice")
    if i != -1:
        j = a.find("\ndef ", i + 10)
        print(f"\n----- {f} def set_voice -----")
        print(a[i:j if j != -1 else i + 900])

print("\n" + "=" * 70)
print("PARTE 2: SONDEO SAPI EN VIVO (valores reales)")
print("=" * 70)
import pythoncom
import win32com.client
pythoncom.CoInitialize()
sapi = win32com.client.Dispatch("SAPI.SpVoice")
print("Voz:", sapi.Voice.GetDescription())
sapi.Speak("Hola, probando la linea de tiempo con audio real.", 1)
for i in range(25):
    st = sapi.Status
    print(f"t={i * 0.3:.1f}s  RunningState={st.RunningState}  AudioPosition={st.AudioPosition}")
    time.sleep(0.3)

print("\n----- cambio de voz (simula el combo) -----")
try:
    for token in sapi.GetVoices():
        d = token.GetDescription()
        if "Brian" in d or "Ava" in d:
            print("Cambiando a:", d)
            sapi.Voice = token
            sapi.Speak("Prueba con voz multilingual.", 1)
            for i in range(10):
                st = sapi.Status
                print(f"t={i * 0.3:.1f}s  state={st.RunningState}  audio={st.AudioPosition}")
                time.sleep(0.3)
            break
except Exception as exc:
    print("ERROR al cambiar voz:", type(exc).__name__, exc)

print("\nFIN DEL DIAGNOSTICO")
input("Enter para cerrar...")
