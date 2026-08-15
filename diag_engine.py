from pathlib import Path
import re

print("=== archivos en core ===")
for f in sorted(Path("core").glob("*.py")):
    print(" -", f.name)

t = Path("core/tts_engine.py").read_text(encoding="utf-8")
print("=== metodos de tts_engine.py ===")
for m in re.finditer(r"def (\w+)", t):
    print("  def", m.group(1))

i = t.find("def speak_async")
if i != -1:
    print("=== speak_async ===")
    print(t[i:i + 1200])

i = t.find("def stop")
if i != -1:
    print("=== stop ===")
    print(t[i:i + 500])

print("=== Pause/Resume en core ===")
for f in Path("core").glob("*.py"):
    c = f.read_text(encoding="utf-8")
    for kw in ("Pause", "Resume", "pause", "resume"):
        if kw in c:
            print(f"{f.name}: contiene {kw!r}")
