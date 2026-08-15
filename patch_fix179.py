from pathlib import Path
import ast

p = Path("core/text_normalizer.py")
t = p.read_text(encoding="utf-8")

old_fn = """def _protege_homografos(text: str) -> str:
    for mapa in (HOMOGRAFOS, CONTEXTO):"""
new_fn = """def _protege_homografos(text: str) -> str:
    low = text.lower()
    hay_ingles = any(
        re.search(r"\\b" + re.escape(w) + r"\\b", low)
        for w in ENGLISH_TRIGGERS
    )
    if not hay_ingles:
        return text
    for mapa in (HOMOGRAFOS, CONTEXTO):"""
if old_fn in t:
    t = t.replace(old_fn, new_fn, 1)
    print("Regla condicional restaurada y generalizada.")
else:
    print("AVISO: ancla no encontrada.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
