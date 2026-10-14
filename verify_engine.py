from pathlib import Path
src = Path("core/tts_engine.py").read_text(encoding="utf-8")
print("LONG:", len(src))
import re
for m in re.finditer(r"def \w+\([^)]*\):", src):
    ln = src[:m.start()].count("\n")+1
    print("L", ln, ":", m.group(0))
