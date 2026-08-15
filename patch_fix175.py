from pathlib import Path
import ast

p = Path("core/text_normalizer.py")
t = p.read_text(encoding="utf-8")

# ---- 1. Numeros con acentos (diccion perfecta) ----
old_uni = '''UNIDADES = [
    "", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho",
    "nueve", "diez", "once", "doce", "trece", "catorce", "quince",
    "dieciseis", "diecisiete", "dieciocho", "diecinueve", "veinte",
    "veintiuno", "veintidos", "veintitres", "veinticuatro", "veinticinco",
    "veintiseis", "veintisiete", "veintiocho", "veintinueve",
]'''
new_uni = '''UNIDADES = [
    "", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho",
    "nueve", "diez", "once", "doce", "trece", "catorce", "quince",
    "dieciséis", "diecisiete", "dieciocho", "diecinueve", "veinte",
    "veintiuno", "veintidós", "veintitrés", "veinticuatro", "veinticinco",
    "veintiséis", "veintisiete", "veintiocho", "veintinueve",
]'''
if old_uni in t:
    t = t.replace(old_uni, new_uni, 1)
    print("1. Unidades con acentos.")

t = t.replace('"un millon" if m == 1', '"un millón" if m == 1', 1)
t = t.replace('_menos_millon(m) + " millones"', '_menos_millon(m) + " millones"', 1)
print("2. Millón con acento.")

# ---- 3. Emojis -> palabras + limpieza de restos ----
if "EMOJIS = {" not in t:
    emojis = '''EMOJIS = {
    "😀": "carita sonriente", "😁": "carita alegre", "😂": "risa",
    "🤣": "risa", "😊": "carita amable", "😍": "carita enamorada",
    "😘": "beso", "😎": "carita genial", "🤔": "duda", "😢": "tristeza",
    "😭": "llanto", "😡": "enojo", "👍": "me gusta", "👎": "no me gusta",
    "🙏": "por favor", "👏": "aplausos", "💪": "fuerza", "🔥": "fuego",
    "❤": "corazon", "💜": "corazon morado", "💙": "corazon azul",
    "💚": "corazon verde", "🖤": "corazon negro", "⭐": "estrella",
    "🌟": "estrella brillante", "🎉": "fiesta", "🎵": "musica",
    "🎙": "microfono", "✅": "correcto", "❌": "equivocado",
    "⚠": "atencion", "📢": "anuncio", "💰": "dinero", "🚀": "cohete",
    "💡": "idea", "📌": "importante", "🕐": "hora", "📅": "fecha",
}
EMOJI_RESTO = re.compile(
    "[\\U0001F000-\\U0001FAFF\\U00002600-\\U000027BF"
    "\\U00002B00-\\U00002BFF\\U0001F1E6-\\U0001F1FF\\uFE0F\\u200D]+")


'''
    anchor = t.find("SYMBOLS = [")
    if anchor != -1:
        t = t[:anchor] + emojis + t[anchor:]
        print("3. Mapa de emojis agregado.")

old_norm = """def normalize_for_tts(text: str) -> str:
    if not text:
        return text
    text = _polish(text)"""
new_norm = """def normalize_for_tts(text: str) -> str:
    if not text:
        return text
    for em, word in EMOJIS.items():
        text = text.replace(em, " " + word + " ")
    text = EMOJI_RESTO.sub(" ", text)
    text = _polish(text)"""
if old_norm in t:
    t = t.replace(old_norm, new_norm, 1)
    print("4. Emojis procesados antes del pulido.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
