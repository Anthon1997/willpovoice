from pathlib import Path
import time

print("=" * 70)
print("PARTE 1: ESTADO ACTUAL DEL CODIGO (sin suposiciones)")
print("=" * 70)
t = Path("ui/modern_window.py").read_text(encoding="utf-8")
for name in ("def _player_play_clicked", "def _tick_player", "def speak_text"):
    i = t.find(name)
    j = t.find("\ndef ", i + 10)
    print(f"\n----- {name} -----")
    print(t[i:j if j != -1 else i + 1600])

print("\n" + "=" * 70)
print("PARTE 2: SONDEO Pause/Resume en voz ONLINE (Multilingual)")
print("=" * 70)
import pythoncom
import win32com.client
pythoncom.CoInitialize()
sapi = win32com.client.Dispatch("SAPI.SpVoice")
for token in sapi.GetVoices():
    d = token.GetDescription()
    if "Multilingual" in d:
        sapi.Voice = token
        print("Voz de prueba:", d)
        break

texto = ("Este es un texto de prueba bastante largo para medir la pausa "
         "y la reanudacion de la sintesis de voz en linea con voces "
         "multilingues del adaptador natural voice.")

t0 = time.time()
sapi.Speak(texto, 1)
print(f"Speak async lanzado en {time.time()-t0:.2f}s")
time.sleep(4)
st = sapi.Status
print(f"t=4s  state={st.RunningState}  pos={st.InputWordPosition}")

t0 = time.time()
sapi.Pause()
dt = time.time() - t0
st = sapi.Status
print(f"PAUSE  tardo {dt:.2f}s  state={st.RunningState}  pos={st.InputWordPosition}")
pos_paused = st.InputWordPosition
time.sleep(2)

t0 = time.time()
sapi.Resume()
dt = time.time() - t0
st = sapi.Status
print(f"RESUME tardo {dt:.2f}s  state={st.RunningState}  pos={st.InputWordPosition}")
time.sleep(3)
st = sapi.Status
print(f"t+3s tras resume  state={st.RunningState}  pos={st.InputWordPosition}")
print("VERDICTO pos:", "CONTINUA (resume real)" if st.InputWordPosition > pos_paused else "SE REINICIO o NO AVANZA")

for i in range(40):
    time.sleep(0.5)
    st = sapi.Status
    if st.RunningState != 2:
        print(f"termino a los ~{i * 0.5:.0f}s tras resume, state={st.RunningState}")
        break

print("\nFIN DEL SONDEO")
input("Enter para cerrar...")
