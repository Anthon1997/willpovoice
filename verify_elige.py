from pathlib import Path
import re
t = "Escribe. Elige. Escucha."
t = t.replace("*","").replace("#","")
t = re.sub(r"\b[Ee]lige\b", lambda m: "Elije" if m.group(0)[0].isupper() else "elije", t)
print("regex directo:", repr(t))

from core.text_normalizer import normalize_for_tts
print("normalize_for_tts:", repr(normalize_for_tts("Escribe. Elige. Escucha. * #")))

src = Path("core/tts_engine.py").read_text(encoding="utf-8")
for m in re.finditer(r"def (speak|speak_async|_speak|synthesize)\([^)]*\):", src):
    ln = src[:m.start()].count("\n")+1
    print("\n=== tts_engine L", ln, m.group(0))
    print(src[m.start():m.start()+500])
