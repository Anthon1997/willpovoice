from pathlib import Path
import re
p = Path("core/brain.py")
t = p.read_text(encoding="utf-8")

# Reemplazar la línea rota por una limpia (clave hardcodeada)
line_rota = r'GROQ_API_KEY\s*=\s*os\.getenv\("[^"]*"\s*,\s*"[^"]*"\)'
line_nueva = 'GROQ_API_KEY = "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"'

new_t, n = re.subn(line_rota, line_nueva, t)
p.write_text(new_t, encoding="utf-8", newline="\n")

# Verificación
print(f"Líneas reemplazadas: {n}")
for i, l in enumerate(new_t.splitlines(), 1):
    if "GROQ_API_KEY" in l and not l.strip().startswith("#"):
        print(f"  L{i}: {l}")

assert n == 1, "no se encontró la línea rota"
assert '"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"' in new_t
print("✅ Fix aplicado")
