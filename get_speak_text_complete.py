from pathlib import Path
import re

m = Path("ui/modern_window.py").read_text(encoding="utf-8")

print("=== MÉTODO speak_text COMPLETO ===")
match = re.search(r'def speak_text\(self\).*?(?=\n    def |\nclass |\Z)', m, re.DOTALL)
if match:
    metodo = match.group(0)
    print(metodo)
    print(f"\n[Longitud: {len(metodo)} caracteres, {len(metodo.splitlines())} líneas]")
else:
    print("NO ENCONTRADO")

print("\n=== MÉTODO export_wav COMPLETO ===")
match2 = re.search(r'def export_wav\(self.*?(?=\n    def |\nclass |\Z)', m, re.DOTALL)
if match2:
    metodo2 = match2.group(0)
    print(metodo2[:3000])
    print(f"\n[Longitud: {len(metodo2)} caracteres]")

print("\n=== MÉTODO export_mp3 COMPLETO ===")
match3 = re.search(r'def export_mp3\(self.*?(?=\n    def |\nclass |\Z)', m, re.DOTALL)
if match3:
    metodo3 = match3.group(0)
    print(metodo3[:3000])
    print(f"\n[Longitud: {len(metodo3)} caracteres]")
