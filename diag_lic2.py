from pathlib import Path
import glob
import sys

# Configurar la ruta del Escritorio y la carpeta de destino
desktop_path = Path.home() / "Desktop"
output_dir = desktop_path / "testeos"
output_dir.mkdir(parents=True, exist_ok=True)
output_file = output_dir / "resultados.txt"

# Redirigir la salida estándar (print) directamente al archivo .txt
sys.stdout = open(output_file, "w", encoding="utf-8")

try:
    # Leer archivo principal
    license_path = Path("core/license_manager.py")
    print("===== license_manager.py =====")
    if license_path.exists():
        print(license_path.read_text(encoding="utf-8"))
    else:
        print("El archivo core/license_manager.py no fue encontrado.")

    print("\n===== buscando KeyGen =====")
    hits = glob.glob("**/*keygen*.py", recursive=True) + \
           glob.glob("**/*key_gen*.py", recursive=True) + \
           glob.glob("scripts/**/*.py", recursive=True)

    for f in sorted(set(hits)):
        print(f"\n----- {f} -----")
        try:
            print(Path(f).read_text(encoding="utf-8"))
        except Exception as e:
            print(f"No se pudo leer el archivo: {e}")

finally:
    # Cerrar el archivo correctamente al terminar
    sys.stdout.close()
