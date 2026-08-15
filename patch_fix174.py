from pathlib import Path
import ast

p = Path("core/text_normalizer.py")
t = p.read_text(encoding="utf-8")

start = t.find("def normalize_for_tts")
new_tail = '''SYMBOLS = [
    ("&", " y "),
    ("+", " mas "),
    ("=", " igual a "),
    ("#", " numero "),
    ("@", " arroba "),
    ("~", " aproximadamente "),
    ("°", " grados "),
]
ABBR = {
    "sr.": "senor",
    "sra.": "senora",
    "srta.": "senorita",
    "dr.": "doctor",
    "dra.": "doctora",
    "ud.": "usted",
    "uds.": "ustedes",
    "pag.": "pagina",
    "art.": "articulo",
    "etc.": "etcetera",
}


def _polish(text: str) -> str:
    text = re.sub(r"\\$\\s*(\\d+(?:[.,]\\d+)*)", r"\\1 dolares", text)
    text = re.sub(r"€\\s*(\\d+(?:[.,]\\d+)*)", r"\\1 euros", text)
    for sym, word in SYMBOLS:
        text = text.replace(sym, word)
    for abbr, full in ABBR.items():
        pattern = re.compile(re.escape(abbr), re.IGNORECASE)
        text = pattern.sub(
            lambda m: full.capitalize()
            if m.group(0)[0].isupper() else full,
            text,
        )
    text = re.sub(r"[ \\t]+", " ", text)
    text = re.sub(r"\\s+([,.;!?])", r"\\1", text)
    return text


def normalize_for_tts(text: str) -> str:
    if not text:
        return text
    text = _polish(text)
    text = re.sub(
        r"(\\b\\d{1,3}(?:\\.\\d{3})+(?:,\\d+)?\\b|\\b\\d+(?:[.,]\\d+)?)\\s*%",
        lambda m: _num_match(m.group(1)) + " por ciento",
        text,
    )
    text = re.sub(r"\\s*%", "", text)
    text = re.sub(NUM_PAT, _num_match, text)
    return text
'''
if start != -1:
    t = t[:start] + new_tail
    print("Pulido natural agregado al normalizador.")
else:
    print("AVISO: normalize_for_tts no encontrado.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
