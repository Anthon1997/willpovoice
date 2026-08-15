from pathlib import Path
import re, ast

# ---- 1. core/text_normalizer.py ----
Path("core/text_normalizer.py").write_text(r'''from __future__ import annotations

import re

UNIDADES = [
    "", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho",
    "nueve", "diez", "once", "doce", "trece", "catorce", "quince",
    "dieciseis", "diecisiete", "dieciocho", "diecinueve", "veinte",
    "veintiuno", "veintidos", "veintitres", "veinticuatro", "veinticinco",
    "veintiseis", "veintisiete", "veintiocho", "veintinueve",
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
        out = "un millon" if m == 1 else _menos_millon(m) + " millones"
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


def normalize_for_tts(text: str) -> str:
    if not text:
        return text
    text = re.sub(
        r"(\b\d{1,3}(?:\.\d{3})+(?:,\d+)?\b|\b\d+(?:[.,]\d+)?)\s*%",
        lambda m: _num_match(m.group(1)) + " por ciento",
        text,
    )
    text = re.sub(NUM_PAT, _num_match, text)
    return text
''', encoding="utf-8")
print("1. core/text_normalizer.py creado.")

# ---- 2. Reproduccion: normalizar en speak_async ----
p = Path("core/tts_engine.py")
t = p.read_text(encoding="utf-8")
old = """        self.logger.info("Reproduciendo texto de forma asincrona.")
        self.adapter.speak(text, asynchronous=True)"""
old2 = """        self.logger.info("Reproduciendo texto de forma asíncrona.")
        self.adapter.speak(text, asynchronous=True)"""
new = """        self.logger.info("Reproduciendo texto de forma asíncrona.")
        from core.text_normalizer import normalize_for_tts
        text = normalize_for_tts(text)
        self.adapter.speak(text, asynchronous=True)"""
if old2 in t:
    t = t.replace(old2, new, 1)
    print("2. speak_async normaliza numeros a espanol.")
elif old in t:
    t = t.replace(old, new, 1)
    print("2. speak_async normaliza numeros a espanol.")
p.write_text(t, encoding="utf-8")

# ---- 3. Exportacion: normalizar en ExportWorker ----
pm = Path("ui/main_window.py")
mt = pm.read_text(encoding="utf-8")
pat = re.compile(r"([ \t]*)chunks = self\._split_chunks\(self\.text\)")
mt, n = pat.subn(
    lambda m: m.group(1) + "from core.text_normalizer import normalize_for_tts\n"
    + m.group(1) + "chunks = self._split_chunks(normalize_for_tts(self.text))",
    mt,
)
print(f"3. ExportWorker normaliza ({n} sitio(s)).")
pm.write_text(mt, encoding="utf-8")

try:
    ast.parse(mt)
    print("main_window SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
