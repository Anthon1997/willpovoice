"""
Módulo Brain: el cerebro conversacional de WillpoVoice.
Usa Groq (modelos abiertos) para generar respuestas en español
neutro, optimizadas para ser leídas en voz alta.
"""
from __future__ import annotations

import os
import logging

logger = logging.getLogger("willpovoice.brain")

# La API Key la pone CADA USUARIO (tarjeta de la UI o variable de entorno).
# NUNCA hardcodear claves aquí para releases públicos.
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

SYSTEM_PROMPT = """Eres Willpo, el asistente de inteligencia artificial de WillpoVoice, una aplicacion de texto a voz con voces neuronales premium.
Hablas siempre en espanol neutro latinoamericano, con tono amigable, calido y empatico.
MODO CONVERSACION (por defecto): respuestas de maximo 3 o 4 frases, cortas y claras, porque seran leidas en voz alta. Nada de markdown, emojis, listas ni asteriscos.
MODO EXTENSO (solo si el usuario pide explicitamente un guion, historia, cuento, ensayo, documento o texto largo): entrega hasta 5000 caracteres de contenido continuo, bien redactado y sin markdown.
Si te preguntan quien eres o que modelo eres: eres Willpo, el asistente de WillpoVoice, impulsado por IA de ultima generacion. Nunca digas que eres ChatGPT, GPT, Claude, Gemini ni Llama."""

MODE_PROMPTS = {
    "Crear un guion / historia": (
        "MODO EXTENSO ACTIVADO: flujo de guiones e historias. Ignora el "
        "limite de 3 o 4 frases. Entrega hasta 5000 caracteres con gancho, "
        "desarrollo, climax y cierre emocional. Narracion continua lista "
        "para TTS: sin markdown ni emojis. Usa los detalles del usuario."),
    "Analizar guion y mejorar": (
        "MODO EXTENSO ACTIVADO: flujo de mejora de guiones. Explica en 2 "
        "frases que mejoraste y entrega la version mejorada completa de "
        "hasta 5000 caracteres en narracion continua lista para TTS."),
    "Crear anuncios publicitarios": (
        "MODO EXTENSO ACTIVADO: flujo de anuncios. Con los datos del usuario "
        "crea un anuncio completo de hasta 5000 caracteres: gancho "
        "emocional, presentacion, beneficios, escena que conecte, oferta "
        "con precio y llamado a la accion. Narracion continua para TTS."),
}

_MODELOS = [
    "openai/gpt-oss-20b",
    "openai/gpt-oss-120b",
    "groq/compound",
    "groq/compound-mini",
]


def _get_client():
    if not GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY no configurada. Obtén tu clave gratis en "
            "https://console.groq.com/ y configúrala en el Chat IA.")
    from groq import Groq
    return Groq(api_key=GROQ_API_KEY)


def pensar(texto_usuario, historial=None, modo=None):
    """Pregunta a Groq con historial de contexto y modo extenso."""
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


def pensar_y_hablar(texto_del_usuario, speak_fn=None):
    respuesta = pensar(texto_del_usuario)
    print(f"🧠 {respuesta}")
    # TODO: AQUI SE CONECTA EL MOTOR SAPI
    if speak_fn is not None:
        try:
            speak_fn(respuesta)
        except Exception as exc:
            print(f"Motor TTS falló: {exc}")
    else:
        print(f"🔊 [Motor TTS debería decir: {respuesta}]")
    return respuesta


if __name__ == "__main__":
    print("=" * 60)
    print("WillpoVoice Brain — Modo Chat")
    print("=" * 60)
    print("Escribe 'salir' para terminar\n")
    try:
        while True:
            texto = input("👤 Tú: ").strip()
            if texto.lower() in ("salir", "exit", "quit"):
                print("👋 ¡Hasta luego!")
                break
            if not texto:
                continue
            pensar_y_hablar(texto)
    except KeyboardInterrupt:
        print("\n👋 ¡Hasta luego!")
