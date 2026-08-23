from pathlib import Path
import ast

# ============ 1) brain.py: modo extenso + fallback ============
bp = Path("core/brain.py")
b = bp.read_text(encoding="utf-8-sig")
log = []

i = b.find('SYSTEM_PROMPT = """')
j = b.find('"""', i + 20)
if i != -1 and j != -1:
    new_prompt = '''SYSTEM_PROMPT = """Eres Willpo, el asistente de inteligencia artificial de WillpoVoice, una aplicacion de texto a voz con voces neuronales premium.
Hablas siempre en espanol neutro latinoamericano, con tono amigable, calido y empatico.
MODO CONVERSACION (por defecto): respuestas de maximo 3 o 4 frases, cortas y claras, porque seran leidas en voz alta. Nada de markdown, emojis, listas ni asteriscos.
MODO EXTENSO (solo si el usuario pide explicitamente un guion, historia, cuento, ensayo, documento o texto largo): entrega hasta 8000 caracteres de contenido continuo, bien redactado y sin markdown.
Si te preguntan quien eres o que modelo eres: eres Willpo, el asistente de WillpoVoice, impulsado por IA de ultima generacion. Nunca digas que eres ChatGPT, GPT, Claude, Gemini ni Llama."""'''
    b = b[:i] + new_prompt + b[j + 3:]
    log.append("prompt modo extenso")

old_ret = '            return (response.choices[0].message.content or "").strip()'
new_ret = '''            msg = response.choices[0].message
            content = msg.content
            if not content:
                content = getattr(msg, "reasoning", None) or (
                    "No pude generar una respuesta completa. "
                    "Intenta pedirmelo de nuevo.")
            return content.strip()'''
if old_ret in b:
    b = b.replace(old_ret, new_ret, 1)
    log.append("fallback contenido")

old_max = "max_tokens=180"
if old_max in b:
    b = b.replace(old_max, "max_tokens=8192")
    log.append("techo 8192 tokens")

bp.write_text(b, encoding="utf-8", newline="\n")

# ============ 2) modern_window: ocultar tarjeta si hay key ============
mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")

anchor_b = "    p5.addWidget(self._chat_banner)"
hide = '''    p5.addWidget(self._chat_banner)
    from PySide6.QtCore import QSettings as _QSb
    if _QSb("WillpoVoice", "WillpoVoice").value("groq_api_key", ""):
        self._chat_banner.setVisible(False)'''
if anchor_b in t and "_QSb" not in t:
    t = t.replace(anchor_b, hide, 1)
    log.append("tarjeta oculta con key")

# ============ 3) Solo hablar respuestas cortas ============
old_speak = "    if ad is not None:\n        try:\n            ad.speak(response)"
new_speak = ("    if ad is not None and len(response or \"\") <= 500:\n"
             "        try:\n            ad.speak(response)")
if old_speak in t:
    t = t.replace(old_speak, new_speak, 1)
    log.append("habla solo <=500 chars")

mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
print("OK", log)
