from pathlib import Path
import ast

p = Path("core/text_normalizer.py")
t = p.read_text(encoding="utf-8")

# ---- 1. "vacio" protegido siempre con guard activo ----
old_fn = """def _protege_homografos(text: str) -> str:
    low = text.lower()
    hay_ingles = any(
        re.search(r"\\b" + re.escape(w) + r"\\b", low)
        for w in ENGLISH_TRIGGERS
    )
    mapas = [HOMOGRAFOS] + ([CONTEXTO] if hay_ingles else [])
    for mapa in mapas:"""
new_fn = """def _protege_homografos(text: str) -> str:
    for mapa in (HOMOGRAFOS, CONTEXTO):"""
if old_fn in t:
    t = t.replace(old_fn, new_fn, 1)
    print("1. 'vacio' protegido siempre con guard.")

# ---- 2. Emojis eliminados en silencio (sin lectura) ----
old_em = """    for em, word in EMOJIS.items():
        text = text.replace(em, " " + word + " ")
    text = EMOJI_RESTO.sub(" ", text)"""
new_em = """    text = EMOJI_RESTO.sub(" ", text)"""
if old_em in t:
    t = t.replace(old_em, new_em, 1)
    print("2. Emojis eliminados por completo (sin lectura).")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
