from pathlib import Path
import re

p = Path("core/brain.py")
t = p.read_text(encoding="utf-8")

# Reemplazar la línea de la key con una que prioriza el valor hardcodeado
# Formato objetivo: GROQ_API_KEY = "gsk_..." or os.getenv("GROQ_API_KEY", "")
old_pattern = r'GROQ_API_KEY\s*=\s*os\.getenv\("GROQ_API_KEY",\s*"[^"]*"\)'
new_line = 'GROQ_API_KEY = "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" or os.getenv("GROQ_API_KEY", "")'

count = len(re.findall(old_pattern, t))
print(f"Líneas GROQ_API_KEY encontradas: {count}")

t = re.sub(old_pattern, new_line, t)
p.write_text(t, encoding="utf-8", newline="\n")

# Verificar
verif = Path("core/brain.py").read_text(encoding="utf-8")
for line in verif.splitlines():
    if "GROQ_API_KEY" in line and not line.strip().startswith("#"):
        print(f"  ✓ {line[:100]}")
