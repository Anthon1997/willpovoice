from pathlib import Path
import ast

p = Path("core/text_normalizer.py")
t = p.read_text(encoding="utf-8")

# ---- 1. Funcion que libera ingles encerrado en signos ----
if "def _libera_ingles_encerrado" not in t:
    fn = '''def _libera_ingles_encerrado(text: str) -> str:
    pat = re.compile(
        r'([\\""“”\'\\(\\[\\{«])'
        r'([^\\""“”\'\\(\\)\\[\\]\\{\\}«»]{1,200}?)'
        r'([\\""“”\'\\)\\]\\}»])'
    )

    def repl(m):
        seg = m.group(2)
        low = seg.lower()
        hay_ingles = any(
            re.search(r"\\b" + re.escape(w) + r"\\b", low)
            for w in ENGLISH_TRIGGERS
        )
        if hay_ingles:
            return " " + seg + " "
        return m.group(0)

    return pat.sub(repl, text)


'''
    anchor = t.find("def _protege_homografos")
    if anchor != -1:
        t = t[:anchor] + fn + t[anchor:]
        print("1. _libera_ingles_encerrado agregado.")

# ---- 2. Aplicarlo en normalize_for_tts ----
old = """    text = EMOJI_RESTO.sub(" ", text)
    text = _polish(text)"""
new = """    text = EMOJI_RESTO.sub(" ", text)
    text = _libera_ingles_encerrado(text)
    text = _polish(text)"""
if old in t:
    t = t.replace(old, new, 1)
    print("2. Integrado en el pipeline.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
