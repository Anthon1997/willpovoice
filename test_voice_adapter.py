import sys
sys.path.insert(0, ".")

print("=== PRUEBA DIRECTA DE CARGA DE VOCES ===")
try:
    from adapters.sapi_adapter import SAPIAdapter
    adapter = SAPIAdapter()
    voices = adapter.list_voices()
    print(f"✓ SAPIAdapter.list_voices(): {len(voices)} voces")
    
    # Probar filtro por idioma
    spanish_voices = [v for v in voices if "spanish" in v.get("description", "").lower()]
    print(f"✓ Voces en español: {len(spanish_voices)}")
    
    # Probar selección de voz
    if voices:
        test_voice = voices[0]["description"]
        result = adapter.set_voice(test_voice)
        print(f"✓ set_voice('{test_voice[:30]}...'): {result}")
        
except Exception as e:
    print(f"✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
