import sys
sys.path.insert(0, ".")

print("=== 1) PRUEBA DEL ENGINE (método correcto) ===")
from core.tts_engine import TTSEngine

eng = TTSEngine()
voices = eng.get_available_voices()
test_voice = next((v for v in voices if "Helena" in v), voices[0])
print(f"Voz: {test_voice}")

ok = eng.select_voice(test_voice)
print(f"select_voice: {ok}")

print("\n>>> Probando engine.speak() sincrónico...")
try:
    eng.speak("Prueba de audio desde el engine directamente.")
    print("✓ speak() ejecutado. ¿SE ESCUCHÓ? (S/N)")
except Exception as e:
    print(f"✗ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n=== 2) MÉTODOS DE PLAY/PREVIEW EN UI ===")
from pathlib import Path
import re

m = Path("ui/modern_window.py").read_text(encoding="utf-8")

# Buscar _player_play_clicked
match = re.search(r'def _player_play_clicked\(self.*?\n(?=\n    def |\nclass |\Z)', m, re.DOTALL)
if match:
    print("Método _player_play_clicked encontrado:")
    print(match.group(0)[:1500])

print("\n=== 3) BOTÓN PLAY EN LA UI ===")
# Buscar dónde se conecta el botón play
for i, line in enumerate(m.split('\n'), 1):
    if 'play' in line.lower() and 'connect' in line.lower():
        print(f"Línea {i}: {line.strip()}")

print("\n=== 4) MÉTODO speak_text ===")
match2 = re.search(r'def speak_text\(self.*?\n(?=\n    def |\nclass |\Z)', m, re.DOTALL)
if match2:
    print("Método speak_text encontrado:")
    print(match2.group(0)[:1500])
