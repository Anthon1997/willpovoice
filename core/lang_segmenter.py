"""
Segmentador ligero para textos mixtos español/inglés.

Objetivo:
- Si una frase tiene marca/nombre en inglés y luego texto español,
  forzar cada tramo con acento correcto usando XML/SAPI:
    <lang langid="409">English</lang>
    <lang langid="0C0A">Español</lang>
"""

import re
from typing import List, Tuple


# SAPI LANGID:
# 409  = en-US
# 0C0A = es-ES
EN_LANGID = "409"
ES_LANGID = "0C0A"


_ES_WORDS = {
    "el", "la", "los", "las", "de", "del", "que", "y", "en", "por", "para",
    "con", "una", "un", "es", "son", "esta", "este", "esto", "estos", "estas",
    "como", "más", "mas", "pero", "sin", "sobre", "entre", "hasta", "desde",
    "cuando", "donde", "quien", "qué", "que", "cómo", "como", "cuándo",
    "porque", "también", "tambien", "puedes", "puede", "hacer", "usar",
    "voz", "voces", "texto", "frase", "frases", "palabra", "palabras",
    "guion", "guión", "publicitario", "publicitaria", "publicidad",
    "escribe", "escucha", "elige", "elije", "reproduce", "exporta",
}

_EN_WORDS = {
    "the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with",
    "by", "from", "up", "about", "into", "through", "during", "before",
    "after", "hello", "hi", "welcome", "voice", "script", "advertising",
    "willpovoice",
}


def _words(text: str):
    return re.findall(r"\b[\wáéíóúüñÁÉÍÓÚÜÑ]+\b", text, flags=re.UNICODE)


def _detect_segment_lang(text: str) -> str:
    """
    Devuelve:
    - "es" para español
    - "en" para inglés/marca inglesa
    - "mix" si no está claro
    """
    raw = text.strip()
    low = raw.lower()

    if not raw:
        return "mix"

    # Caracteres inequívocos del español
    if re.search(r"[¿¡ñáéíóúü]", low):
        return "es"

    words = {w.lower() for w in _words(raw)}

    es_count = len(words & _ES_WORDS)
    en_count = len(words & _EN_WORDS)

    if es_count > en_count:
        return "es"
    if en_count > es_count:
        return "en"

    # Caso marca / acrónimo / nombre comercial en mayúsculas:
    # WILLPOVOICE, AI, TTS, etc.
    compact = re.sub(r"[^A-Za-z]", "", raw)
    if compact and compact.isupper() and len(compact) >= 2:
        return "en"

    # Si no hay señales claras, por defecto español
    # porque la app normalmente genera locución en español.
    return "es"


def _split_keep_context(text: str) -> List[str]:
    """
    Divide en unidades por:
    - saltos de oración
    - guiones largos/medios usados en titulares
    Conserva suficiente contexto sin romper demasiado.
    """
    text = text.strip()
    if not text:
        return []

    # Separar encabezados tipo:
    # WILLPOVOICE — GUION PUBLICITARIO
    chunks = []
    for part in re.split(r"\s+[—–-]\s+", text):
        part = part.strip()
        if not part:
            continue

        # Además dividir por oración normal.
        subs = re.split(r"(?<=[.!?])\s+", part)
        chunks.extend([s.strip() for s in subs if s.strip()])

    return chunks


def segment_text(text: str) -> List[Tuple[str, str]]:
    """
    Retorna lista de (segmento, idioma).
    """
    chunks = _split_keep_context(text)
    if not chunks:
        return []

    segments = []
    for c in chunks:
        lang = _detect_segment_lang(c)
        segments.append((c, lang))

    # Fusionar consecutivos del mismo idioma
    merged = []
    for seg, lang in segments:
        if merged and merged[-1][1] == lang:
            merged[-1] = (merged[-1][0] + " " + seg, lang)
        else:
            merged.append((seg, lang))

    return merged


def is_mixed_language(text: str) -> bool:
    segments = segment_text(text)
    langs = {lang for _, lang in segments if lang in ("es", "en")}
    return len(langs) > 1


def wrap_ssml(segments: List[Tuple[str, str]]) -> str:
    """
    Genera XML compatible con SAPI, NO SSML Azure completo.

    Ejemplo:
      <lang langid="409">WILLPOVOICE</lang>
      <lang langid="0C0A">GUION PUBLICITARIO</lang>
    """
    if not segments:
        return ""

    parts = []
    for seg, lang in segments:
        safe = _escape_xml(seg)
        if lang == "en":
            parts.append(f'<lang langid="{EN_LANGID}">{safe}</lang>')
        else:
            parts.append(f'<lang langid="{ES_LANGID}">{safe}</lang>')

    return " ".join(parts)


def _escape_xml(text: str) -> str:
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
    )
