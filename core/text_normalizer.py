from __future__ import annotations

import re

UNIDADES = [
    "", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho",
    "nueve", "diez", "once", "doce", "trece", "catorce", "quince",
    "dieciséis", "diecisiete", "dieciocho", "diecinueve", "veinte",
    "veintiuno", "veintidós", "veintitrés", "veinticuatro", "veinticinco",
    "veintiséis", "veintisiete", "veintiocho", "veintinueve",
]
DECENAS = ["", "", "veinte", "treinta", "cuarenta", "cincuenta",
           "sesenta", "setenta", "ochenta", "noventa"]
CENTENAS = ["", "ciento", "doscientos", "trescientos", "cuatrocientos",
            "quinientos", "seiscientos", "setecientos", "ochocientos",
            "novecientos"]


def _menos_mil(n: int) -> str:
    if n == 0:
        return "cero"
    if n == 100:
        return "cien"
    parts = []
    c, rest = divmod(n, 100)
    if c:
        parts.append(CENTENAS[c])
    if rest:
        if rest < 30:
            parts.append(UNIDADES[rest])
        else:
            d, u = divmod(rest, 10)
            s = DECENAS[d]
            if u:
                s += " y " + UNIDADES[u]
            parts.append(s)
    return " ".join(parts)


def _menos_millon(n: int) -> str:
    if n < 1000:
        return _menos_mil(n)
    m, rest = divmod(n, 1000)
    out = "mil" if m == 1 else _menos_mil(m) + " mil"
    if rest:
        out += " " + _menos_mil(rest)
    return out


def numero_a_palabras(n: int) -> str:
    if n < 0:
        return "menos " + numero_a_palabras(-n)
    if n >= 1_000_000:
        m, rest = divmod(n, 1_000_000)
        out = "un millón" if m == 1 else _menos_millon(m) + " millones"
        if rest:
            out += " " + _menos_millon(rest)
        return out
    return _menos_millon(n)


def _num_match(m) -> str:
    raw = m.group(0) if hasattr(m, "group") else str(m)
    dec = None
    if "," in raw and "." in raw:
        entero = raw.split(",")[0].replace(".", "")
        dec = raw.split(",")[1]
    elif "." in raw:
        if re.fullmatch(r"\d{1,3}(\.\d{3})+", raw):
            entero = raw.replace(".", "")
        else:
            entero, dec = raw.split(".")
    elif "," in raw:
        entero, dec = raw.split(",")
    else:
        entero = raw
    out = numero_a_palabras(int(entero))
    if dec is not None:
        out += " punto " + " ".join(numero_a_palabras(int(d)) for d in dec)
    return out


NUM_PAT = r"\b\d{1,3}(?:\.\d{3})+(?:,\d+)?\b|\b\d+(?:[.,]\d+)?\b"


EMOJIS = {
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
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF"
    "\U00002B00-\U00002BFF\U0001F1E6-\U0001F1FF\uFE0F\u200D]+")


SYMBOLS = [
    ("&", " y "),
    ("+", " mas "),
    (" - ", " menos "),
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


TECH = {
    "Python": "Paiton",
    "python": "paiton",
    "PyTorch": "Paitorch",
    "pytorch": "paitorch",
    "TensorFlow": "Tensor Flou",
    "JavaScript": "Yava Script",
    "javascript": "yava script",
}


def _polish(text: str) -> str:
    for k, v in TECH.items():
        text = text.replace(k, v)
    text = re.sub(r"\$\s*(\d+(?:[.,]\d+)*)", r"\1 dolares", text)
    text = re.sub(r"€\s*(\d+(?:[.,]\d+)*)", r"\1 euros", text)
    for sym, word in SYMBOLS:
        text = text.replace(sym, word)
    for abbr, full in ABBR.items():
        pattern = re.compile(re.escape(abbr), re.IGNORECASE)
        text = pattern.sub(
            lambda m: full.capitalize()
            if m.group(0)[0].isupper() else full,
            text,
        )
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\s+([,.;!?])", r"\1", text)
    return text


HOMOGRAFOS = {
    "sale": "salee",
    "sales": "salees",
    "pie": "piee",
    "son": "sonn",
    "tan": "tann",
    "pan": "pann",
    "mar": "marr",
    "par": "parr",
    "lima": "limaa",
    "cola": "colaa",
    "peso": "pesoo",
    "pesos": "pesoos",
}


CONTEXTO = {
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

ENGLISH_DETECT = ENGLISH_TRIGGERS + [
    "a", "an", "and", "but", "if", "then", "than", "because", "while",
    "during", "before", "after", "above", "below", "between", "into",
    "through", "about", "against", "again", "once", "just", "now",
    "such", "very", "too", "also", "only", "even", "still", "already",
    "yet", "ever", "never", "always", "often", "sometimes", "usually",
    "finally", "really", "actually", "basically", "probably", "maybe",
    "perhaps", "almost", "enough", "quite", "rather", "soon", "there",
    "here", "we", "they", "them", "him", "his", "its", "our", "your",
    "their", "mine", "yours", "ours", "theirs", "myself", "yourself",
    "himself", "herself", "itself", "ourselves", "themselves", "to",
    "of", "in", "on", "at", "by", "for", "with", "from", "up", "down",
    "out", "off", "over", "under", "away", "back", "forward", "is",
    "am", "are", "was", "were", "be", "been", "being", "do", "does",
    "did", "done", "doing", "have", "has", "had", "having", "will",
    "would", "can", "could", "shall", "should", "must", "might",
    "need", "let", "get", "got", "gets", "getting", "go", "goes",
    "went", "gone", "going", "make", "makes", "made", "making",
    "take", "takes", "took", "taken", "taking", "know", "knows",
    "knew", "known", "think", "thinks", "thought", "see", "sees",
    "saw", "seen", "come", "comes", "came", "coming", "want",
    "wants", "wanted", "like", "likes", "liked", "say", "says",
    "said", "tell", "tells", "told", "ask", "asks", "asked",
    "answer", "answers", "give", "gives", "gave", "given", "find",
    "finds", "found", "help", "helps", "helped", "try", "tries",
    "tried", "call", "calls", "called", "keep", "keeps", "kept",
    "leave", "leaves", "left", "live", "lives", "lived", "move",
    "moves", "moved", "run", "runs", "ran", "running", "stop",
    "stops", "stopped", "start", "starts", "started", "turn",
    "turns", "turned", "open", "opens", "opened", "close",
    "closes", "closed", "read", "reads", "write", "writes",
    "wrote", "written", "speak", "speaks", "spoke", "listen",
    "listens", "push", "pushed", "pull", "pulled", "deploy",
    "deployed", "build", "built", "release", "released",
    "refactor", "loop", "loops", "break", "breaks", "broke",
    "broken", "it", "as", "or", "us",
]




def _libera_ingles_encerrado(text: str) -> str:
    pairs = [
        ('"', '"'), ("'", "'"), ("(", ")"), ("[", "]"),
        ("{", "}"), ("\u00ab", "\u00bb"), ("\u201c", "\u201d"),
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
                    re.search(r"\b" + re.escape(w) + r"\b", low)
                    for w in ENGLISH_DETECT
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

def _protege_homografos(text: str) -> str:
    low = text.lower()
    hay_ingles = any(
        re.search(r"\b" + re.escape(w) + r"\b", low)
        for w in ENGLISH_DETECT
    )
    if not hay_ingles:
        return text
    for mapa in (HOMOGRAFOS, CONTEXTO):
        for palabra, resp in mapa.items():
            pat = re.compile(
                r"\b" + re.escape(palabra) + r"\b", re.IGNORECASE)
            def repl(m, resp=resp):
                orig = m.group(0)
                return resp.capitalize() if orig[0].isupper() else resp
            text = pat.sub(repl, text)
    return text


def needs_homograph_guard(voice_desc: str) -> bool:
    low = (voice_desc or "").lower()
    return "multilingual" in low and "spanish" not in low


def _es_spanish(text):
    low = (text or "").lower()
    if re.search(r"[\u00bf\u00a1\u00f1\u00e1\u00e9\u00ed\u00f3\u00fa\u00fc]", low):
        return True
    common = (" el ", " la ", " los ", " las ", " de ", " que ", " y ",
              " en ", " por ", " para ", " con ", " una ", " un ", " es ", " son ")
    return sum(1 for w in common if w in low) >= 2



_UPPER_ES = {
    "GUION": "GUIÓN", "DIA": "DÍA", "MAS": "MÁS", "SI": "SÍ", "ESTA": "ESTÁ",
    "TECNOLOGIA": "TECNOLOGÍA", "INNOVACION": "INNOVACIÓN", "MUSICA": "MÚSICA",
    "RAPIDO": "RÁPIDO", "FACIL": "FÁCIL", "UNICO": "ÚNICO", "ULTIMO": "ÚLTIMO",
    "ULTIMA": "ÚLTIMA", "NUMERO": "NÚMERO", "TELEFONO": "TELÉFONO",
    "PAGINA": "PÁGINA", "DISENO": "DISEÑO", "ESPANOL": "ESPAÑOL",
    "INGLES": "INGLÉS", "AUTOMATICO": "AUTOMÁTICO", "BASICO": "BÁSICO",
    "CLASICO": "CLÁSICO", "PRACTICO": "PRÁCTICO", "DINAMICO": "DINÁMICO",
    "ELECTRONICO": "ELECTRÓNICO", "TRADUCCION": "TRADUCCIÓN",
    "CONVERSION": "CONVERSIÓN", "GENERACION": "GENERACIÓN",
    "CREACION": "CREACIÓN", "PRODUCCION": "PRODUCCIÓN",
    "COMUNICACION": "COMUNICACIÓN", "INFORMACION": "INFORMACIÓN",
    "APLICACION": "APLICACIÓN", "CONFIGURACION": "CONFIGURACIÓN",
    "EDUCACION": "EDUCACIÓN", "TECNICO": "TÉCNICO", "CIENTIFICO": "CIENTÍFICO",
    "MEDICO": "MÉDICO", "POLITICO": "POLÍTICO", "ECONOMICO": "ECONÓMICO",
    "ESTRATEGICO": "ESTRATÉGICO", "METODO": "MÉTODO", "CATEGORIA": "CATEGORÍA",
    "PUBLICITARIO": "PUBLICITARIO", "AMOR": "AMOR",
}


_ES_HEAD = {
    "guion", "publicitario", "publicitaria", "publicidad", "anuncio",
    "promo", "promocion", "oferta", "descuento", "precio", "producto",
    "calidad", "garantia", "envio", "gratis", "compra", "venta",
    "servicio", "atencion", "cliente", "empresa", "negocio", "marca",
    "tecnologia", "innovacion", "mensaje", "texto", "voz", "audio",
    "video", "musica", "espectacular", "increible", "unico", "nuevo",
    "mejor", "grande", "amor", "vida", "estilo", "modo", "forma",
    "parte", "lugar", "momento", "hoy", "ahora", "siempre", "todo",
}

_ES_STOP = {
    "a", "tus", "tu", "mi", "su", "mis", "sus", "que", "de", "la", "el",
    "los", "las", "un", "una", "unos", "unas", "en", "con", "por", "para",
    "se", "no", "si", "y", "o", "u", "pero", "porque", "cuando", "como",
    "mas", "menos", "lo", "le", "les", "me", "te", "nos", "es", "son",
    "esta", "estan", "hay", "ser", "estar", "dale", "da", "dar", "hacer",
    "haz", "tiene", "tener", "quieres", "quiere", "puedes", "puede",
    "merecen", "merece", "ideas", "voz", "cada", "mes", "solo", "para",
}



def _acentua_mayusculas_es(text):
    s = (text or "").strip()
    if not s:
        return text
    if "\n" in s or len(s.split()) > 6:
        return text
    letras = [c for c in s if c.isalpha()]
    if not letras:
        return text
    up = sum(1 for c in letras if c.isupper()) / len(letras)
    if up < 0.7:
        return text
    if re.search(r"[ÁÉÍÓÚÜÑ]", s):
        return text
    toks = re.findall(r"[A-Za-zÑñ]+", s)
    if any(tok.isupper() and len(tok) >= 3 and tok.lower() not in _ES_HEAD
           for tok in toks):
        return text
    low_words = set(re.findall(r"\b[a-zñ]+\b", s.lower()))
    if not (low_words & _ES_HEAD):
        return text
    return "El " + s.lower()






def _chunk_lang(part):
    s = part.strip()
    if not s:
        return "mix"
    low = s.lower()
    if re.search(r"[\u00e1\u00e9\u00ed\u00f3\u00fa\u00fc\u00f1\u00bf\u00a1]", low):
        return "es"
    words = set(re.findall(r"\b[a-z\u00f1]+\b", low))
    if words & _ES_HEAD:
        return "es"
    compact = re.sub(r"[^A-Za-z]", "", s)
    if compact and compact.isupper() and len(compact) >= 3:
        return "brand"
    return "mix"


def _ancla_es_mixta(text):
    if not text:
        return text
    parts = re.split(r"([,;—–-]|\n)", text)
    out = []
    prev = None
    for part in parts:
        if part in (",", ";", "—", "–", "-", "\n"):
            out.append(part)
            continue
        lang = _chunk_lang(part)
        if lang == "es" and prev in ("brand", "en"):
            lead = part[:len(part) - len(part.lstrip())]
            rest = part[len(part) - len(part.lstrip()):].rstrip()
            low = rest.lower()
            if (not re.match(r"^(el|la|los|las|un|una|unos|unas|y|de|en|con|por|para)\b", low)
                    and not (set(re.findall(r"\b[a-zñ]+\b", low)) & _ES_STOP)):
                part = lead + "el " + low
        out.append(part)
        if lang != "mix":
            prev = lang
    return "".join(out)




_EN_LOAN = {
    # comida
    "cheddar": "chédar", "bacon": "beicon", "burger": "burguer",
    "burgers": "burguers", "brioche": "briosh", "crispy": "crispi",
    "crunch": "cranch", "crunchy": "cranchi", "snack": "snak",
    "snacks": "snaks", "coffee": "cofi", "cake": "keik",
    "cupcake": "capkeik", "cupcakes": "capkeiks", "chef": "shef",
    "grill": "gril", "takeaway": "teikeuei",
    # tech
    "software": "softwer", "hardware": "hardwer", "online": "onlain",
    "offline": "oflain", "streaming": "estriming", "download": "daunloud",
    "upload": "aploud", "click": "clic", "link": "link",
    "bluetooth": "blutut", "smartphone": "esmartfoun", "phone": "foun",
    "app": "ap", "apps": "aps", "email": "imel", "cloud": "claud",
    "data": "deita", "byte": "bait", "bytes": "baits",
    "screen": "escrin", "display": "displei", "laptop": "laptop",
    "mouse": "maus", "keyboard": "kibord",
    # gaming
    "gamer": "gueimer", "gamers": "gueimers", "gaming": "gueiming",
    "gameplay": "gueimplei", "stream": "estrim",
    "streamer": "estrimer", "streamers": "estrimers",
    # marketing / negocio
    "marketing": "marketin", "branding": "branding", "sale": "seil",
    "sales": "seils", "discount": "discaunt", "offer": "ofer",
    "campaign": "campein", "feedback": "fidbak", "review": "riviu",
    "reviews": "rivius", "rating": "reiting", "upgrade": "apgreid",
    "switch": "suich", "bundle": "bandol", "earbud": "irbad",
    "earbuds": "irbads", "next-gen": "nekst yen", "premium": "primiom",
    "delivery": "dilibery", "stock": "stok", "retail": "ritel",
    # cotidiano
    "out": "aut", "up": "ap", "down": "daun", "off": "of",
    "ok": "okei", "okay": "okei", "hello": "jelou", "bye": "bai",
    "welcome": "uelcom", "please": "plis", "thanks": "tanks",
    "look": "luk", "outfit": "autfit", "style": "stail",
    "trend": "trend", "trendy": "trendi", "team": "tim",
    "staff": "staf", "manager": "manayer", "leader": "lider",
}



def _respella_ingles(text):
    if not text or not _es_spanish(text):
        return text
    def rep(m):
        key = m.group(0).lower()
        return _EN_LOAN.get(key, m.group(0))
    patt = "|".join(sorted(map(re.escape, _EN_LOAN), key=len, reverse=True))
    return re.sub(r"\b(" + patt + r")\b", rep, text, flags=re.IGNORECASE)



def _ancla_palabra_aislada(text):
    s = (text or "").strip()
    if not s:
        return text
    # Solo si es una palabra única (sin espacios, saltos de línea, puntuación)
    if re.search(r"[\s\n\r]", s):
        return text
    if re.search(r"[.,;:!?¿¡]", s):
        return text
    # Ya tiene artículo previo
    if re.match(r"^(el|la|los|las|un|una|unos|unas)\b", s, re.IGNORECASE):
        return text
    # Es palabra aislada, agregar ancla
    # Plural si termina en 's' (pero no solo 's')
    if s.endswith("s") and len(s) > 1 and not s.endswith("ss"):
        return "Los " + s
    else:
        return "El " + s


def normalize_for_tts(text: str, guard: bool = False) -> str:
    if not text:
        return text
    text = text.replace("*", "").replace("#", "")
    text = re.sub(r"\b[Ee]lige\b", "elije", text)
    text = _acentua_mayusculas_es(text)
    text = _ancla_palabra_aislada(text)
    text = _ancla_es_mixta(text)
    text = _respella_ingles(text)
    text = re.sub(r"([.!?])\s+elije\b", ", elije", text)
    if guard:
        text = _protege_homografos(text)
    text = EMOJI_RESTO.sub(" ", text)
    text = _libera_ingles_encerrado(text)
    text = _polish(text)
    text = re.sub(
        r"(\b\d{1,3}(?:\.\d{3})+(?:,\d+)?\b|\b\d+(?:[.,]\d+)?)\s*%",
        lambda m: _num_match(m.group(1)) + " por ciento",
        text,
    )
    text = re.sub(r"\s*%", "", text)
    text = re.sub(NUM_PAT, _num_match, text)
    return text
