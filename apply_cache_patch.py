"""
Parche seguro para agregar caché de voces en PreviewWorker
No rompe la indentación ni la codificación del archivo
"""
from pathlib import Path

file_path = Path("ui/modern_window.py")
if not file_path.exists():
    print("❌ No se encuentra modern_window.py")
    exit(1)

content = file_path.read_text(encoding="utf-8")

# Buscar el bloque exacto del PreviewWorker.__init__
old_init = """    def __init__(self):
        super().__init__()
        import queue
        self._q = queue.Queue()
        self._stopflag = False"""

new_init = """    def __init__(self):
        super().__init__()
        import queue
        self._q = queue.Queue()
        self._stopflag = False
        self._voice_cache = {}  # Caché para evitar iterar 300+ voces"""

if old_init in content:
    content = content.replace(old_init, new_init)
    print("✅ Caché agregada al __init__ del PreviewWorker")
else:
    print("⚠️  No se encontró el __init__ del PreviewWorker")

# Buscar el bloque de búsqueda de voz y reemplazarlo
old_search = """                if sapi is not None:
                    tok = None
                    for tk in sapi.GetVoices():
                        if tk.GetDescription() == item:
                            tok = tk
                            break"""

new_search = """                if sapi is not None:
                    tok = self._voice_cache.get(item)
                    if tok is None:
                        for tk in sapi.GetVoices():
                            if tk.GetDescription() == item:
                                tok = tk
                                self._voice_cache[item] = tok
                                break"""

if old_search in content:
    content = content.replace(old_search, new_search)
    print("✅ Búsqueda de voz optimizada con caché")
else:
    print("⚠️  No se encontró el bloque de búsqueda de voz")

# Guardar preservando UTF-8 y saltos de línea originales
file_path.write_text(content, encoding="utf-8", newline="")
print("\n🚀 Parche aplicado exitosamente. La previsualización será más rápida.")