from pathlib import Path
import re
p = Path("core/brain.py")
t = p.read_text(encoding="utf-8-sig")
t2, n = re.subn(r'GROQ_API_KEY = "gsk_[^"]*"',
                'GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")', t)
p.write_text(t2, encoding="utf-8", newline="\n")
print(f"key removida del codigo: {n} linea(s)")
