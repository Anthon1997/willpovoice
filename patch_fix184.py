from pathlib import Path
import ast

p = Path("core/text_normalizer.py")
t = p.read_text(encoding="utf-8")

# ---- 1. Mapa de pronunciacion tecnica ----
if "TECH = {" not in t:
    bloque = '''TECH = {
    "C++": " ce plus plus ",
    "c++": " ce plus plus ",
    "Python": "Paiton",
    "python": "paiton",
    "PyTorch": "Paitorch",
    "pytorch": "paitorch",
    "TensorFlow": "Tensor Flou",
    "JavaScript": "Yava Script",
    "javascript": "yava script",
}


'''
    anchor = t.find("def _polish")
    if anchor != -1:
        t = t[:anchor] + bloque + t[anchor:]
        print("1. Mapa TECH agregado.")

# ---- 2. Aplicarlo al inicio de _polish (antes de simbolos) ----
old = '''def _polish(text: str) -> str:
    text = re.sub(r"\\$\\s*(\\d+(?:[.,]\\d+)*)", r"\\1 dolares", text)'''
new = '''def _polish(text: str) -> str:
    for k, v in TECH.items():
        text = text.replace(k, v)
    text = re.sub(r"\\$\\s*(\\d+(?:[.,]\\d+)*)", r"\\1 dolares", text)'''
if old in t:
    t = t.replace(old, new, 1)
    print("2. TECH aplicado antes de simbolos (C++ no se rompe).")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
