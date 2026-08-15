from pathlib import Path
import subprocess

t = Path("ui/modern_window.py").read_text(encoding="utf-8")
print("Textos en el arbol actual:", "OK" if t.count("Ã") == 0 else f"CORRUPTO ({t.count('Ã')} mojibake)")

c = subprocess.run(["git", "show", "HEAD:ui/modern_window.py"],
                   capture_output=True).stdout.decode("utf-8", "replace")
print("Textos en el ultimo commit:", "OK" if c.count("Ã") == 0 else f"CORRUPTO ({c.count('Ã')} mojibake)")

print("\n=== Zona del boton Descargar e instalar ===")
i = t.find("def _on_download_clicked")
if i != -1:
    print(t[i:i+1500])
