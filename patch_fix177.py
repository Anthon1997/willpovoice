from pathlib import Path
import ast

p = Path("core/text_normalizer.py")
t = p.read_text(encoding="utf-8")

# ---- 1. "vacio" sale del mapa siempre -> pasa al mapa contextual ----
old_map = '''HOMOGRAFOS = {
    "sale": "salee",
    "sales": "salees",
    "vacio": "vacioo",
    "vacío": "vacioo",
    "pie": "piee",'''
new_map = '''HOMOGRAFOS = {
    "sale": "salee",
    "sales": "salees",
    "pie": "piee",'''
if old_map in t:
    t = t.replace(old_map, new_map, 1)
    print("1. 'vacio' movido a proteccion contextual.")

# ---- 2. Mapa contextual + disparadores de ingles ----
if "CONTEXTO = {" not in t:
    bloque = '''CONTEXTO = {
    "vacio": "vacioo",
    "vacío": "vacioo",
}
ENGLISH_TRIGGERS = [
    "hello", "hi", "hey", "bye", "the", "and", "is", "are", "was",
    "were", "be", "been", "being", "have", "has", "had", "does",
    "did", "will", "would", "could", "should", "shall", "this",
    "that", "these", "those", "here", "there", "what", "when",
    "where", "who", "why", "how", "with", "from", "for", "not",
    "please", "thanks", "thank", "good", "morning", "night",
    "today", "tomorrow", "tonight", "friend", "friends", "my",
    "your", "our", "their", "his", "her", "its", "you", "yours",
    "see", "look", "watch", "love", "life", "time", "day", "days",
    "week", "month", "year", "world", "people", "man", "woman",
    "boy", "girl", "dog", "cat", "car", "house", "home", "work",
    "job", "play", "game", "music", "song", "book", "new", "old",
    "big", "small", "hot", "cold", "water", "food", "name",
    "sorry", "welcome", "okay", "ok", "yes", "one", "two",
    "three", "four", "five", "six", "seven", "eight", "nine",
    "ten",
] + list(HOMOGRAFOS)


'''
    anchor = t.find("def _protege_homografos")
    if anchor != -1:
        t = t[:anchor] + bloque + t[anchor:]
        print("2. CONTEXTO + ENGLISH_TRIGGERS agregados.")

# ---- 3. Regla contextual en _protege_homografos ----
old_fn = '''def _protege_homografos(text: str) -> str:
    for palabra, resp in HOMOGRAFOS.items():
        pat = re.compile(
            r"\\b" + re.escape(palabra) + r"\\b", re.IGNORECASE)
        def repl(m, resp=resp):
            orig = m.group(0)
            return resp.capitalize() if orig[0].isupper() else resp
        text = pat.sub(repl, text)
    return text'''
new_fn = '''def _protege_homografos(text: str) -> str:
    low = text.lower()
    hay_ingles = any(
        re.search(r"\\b" + re.escape(w) + r"\\b", low)
        for w in ENGLISH_TRIGGERS
    )
    mapas = [HOMOGRAFOS] + ([CONTEXTO] if hay_ingles else [])
    for mapa in mapas:
        for palabra, resp in mapa.items():
            pat = re.compile(
                r"\\b" + re.escape(palabra) + r"\\b", re.IGNORECASE)
            def repl(m, resp=resp):
                orig = m.group(0)
                return resp.capitalize() if orig[0].isupper() else resp
            text = pat.sub(repl, text)
    return text'''
if old_fn in t:
    t = t.replace(old_fn, new_fn, 1)
    print("3. Regla contextual aplicada.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
