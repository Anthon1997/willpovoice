from pathlib import Path
import ast

p = Path("core/text_normalizer.py")
t = p.read_text(encoding="utf-8")

# ---- Localizar la funcion rota y reemplazarla ----
start = t.find("def _libera_ingles_encerrado")
if start == -1:
    print("AVISO: funcion no encontrada.")
else:
    # Buscar el final (siguiente def de mismo nivel o dos \n\n)
    end_candidates = [
        t.find("\n\ndef ", start),
        t.find("\n\n\ndef ", start),
        t.find("\nENGLISH_TRIGGERS", start),
    ]
    end = min(x for x in end_candidates if x != -1) if any(x != -1 for x in end_candidates) else start + 2000

new_fn = '''def _libera_ingles_encerrado(text: str) -> str:
    """Libera segmentos con palabras inglesas que estan entre comillas/parentesis/corchetes."""
    import re as _re
    # Signos de apertura/cierre emparejados
    pairs = [("\"", "\""), ("'", "'"), ("\\u201c", "\\u201d"),  # comillas rectas y curvas
             ("(", ")"), ("[", "]"), ("{", "}"), ("\\u00ab", "\\u00bb")]  # llaves y angulares
    out = []
    i = 0
    n = len(text)
    while i < n:
        matched = False
        for open_s, close_s in pairs:
            if text[i:i+len(open_s)] == open_s:
                # Buscar el cierre
                j = text.find(close_s, i + len(open_s))
                if j == -1:
                    continue
                segmento = text[i+len(open_s):j]
                low = segmento.lower()
                hay_ingles = any(
                    _re.search(r"\\b" + _re.escape(w) + r"\\b", low)
                    for w in ENGLISH_TRIGGERS
                )
                if hay_ingles:
                    out.append(" ")
                    out.append(segmento)
                    out.append(" ")
                else:
                    out.append(text[i:j+len(close_s)])
                i = j + len(close_s)
                matched = True
                break
        if not matched:
            out.append(text[i])
            i += 1
    return "".join(out)
'''

    t = t[:start] + new_fn + t[end:]
    print("1. _libera_ingles_encerrado reescrita (sin paréntesis sueltos).")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
    print("TEXTO:", e.text)
