from pathlib import Path
import glob

t = Path("ui/modern_window.py").read_text(encoding="utf-8")

print("=" * 70)
print("1. ESTADO ACTUAL: cambio de voz, play, speak")
print("=" * 70)
for name in ("def _on_combo_voice", "def _player_play_clicked",
             "def speak_text"):
    i = t.find(name)
    if i != -1:
        j = t.find("\ndef ", i + 10)
        print(f"\n----- {name} -----")
        print(t[i:j if j != -1 else i + 1500])

print("\n----- que guarda el combo en UserRole -----")
for ln in t.splitlines():
    if "addItem" in ln or "UserRole" in ln and "combo" in ln:
        print(ln.strip())

print("\n" + "=" * 70)
print("2. MATCHER DE VOCES (codigo real)")
print("=" * 70)
for f in glob.glob("core/*.py") + glob.glob("adapters/*.py"):
    a = Path(f).read_text(encoding="utf-8")
    for fn in ("def _get_voice_token", "def select_voice"):
        i = a.find(fn)
        if i != -1:
            j = a.find("\ndef ", i + 10)
            print(f"\n----- {f} {fn} -----")
            print(a[i:j if j != -1 else i + 1200])

print("\n" + "=" * 70)
print("3. PRUEBA EN VIVO: nombres del combo vs SAPI")
print("=" * 70)
from adapters.naturalvoice_adapter import NaturalVoiceAdapter
ad = NaturalVoiceAdapter()
pruebas = ["Ava (Multilingual)", "Brian (Multilingual)",
           "Dalia - Spanish (Mexico)", "Elvira - Spanish (Spain)",
           "Seraphina (Multilingual)", "Alonso - Spanish (United States)"]
for q in pruebas:
    try:
        ok = ad.set_voice(q)
        print(f"OK   {q!r} -> {ad.sapi.Voice.GetDescription()}")
    except Exception as e:
        print(f"FALLO {q!r} -> {type(e).__name__}: {e}")

print("\nFIN")
input("Enter para cerrar...")
