from pathlib import Path
import ast

# ---- 1. Capa de homografos en text_normalizer ----
p = Path("core/text_normalizer.py")
t = p.read_text(encoding="utf-8")

if "HOMOGRAFOS = {" not in t:
    bloque = '''HOMOGRAFOS = {
    "sale": "salee",
    "sales": "salees",
    "vacio": "vacioo",
    "vacío": "vacioo",
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


def _protege_homografos(text: str) -> str:
    for palabra, resp in HOMOGRAFOS.items():
        pat = re.compile(
            r"\\b" + re.escape(palabra) + r"\\b", re.IGNORECASE)
        def repl(m, resp=resp):
            orig = m.group(0)
            return resp.capitalize() if orig[0].isupper() else resp
        text = pat.sub(repl, text)
    return text


def needs_homograph_guard(voice_desc: str) -> bool:
    low = (voice_desc or "").lower()
    return "multilingual" in low and "spanish" not in low


'''
    anchor = t.find("def normalize_for_tts")
    if anchor != -1:
        t = t[:anchor] + bloque + t[anchor:]
        print("1. Capa de homografos agregada.")

old_sig = """def normalize_for_tts(text: str) -> str:
    if not text:
        return text
    for em, word in EMOJIS.items():"""
new_sig = """def normalize_for_tts(text: str, guard: bool = False) -> str:
    if not text:
        return text
    if guard:
        text = _protege_homografos(text)
    for em, word in EMOJIS.items():"""
if old_sig in t:
    t = t.replace(old_sig, new_sig, 1)
    print("2. normalize_for_tts acepta guard.")

p.write_text(t, encoding="utf-8")

# ---- 2. Reproduccion: guard segun la voz activa ----
pe = Path("core/tts_engine.py")
te = pe.read_text(encoding="utf-8")
old_sp = """        from core.text_normalizer import normalize_for_tts
        text = normalize_for_tts(text)
        self.adapter.speak(text, asynchronous=True)"""
new_sp = """        from core.text_normalizer import (
            needs_homograph_guard,
            normalize_for_tts,
        )
        desc = ""
        try:
            desc = self.adapter.sapi.Voice.GetDescription()
        except Exception:
            desc = ""
        text = normalize_for_tts(
            text, guard=needs_homograph_guard(desc))
        self.adapter.speak(text, asynchronous=True)"""
if old_sp in te:
    te = te.replace(old_sp, new_sp, 1)
    print("3. Reproduccion con guard por voz activa.")
pe.write_text(te, encoding="utf-8")

# ---- 3. Exportacion: guard segun voz elegida ----
pm = Path("ui/main_window.py")
mt = pm.read_text(encoding="utf-8")
old_ex = """        from core.text_normalizer import normalize_for_tts
        chunks = self._split_chunks(normalize_for_tts(self.text))"""
new_ex = """        from core.text_normalizer import (
            needs_homograph_guard,
            normalize_for_tts,
        )
        chunks = self._split_chunks(
            normalize_for_tts(
                self.text,
                guard=needs_homograph_guard(self.voice or ""),
            )
        )"""
if old_ex in mt:
    mt = mt.replace(old_ex, new_ex, 1)
    print("4. Exportacion con guard por voz elegida.")
pm.write_text(mt, encoding="utf-8")

try:
    ast.parse(mt)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
