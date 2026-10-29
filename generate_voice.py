"""
Generador manual de huella vocal (.safetensors)
Uso: python generate_voice.py <ruta_wav> <nombre_salida>
Ejemplo: python generate_voice.py "C:\mi_voz.wav" Alfredo
"""
import sys
from pathlib import Path

def generate_voice(wav_path: str, name: str):
    wav = Path(wav_path)
    if not wav.exists():
        print(f"❌ No existe: {wav_path}")
        sys.exit(1)
    
    print(f"🎤 Extrayendo huella vocal de: {wav.name}")
    from core.pocket_cloner import cloner_instance
    
    out = cloner_instance.save_voice_state(str(wav), name)
    print(f"✅ Huella guardada: {out}")
    
    # Verificar
    voices = cloner_instance.list_saved_voices()
    print(f"📋 Voces disponibles: {voices}")
    if name in voices:
        print(f" '{name}' listo para usarse en Voces → Premium")
    else:
        print(f"⚠️  '{name}' no apareció en la lista")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python generate_voice.py <ruta_wav> <nombre>")
        print("Ejemplo: python generate_voice.py mi_voz.wav Alfredo")
        sys.exit(1)
    generate_voice(sys.argv[1], sys.argv[2])
