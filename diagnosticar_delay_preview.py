"""
DIAGNÓSTICO DE DELAY EN PREVIEWWORKER
Mide tiempos exactos de cada paso durante la inicialización y primera previsualización.
Simula el flujo real del PreviewWorker de modern_window.py
"""
import time
import sys
import pythoncom
import win32com.client

def medir(nombre, func):
    """Mide el tiempo de ejecución de una función"""
    inicio = time.perf_counter()
    resultado = func()
    fin = time.perf_counter()
    tiempo = fin - inicio
    print(f"⏱️  {nombre}: {tiempo:.3f} segundos")
    return resultado, tiempo

def main():
    print("=" * 70)
    print("DIAGNÓSTICO DE DELAY - PREVIEWWORKER")
    print("=" * 70)
    print()
    
    # Paso 1: Inicialización COM
    print("1️  Inicializando COM...")
    _, t_com = medir("pythoncom.CoInitialize()", pythoncom.CoInitialize)
    print()
    
    # Paso 2: Crear objeto SAPI
    print("2️⃣  Creando objeto SAPI.SpVoice...")
    sapi, t_sapi = medir("Dispatch('SAPI.SpVoice')", 
                         lambda: win32com.client.Dispatch("SAPI.SpVoice"))
    print()
    
    # Paso 3: Obtener lista de voces
    print("3️⃣  Obteniendo lista de voces (GetVoices)...")
    voces, t_voces = medir("sapi.GetVoices()", lambda: list(sapi.GetVoices()))
    print(f"   📊 Total de voces detectadas: {len(voces)}")
    print()
    
    # Paso 4: Primer Speak (Cold Start)
    print("4️⃣  PRIMER SPEAK (Cold Start) - Este es el culpable principal...")
    print("   ⚠️  Aquí es donde se establece la conexión con Microsoft Edge TTS")
    print("   ⚠️  Puede tardar 1-3 segundos la primera vez")
    
    # Seleccionar la primera voz disponible
    if voces:
        sapi.Voice = voces[0]
        nombre_voz = voces[0].GetDescription()
        print(f"    Usando voz: {nombre_voz[:50]}...")
        
        t_cold, _ = medir("sapi.Speak('Hola esta es mi voz', 1)", 
                          lambda: sapi.Speak("Hola esta es mi voz", 1))
        
        # Esperar a que termine
        print("   ⏳ Esperando a que termine el audio...")
        for i in range(50):
            estado = int(sapi.Status.RunningState)
            if estado != 2:  # 2 = Speaking
                break
            time.sleep(0.1)
        print("   ✅ Audio terminado")
    else:
        print("   ❌ No hay voces disponibles")
        t_cold = 0
    print()
    
    # Paso 5: Segundo Speak (ya caliente)
    print("5️⃣  SEGUNDO SPEAK (conexión caliente)...")
    print("   ✅ Este debería ser mucho más rápido (< 0.5 segundos)")
    if voces:
        t_caliente, _ = medir("sapi.Speak('Segunda prueba', 1)", 
                              lambda: sapi.Speak("Segunda prueba", 1))
        
        # Esperar a que termine
        for i in range(50):
            estado = int(sapi.Status.RunningState)
            if estado != 2:
                break
            time.sleep(0.1)
    else:
        t_caliente = 0
    print()
    
    # Paso 6: Búsqueda de voz específica (como hace el PreviewWorker)
    print("6️⃣  Búsqueda de voz por nombre (iterando 300+ voces)...")
    voz_test = voces[0].GetDescription() if voces else ""
    
    def buscar_voz():
        for v in voces:
            if v.GetDescription() == voz_test:
                return v
        return None
    
    _, t_busqueda = medir("Búsqueda lineal de voz", buscar_voz)
    print()
    
    # Resumen
    print("=" * 70)
    print("RESUMEN DE TIEMPOS")
    print("=" * 70)
    print(f"   Inicialización COM:      {t_com:.3f}s")
    print(f"   Crear objeto SAPI:       {t_sapi:.3f}s")
    print(f"   GetVoices():             {t_voces:.3f}s")
    print(f"   Cold Start (1er Speak):  {t_cold:.3f}s  ← CUELLO DE BOTELLA")
    print(f"   Speak caliente:          {t_caliente:.3f}s")
    print(f"   Búsqueda de voz:         {t_busqueda:.3f}s")
    print()
    
    # Diagnóstico
    print("=" * 70)
    print("DIAGNÓSTICO")
    print("=" * 70)
    
    if t_cold > 1.0:
        print(f"   🔴 PROBLEMA CRÍTICO: Cold Start de {t_cold:.1f}s")
        print(f"      Solución: Warm-up silencioso al iniciar el PreviewWorker")
        print(f"      Comando: sapi.Speak('', 1) al crear el hilo")
    elif t_cold > 0.5:
        print(f"   🟡 PROBLEMA MODERADO: Cold Start de {t_cold:.2f}s")
        print(f"      Solución: Warm-up silencioso recomendado")
    else:
        print(f"   ✅ Cold Start aceptable: {t_cold:.2f}s")
    
    if t_busqueda > 0.1:
        print(f"   🟡 Búsqueda lenta: {t_busqueda:.3f}s")
        print(f"      Solución: Implementar caché de voces")
    
    if t_caliente < 0.5:
        print(f"   ✅ Conexión caliente funciona bien: {t_caliente:.3f}s")
    
    print()
    print("=" * 70)
    print("RECOMENDACIÓN FINAL")
    print("=" * 70)
    print("   El delay que experimentas al iniciar la app se debe al Cold Start")
    print("   del adapter SAPI. La primera vez que se llama a Speak(), el adapter")
    print("   debe:")
    print("   1. Resolver DNS de Microsoft")
    print("   2. Establecer conexión TLS")
    print("   3. Autenticarse y obtener token JWT")
    print("   4. Abrir canal WebSocket")
    print()
    print("   Esto toma 1-3 segundos. Las siguientes llamadas son instantáneas.")
    print()
    print("   SOLUCIÓN: Agregar warm-up silencioso en el __init__ del PreviewWorker:")
    print("   ```python")
    print("   def __init__(self):")
    print("       super().__init__()")
    print("       import queue")
    print("       self._q = queue.Queue()")
    print("       self._stopflag = False")
    print("       self._voice_cache = {}")
    print("       self._warmed_up = False")
    print()
    print("   def run(self):")
    print("       # ... código existente ...")
    print("       sapi = win32com.client.Dispatch('SAPI.SpVoice')")
    print("       if not self._warmed_up:")
    print("           self._warmed_up = True")
    print("           try: sapi.Speak('', 1)  # Warm-up silencioso")
    print("           except: pass")
    print("   ```")
    
    try:
        pythoncom.CoUninitialize()
    except:
        pass

if __name__ == "__main__":
    main()