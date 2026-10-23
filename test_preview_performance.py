"""
DIAGNÓSTICO DE RENDIMIENTO - PREVISUALIZACIÓN DE VOCES
Mide tiempos exactos de cada paso del PreviewWorker
"""
import time
import pythoncom
import win32com.client
from pathlib import Path
import sys

def measure_step(name, func):
    """Mide el tiempo de ejecución de una función"""
    start = time.perf_counter()
    result = func()
    elapsed = time.perf_counter() - start
    print(f"⏱️  {name}: {elapsed:.3f} segundos")
    return result, elapsed

def main():
    print("=" * 60)
    print("DIAGNÓSTICO DE RENDIMIENTO - PREVISUALIZACIÓN")
    print("=" * 60)
    
    # 1. Inicialización de SAPI
    print("\n1️⃣  Inicializando SAPI...")
    sapi, t_init = measure_step("Inicialización SAPI", lambda: win32com.client.Dispatch("SAPI.SpVoice"))
    
    # 2. Obtener lista de voces
    print("\n2️  Obteniendo lista de voces...")
    voices, t_voices = measure_step("GetVoices()", lambda: list(sapi.GetVoices()))
    print(f"   📊 Total de voces: {len(voices)}")
    
    # 3. Búsqueda lineal de voz (simulando el código actual)
    print("\n3️⃣  Búsqueda lineal de voz (código actual)...")
    test_voice = "Microsoft Andrew Multilingual Online (Natural)"
    
    def search_linear():
        for tk in voices:
            if tk.GetDescription() == test_voice:
                return tk
        return None
    
    tok, t_search = measure_step("Búsqueda lineal", search_linear)
    
    # 4. Cold Start (primera conexión al endpoint)
    print("\n4️⃣  Cold Start (primera conexión al endpoint)...")
    if tok:
        sapi.Voice = tok
        def cold_start():
            sapi.Speak("Hola esta es mi voz", 1)
            # Esperar a que termine
            for _ in range(100):
                st = int(sapi.Status.RunningState)
                if st != 2:
                    break
                time.sleep(0.1)
        _, t_cold = measure_step("Cold Start (primer Speak)", cold_start)
    else:
        print("   ⚠️  Voz de prueba no encontrada")
        t_cold = 0
    
    # 5. Segunda previsualización (ya con caché de conexión)
    print("\n5️⃣  Segunda previsualización (conexión caliente)...")
    if tok:
        def warm_start():
            sapi.Speak("Segunda prueba", 1)
            for _ in range(100):
                st = int(sapi.Status.RunningState)
                if st != 2:
                    break
                time.sleep(0.1)
        _, t_warm = measure_step("Speak caliente", warm_start)
    else:
        t_warm = 0
    
    # 6. Búsqueda con caché (simulación)
    print("\n6️⃣  Búsqueda con caché (simulación)...")
    cache = {test_voice: tok}
    def search_cached():
        return cache.get(test_voice)
    _, t_cached = measure_step("Búsqueda con caché", search_cached)
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE TIEMPOS")
    print("=" * 60)
    print(f"   Inicialización SAPI:     {t_init:.3f}s")
    print(f"   Obtener voces:           {t_voices:.3f}s")
    print(f"   Búsqueda lineal:         {t_search:.3f}s")
    print(f"   Cold Start:              {t_cold:.3f}s")
    print(f"   Speak caliente:          {t_warm:.3f}s")
    print(f"   Búsqueda con caché:      {t_cached:.3f}s")
    print(f"   ─────────────────────────────────")
    print(f"   TOTAL (sin caché):       {t_init + t_voices + t_search + t_cold:.3f}s")
    print(f"   TOTAL (con caché):       {t_init + t_voices + t_cached + t_warm:.3f}s")
    print("=" * 60)
    
    # Diagnóstico
    print("\n DIAGNÓSTICO:")
    if t_cold > 1.0:
        print("   ⚠️  Cold Start es el principal cuello de botella")
        print("      Solución: Warm-up silencioso al iniciar el worker")
    if t_search > 0.1:
        print("   ⚠️  Búsqueda lineal es lenta")
        print("      Solución: Implementar caché de tokens")
    if t_warm < 0.5:
        print("   ✅ Conexión caliente funciona bien")
    
    pythoncom.CoUninitialize()

if __name__ == "__main__":
    main()