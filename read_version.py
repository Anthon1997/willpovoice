import sys
sys.path.insert(0, ".")
try:
    from app.version import APP_VERSION
    print(f"Versión actual: {APP_VERSION}")
except Exception as e:
    print(f"Error leyendo versión: {e}")
