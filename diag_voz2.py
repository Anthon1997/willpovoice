from pathlib import Path

t = Path("ui/modern_window.py").read_text(encoding="utf-8")

print("=" * 70)
print("1. COMO SE LLENA EL COMBO (tipo de dato en UserRole)")
print("=" * 70)
i = t.find("_display_voice_name")
if i != -1:
    j = t.find("\ndef ", i + 10)
    print(t[i:j if j != -1 else i + 800])
for ln in t.splitlines():
    if "voice_combo.addItem" in ln or "setItemData" in ln or "_load_voices" in ln or "list_voices" in ln:
        print("LIN:", ln.strip())

print("\n" + "=" * 70)
print("2. SIMULACION EXACTA DEL FLUJO speak_text")
print("=" * 70)
from adapters.naturalvoice_adapter import NaturalVoiceAdapter
ad = NaturalVoiceAdapter()
voces = ad.list_voices()
v = voces[0]
print("tipo de v:", type(v).__name__)
if isinstance(v, dict):
    print("claves de v:", list(v.keys()))
else:
    print("valor de v:", repr(v)[:200])

print("\n--- paso A: stop ---")
try:
    ad.stop()
    print("stop OK")
except Exception as e:
    print("stop FALLO:", type(e).__name__, e)

print("\n--- paso B: asignar v COMPLETO (lo que hace el parche hoy) ---")
try:
    ad.sapi.Voice = v
    print("v completo OK:", ad.sapi.Voice.GetDescription())
except Exception as e:
    print("v completo FALLO:", type(e).__name__, str(e)[:120])

if isinstance(v, dict) and "token" in v:
    print("\n--- paso C: asignar v['token'] ---")
    try:
        ad.sapi.Voice = v["token"]
        print("token OK:", ad.sapi.Voice.GetDescription())
    except Exception as e:
        print("token FALLO:", type(e).__name__, str(e)[:120])

print("\n--- paso D: speak async + estados ---")
try:
    ad.speak("Prueba de narracion con la voz recien asignada.", asynchronous=True)
    import time
    for i in range(12):
        st = ad.sapi.Status
        print(f"t={i * 0.3:.1f}s state={st.RunningState} pos={st.InputWordPosition}")
        time.sleep(0.3)
except Exception as e:
    print("speak FALLO:", type(e).__name__, str(e)[:200])

print("\nFIN")
input("Enter para cerrar...")
