from pathlib import Path
import re
src = Path("adapters/sapi_adapter.py").read_text(encoding="utf-8")
i = src.find("def speak(")
if i < 0:
    i = src.find("def speak")
print("=== metodo speak ===")
print(src[i:i+1200] if i>=0 else "NO ENCONTRADO")
print("\n=== constantes de flags ===")
for m in re.finditer(r"SVS\w+\s*=\s*\d+", src):
    ln = src[:m.start()].count("\n")+1
    print("L" + str(ln) + ":", m.group(0))
