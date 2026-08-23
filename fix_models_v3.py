from pathlib import Path

p = Path("core/brain.py")
t = p.read_text(encoding="utf-8-sig")

old = '''_MODELOS = [
    "llama-3.3-70b-versatile",
    "qwen/qwen3-32b",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "meta-llama/llama-4-maverick-17b-128e-instruct",
    "openai/gpt-oss-20b",
]'''

new = '''_MODELOS = [
    "openai/gpt-oss-20b",
    "openai/gpt-oss-120b",
    "groq/compound",
    "groq/compound-mini",
]'''

if old in t:
    t = t.replace(old, new)
    p.write_text(t, encoding="utf-8", newline="\n")
    print("✅ Modelos optimizados para tu cuenta Groq")
else:
    print("AVISO: bloque no encontrado")
