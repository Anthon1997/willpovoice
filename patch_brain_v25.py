from pathlib import Path
import ast

p = Path("core/brain.py")
t = p.read_text(encoding="utf-8-sig")

# Marcadores actuales
for ln in t.splitlines():
    s = ln.strip()
    if s.startswith(("def ", "_MODELOS", "MODE_PROMPTS", "GROQ_API_KEY", "SYSTEM_PROMPT")):
        print("  >", s[:70])

# Auto-reparar _MODELOS si falta
if "_MODELOS = [" not in t:
    a = t.find("def _get_client")
    if a == -1:
        a = t.find("def pensar(")
    block = ('_MODELOS = [\n'
             '    "openai/gpt-oss-20b",\n'
             '    "openai/gpt-oss-120b",\n'
             '    "groq/compound",\n'
             '    "groq/compound-mini",\n'
             ']\n\n')
    t = t[:a] + block + t[a:]
    print("_MODELOS reinsertado")

p.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
assert "_MODELOS = [" in t
assert "def pensar(texto_usuario, historial=None, modo=None):" in t
print("OK brain.py completo")
