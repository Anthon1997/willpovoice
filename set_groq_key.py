from pathlib import Path
key = input("🔑 Pega tu Groq API Key (la obtienes gratis en console.groq.com):\n> ").strip()
if not key:
    print("❌ Clave vacía"); raise SystemExit(1)
p = Path("core/brain.py")
t = p.read_text(encoding="utf-8")
import re
t = re.sub(r'GROQ_API_KEY = os\.getenv\("GROQ_API_KEY",\s*"[^"]*"\)',
           f'GROQ_API_KEY = os.getenv("GROQ_API_KEY", "{key}")', t)
p.write_text(t, encoding="utf-8", newline="\n")
print("✅ Clave guardada en core/brain.py")
