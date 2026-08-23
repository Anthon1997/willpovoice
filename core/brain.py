"""
Módulo Brain: el cerebro conversacional de WillpoVoice.
Usa Groq (Llama) para generar respuestas cortas y empáticas
en español neutro, optimizadas para ser leídas en voz alta.
"""
from __future__ import annotations

import os
import logging
from typing import Optional

logger = logging.getLogger("willpovoice.brain")

# API Key desde variable de entorno o configurar aquí
# Obtén tu key gratis en: https://console.groq.com/
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

SYSTEM_PROMPT = """Eres Willpo, el asistente de inteligencia artificial de WillpoVoice, una aplicacion de texto a voz con voces neuronales premium.
Hablas siempre en espanol neutro latinoamericano, con tono amigable, calido y empatico.
MODO CONVERSACION (por defecto): respuestas de maximo 3 o 4 frases, cortas y claras, porque seran leidas en voz alta. Nada de markdown, emojis, listas ni asteriscos.
MODO EXTENSO (solo si el usuario pide explicitamente un guion, historia, cuento, ensayo, documento o texto largo): entrega hasta 8000 caracteres de contenido continuo, bien redactado y sin markdown.
Si te preguntan quien eres o que modelo eres: eres Willpo, el asistente de WillpoVoice, impulsado por IA de ultima generacion. Nunca digas que eres ChatGPT, GPT, Claude, Gemini ni Llama."""

MODE_PROMPTS = {
    "Crear un guion / historia": (
        "MODO EXTENSO ACTIVADO: estas en el flujo de creacion de guiones e "
        "historias. Ignora el limite de 3 o 4 frases. Entrega guiones o "
        "historias COMPLETOS y PROFUNDIZADOS de hasta 5000 caracteres, con "
        "gancho inicial, desarrollo, climax y cierre emocional. Formato de "
        "narracion continua listo para texto a voz: sin markdown, sin "
        "emojis, sin acotaciones entre parentesis. Usa todos los detalles "
        "que el usuario te haya dado."),
    "Analizar guion y mejorar": (
        "MODO EXTENSO ACTIVADO: estas en el flujo de analisis y mejora de "
        "guiones. Ignora el limite de 3 o 4 frases. Primero explica en 2 "
        "frases que mejoraste, y luego entrega la version mejorada COMPLETA "
        "de hasta 5000 caracteres: mejor gancho, mejor ritmo, lenguaje mas "
        "emocional y cierre mas persuasivo. El guion va en narracion "
        "continua lista para texto a voz: sin markdown ni emojis."),
    "Crear anuncios publicitarios": (
        "MODO EXTENSO ACTIVADO: estas en el flujo de creacion de anuncios "
        "publicitarios. Ignora el limite de 3 o 4 frases. Con los datos del "
        "usuario (negocio, producto, precio) crea un anuncio COMPLETO y "
        "PROFUNDIZADO de hasta 5000 caracteres con esta estructura: gancho "
        "emocional, presentacion del negocio, beneficios clave, una escena "
        "o historia que conecte, oferta con precio, y llamado a la accion "
        "memorable. Narracion continua lista para texto a voz: sin markdown "
        "ni emojis. Tono persuasivo, calido y profesional."),
}

_MODELOS = [
    "openai/gpt-oss-20b",
    "openai/gpt-oss-120b",
    "groq/compound",
    "groq/compound-mini",
]


def _get_client():
    """Crea el cliente de Groq. Lanza ValueError si no hay key."""
    if not GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY no configurada. "
            "Obtén tu clave gratis en https://console.groq.com/ "
            "y ponla en la variable de entorno GROQ_API_KEY "
            "o en core/brain.py -> GROQ_API_KEY."
        )
    from groq import Groq  # import diferido: no rompe si no se usa
    return Groq(api_key=GROQ_API_KEY)


def pensar(texto_usuario: str, historial=None, modo=None) -> str:
    """
    Envía el texto del usuario a Groq y devuelve la respuesta corta.
    Prueba una cadena de modelos disponibles hasta que uno funcione.
    """
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
            logger.warning("Modelo %s fallo: %s", modelo, exc)
            continue

    logger.exception("Todos los modelos de Groq fallaron")
    return f"Error de conexión con la IA: {ultimo_error}"


def pensar_y_hablar(texto_del_usuario: str,
                    speak_fn: Optional[callable] = None) -> str:
    """
    Función principal:
      1) Pide a Groq una respuesta corta
      2) La imprime en consola
      3) Si se provee speak_fn(texto), la envía al motor SAPI
    Devuelve la respuesta (útil para la UI).
    """
    respuesta = pensar(texto_del_usuario)
    print(f"🧠 {respuesta}")

    # TODO: AQUI SE CONECTA EL MOTOR SAPI
    if speak_fn is not None:
        try:
            speak_fn(respuesta)
        except Exception as exc:
            logger.exception("Motor TTS falló al hablar la respuesta")
            print(f"⚠️ Motor TTS falló: {exc}")
    else:
        print(f"🔊 [Motor TTS debería decir: {respuesta}]")

    return respuesta


# ---------------- Bucle de chat en consola ----------------
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
