from pathlib import Path
import ast

p = Path("core/brain.py")
t = p.read_text(encoding="utf-8-sig")

# Diagnostico
for ln in t.splitlines():
    if ln.startswith("def pensar") or "MODE_PROMPTS = {" in ln or "_MODELOS = [" in ln:
        print("  >", ln.strip()[:70])

# 1) MODE_PROMPTS garantizado
if "MODE_PROMPTS = {" not in t and "_MODELOS = [" in t:
    i = t.find("_MODELOS = [")
    t = t[:i] + '''MODE_PROMPTS = {
    "Crear un guion / historia": (
        "MODO EXTENSO ACTIVADO: flujo de guiones e historias. Ignora el "
        "limite de 3 o 4 frases. Entrega hasta 5000 caracteres con gancho, "
        "desarrollo, climax y cierre. Narracion continua para TTS: sin "
        "markdown ni emojis."),
    "Analizar guion y mejorar": (
        "MODO EXTENSO ACTIVADO: flujo de mejora de guiones. Explica en 2 "
        "frases que mejoraste y entrega la version mejorada completa de "
        "hasta 5000 caracteres en narracion continua para TTS."),
    "Crear anuncios publicitarios": (
        "MODO EXTENSO ACTIVADO: flujo de anuncios. Con los datos del usuario "
        "crea un anuncio completo de hasta 5000 caracteres: gancho "
        "emocional, presentacion, beneficios, escena que conecte, oferta "
        "con precio y llamado a la accion. Narracion continua para TTS."),
}

''' + t[i:]
    print("MODE_PROMPTS agregado")

# 2) Reescribir pensar() completa (region entre def pensar y def pensar_y_hablar)
i = t.find("def pensar(")
j = t.find("\ndef pensar_y_hablar")
if i == -1 or j == -1:
    raise SystemExit("ERROR: region pensar no encontrada")

new_fn = '''def pensar(texto_usuario, historial=None, modo=None):
    """Pregunta a Groq con historial y modo extenso opcional."""
    texto = (texto_usuario or "").strip()
    if not texto:
        return "No escuché nada. ¿Podrías repetirme tu pregunta?"

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if modo and modo in MODE_PROMPTS:
        messages.append({"role": "system", "content": MODE_PROMPTS[modo]})
    if historial:
        messages.extend(historial[-12:])
    messages.append({"role": "user", "content": texto})

    ultimo_error = None
    for modelo in _MODELOS:
        try:
            client = _get_client()
            response = client.chat.completions.create(
                model=modelo,
                messages=messages,
                temperature=0.9 if modo else 0.7,
                max_tokens=8192,
                top_p=1,
                stream=False,
            )
            msg = response.choices[0].message
            content = msg.content
            if not content:
                content = getattr(msg, "reasoning", None) or (
                    "No pude generar una respuesta completa. "
                    "Intenta pedirmelo de nuevo.")
            return content.strip()
        except Exception as exc:
            ultimo_error = exc
            continue
    return f"Error de conexión con la IA: {ultimo_error}"
'''
t = t[:i] + new_fn + t[j + 1:]
p.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
assert "def pensar(texto_usuario, historial=None, modo=None):" in t
print("OK: pensar() reescrita con historial + modo")
