from pathlib import Path
import re

# 1) SAPIAdapter
p = Path("adapters/sapi_adapter.py")
src = p.read_text(encoding="utf-8")
print("=== SAPIAdapter: metodos speak/XML ===")
for m in re.finditer(r"def (speak\w*|speak_xml|_say|_tts_xml)\([^)]*\):", src):
    ln = src[:m.start()].count("\n")+1
    print("L", ln, m.group(0))
    print(src[m.start():m.start()+700])
    print("-"*60)

print("\n=== menciones XML/SSML/lang ===")
for m in re.finditer(r".*(XML|xml|SSML|ssml|lang=|SpeakXml|SpeakComplete|OutputFormat).*", src):
    ln = src[:m.start()].count("\n")+1
    print(ln, ":", src.splitlines()[ln-1].strip())

# 2) _express_segments
q = Path("ui/modern_window.py")
t = q.read_text(encoding="utf-8")
i = t.find("def _express_segments")
print("\n=== _express_segments ===")
print(t[i:i+1200] if i>=0 else "NO")
