from pathlib import Path
src = Path("ui/modern_window.py").read_text(encoding="utf-8")

i = src.find('setObjectName("groqCard")')
print("=== groqCard qss ===")
print(src[i-200:i+1600])

j = src.find("def _add_msg")
print("\n=== _add_msg (burbuja) ===")
print(src[j:j+2600] if j >= 0 else "NO ENCONTRADO")
