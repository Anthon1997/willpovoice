from pathlib import Path
import ast

p = Path("core/text_normalizer.py")
t = p.read_text(encoding="utf-8")

start = t.find("def _libera_ingles_encerrado")
if start == -1:
    print("AVISO: funcion no encontrada.")
else:
    end = t.find("\ndef ", start + 10)
    if end == -1:
        end = len(t)
    new_fn = '''def _libera_ingles_encerrado(text: str) -> str:
    pairs = [
        ('"', '"'), ("'", "'"), ("(", ")"), ("[", "]"),
        ("{", "}"), ("\\u00ab", "\\u00bb"), ("\\u201c", "\\u201d"),
    ]
    out = []
    i = 0
    n = len(text)
    while i < n:
        matched = False
        for open_s, close_s in pairs:
            if text.startswith(open_s, i):
                j = text.find(close_s, i + 1)
                if j == -1:
                    continue
                seg = text[i + 1:j]
                low = seg.lower()
                hay = any(
                    re.search(r"\\b" + re.escape(w) + r"\\b", low)
                    for w in ENGLISH_TRIGGERS
                )
                if hay:
                    out.append(" " + seg + " ")
                else:
                    out.append(text[i:j + 1])
                i = j + 1
                matched = True
                break
        if not matched:
            out.append(text[i])
            i += 1
    return "".join(out)
'''
    t = t[:start] + new_fn + t[end:]
    print("1. _libera_ingles_encerrado reescrita limpia.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
