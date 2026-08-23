from pathlib import Path

p = Path("core/brain.py")
t = p.read_text(encoding="utf-8")

# 1) Reemplazar los modelos obsoletos por cadena actualizada
old_models = '''_MODELO_PRINCIPAL = "llama-3.3-70b-versatile"
_MODELO_FALLBACK  = "llama-3.1-8b-instant"'''

new_models = '''_MODELOS = [
    "llama-3.3-70b-versatile",
    "qwen/qwen3-32b",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "meta-llama/llama-4-maverick-17b-128e-instruct",
    "openai/gpt-oss-20b",
]'''

if old_models in t:
    t = t.replace(old_models, new_models)
    print("modelos reemplazados")
else:
    print("AVISO: bloque de modelos no encontrado (quizas ya aplicado)")

# 2) Reescribir la funcion pensar con cadena de fallback
old_start = "def pensar(texto_usuario: str) -> str:"
old_end = '        return f"Error de conexión con la IA: {exc}"'

i = t.find(old_start)
j = t.find(old_end)
if i != -1 and j != -1:
    j += len(old_end)
    new_pensar = '''def pensar(texto_usuario: str) -> str:
    """
    Envía el texto del usuario a Groq y devuelve la respuesta corta.
    Prueba una cadena de modelos disponibles hasta que uno funcione.
    """
    texto = (texto_usuario or "").strip()
    if not texto:
        return "No escuché nada. ¿Podrías repetirme tu pregunta?"

    ultimo_error = None
    for modelo in _MODELOS:
        try:
            client = _get_client()
            response = client.chat.completions.create(
                model=modelo,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": texto},
                ],
                temperature=0.7,
                max_tokens=180,
                top_p=1,
                stream=False,
            )
            return (response.choices[0].message.content or "").strip()
        except Exception as exc:
            ultimo_error = exc
            logger.warning("Modelo %s fallo: %s", modelo, exc)
            continue

    logger.exception("Todos los modelos de Groq fallaron")
    return f"Error de conexión con la IA: {ultimo_error}"'''
    t = t[:i] + new_pensar + t[j:]
    print("funcion pensar reescrita")
else:
    print("AVISO: funcion pensar no encontrada tal cual")

p.write_text(t, encoding="utf-8", newline="\n")

import ast
ast.parse(t)
assert "_MODELOS = [" in t
print("✅ SINTAXIS OK · cadena de 5 modelos lista")
