from pathlib import Path
import re

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

t = t.replace(old_models, new_models)

# 2) Reescribir la funcion pensar con cadena de fallback
old_pensar = '''def pensar(texto_usuario: str) -> str:
    """
    Envía el texto del usuario a Groq y devuelve la respuesta corta.
    Maneja todos los errores y devuelve un mensaje amigable en español.
    """
    texto = (texto_usuario or "").strip()
    if not texto:
        return "No escuché nada. ¿Podrías repetirme tu pregunta?"

    try:
        client = _get_client()
        response = client.chat.completions.create(
            model=_MODELO_PRINCIPAL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": texto},
            ],
            temperature=0.7,
            max_tokens=180,   # Fuerza respuestas cortas
            top_p=1,
            stream=False,
        )
        return (response.choices[0].message.content or "").strip()
    except Exception as exc:
        msg = str(exc).lower()
        # Intentar con modelo fallback si el principal no tiene permiso
        if "permission" in msg or "does not have access" in msg or "404" in msg:
            try:
                client = _get_client()
                response = client.chat.completions.create(
                    model=_MODELO_FALLBACK,
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
            except Exception as exc2:
                logger.exception("Fallback Groq falló")
                return f"Error de conexión con la IA: {exc2}"
        logger.exception("Groq falló")
        return f"Error de conexión con la IA: {exc}"'''

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
            logger.warning(f"Modelo {modelo} falló: {exc}")
            continue

    logger.exception("Todos los modelos de Groq fallaron")
    return f"Error de conexión con la IA: {ultimo_error}"'''

t = t.replace(old_pensar, new_pensar)

p.write_text(t, encoding="utf-8", newline="\n")

import ast
ast.parse(t)
print("✅ Modelos actualizados + cadena de fallback")
print(f"  Modelos a probar: {[m for m in _MODELOS.split('\"')[1::2]][:5]}")
