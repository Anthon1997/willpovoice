# 1) Crear core/lang_segmenter.py
content = '''"""
Segmentador de idiomas para textos mixtos (español/inglés).
Genera SSML con tags <lang> para que las voces multilingüe
pronuncien cada segmento con el acento correcto.
"""
import re
from typing import List, Tuple


# Palabras comunes para detección
_ES_WORDS = {
    "el", "la", "los", "las", "de", "del", "que", "y", "en", "por", "para",
    "con", "una", "un", "es", "son", "está", "están", "como", "más", "pero",
    "sus", "le", "ya", "o", "este", "esta", "estos", "estas", "ese", "esa",
    "esos", "esas", "aquel", "aquella", "aquellos", "aquellas", "lo", "al",
    "si", "sin", "sobre", "entre", "hasta", "desde", "durante", "mientras",
    "cuando", "donde", "quien", "cuyo", "cuya", "cuyos", "cuyas",
}

_EN_WORDS = {
    "the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with",
    "by", "from", "up", "about", "into", "through", "during", "before",
    "after", "above", "below", "between", "under", "again", "further",
    "then", "once", "here", "there", "when", "where", "why", "how", "all",
    "any", "both", "each", "few", "more", "most", "other", "some", "such",
    "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very",
}


def _detect_segment_lang(text: str) -> str:
    """
    Detecta el idioma dominante de un segmento de texto.
    
    Retorna: "es", "en", o "mix" (si está equilibrado).
    """
    low = text.lower()
    
    # Caracteres especiales indican español
    if re.search(r"[¿¡ñáéíóúü]", low):
        return "es"
    
    # Contar palabras
    words = set(re.findall(r"\\b[a-z]+\\b", low))
    es_count = len(words & _ES_WORDS)
    en_count = len(words & _EN_WORDS)
    
    if es_count == 0 and en_count == 0:
        # Sin palabras reconocibles, usar contexto
        return "mix"
    
    total = es_count + en_count
    if total == 0:
        return "mix"
    
    es_ratio = es_count / total
    en_ratio = en_count / total
    
    if es_ratio > 0.6:
        return "es"
    elif en_ratio > 0.6:
        return "en"
    else:
        return "mix"


def segment_text(text: str) -> List[Tuple[str, str]]:
    """
    Segmenta el texto en partes según el idioma.
    
    Retorna: lista de (segmento, idioma) donde idioma es "es", "en", o "mix".
    
    Estrategia:
    - Dividir por oraciones (punto, !, ?)
    - Detectar idioma de cada oración
    - Fusionar oraciones consecutivas del mismo idioma
    """
    # Dividir por oraciones manteniendo el delimitador
    sentences = re.split(r"(?<=[.!?])\\s+", text)
    
    segments = []
    for sent in sentences:
        if not sent.strip():
            continue
        lang = _detect_segment_lang(sent)
        segments.append((sent, lang))
    
    # Fusionar segmentos consecutivos del mismo idioma
    merged = []
    for seg, lang in segments:
        if merged and merged[-1][1] == lang:
            merged[-1] = (merged[-1][0] + " " + seg, lang)
        else:
            merged.append((seg, lang))
    
    return merged


def wrap_ssml(segments: List[Tuple[str, str]], 
              default_lang: str = "es-ES",
              en_lang: str = "en-US") -> str:
    """
    Envuelve los segmentos en tags SSML <lang>.
    
    Args:
        segments: lista de (texto, idioma) de segment_text()
        default_lang: código de idioma por defecto (español)
        en_lang: código de idioma para inglés
    
    Retorna: texto SSML completo con tags <lang>.
    
    Ejemplo:
        [("Hello", "en"), ("hola", "es")]
        → "<lang xml:lang='en-US'>Hello</lang> <lang xml:lang='es-ES'>hola</lang>"
    """
    if not segments:
        return ""
    
    # Si todo es de un idioma, no envolver
    if len(segments) == 1 and segments[0][1] != "mix":
        return segments[0][0]
    
    # Si hay mezcla, envolver cada segmento
    parts = []
    for seg, lang in segments:
        if lang == "en":
            parts.append(f"<lang xml:lang='{en_lang}'>{_escape_xml(seg)}</lang>")
        elif lang == "es":
            parts.append(f"<lang xml:lang='{default_lang}'>{_escape_xml(seg)}</lang>")
        else:  # mix o no detectado, usar default
            parts.append(f"<lang xml:lang='{default_lang}'>{_escape_xml(seg)}</lang>")
    
    return " ".join(parts)


def _escape_xml(text: str) -> str:
    """Escapa caracteres especiales para XML."""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;"))


def is_mixed_language(text: str) -> bool:
    """
    Detecta si el texto contiene múltiples idiomas.
    
    Retorna True si hay segmentos de diferentes idiomas.
    """
    segments = segment_text(text)
    if len(segments) <= 1:
        return False
    
    langs = {lang for _, lang in segments if lang != "mix"}
    return len(langs) > 1
'''

from pathlib import Path
p = Path("core/lang_segmenter.py")
p.write_text(content, encoding="utf-8", newline="\n")
print("OK: core/lang_segmenter.py creado")
print("LONG:", len(content))
