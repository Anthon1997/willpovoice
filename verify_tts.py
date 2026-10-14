from pathlib import Path
import re
for f in ["ui/modern_window.py", "core/tts_engine.py", "core/engine.py", "core/sapi_engine.py"]:
    p = Path(f)
    if not p.exists():
        continue
    src = p.read_text(encoding="utf-8")
    print("##### ", f)
    for m in re.finditer(r"def (speak|synthesize|convert|text_to_\w+|save_\w+)\([^)]*\):", src):
        ln = src[:m.start()].count("\n")+1
        print("  L", ln, m.group(0))
import os
print("\ncore files:", os.listdir("core"))
