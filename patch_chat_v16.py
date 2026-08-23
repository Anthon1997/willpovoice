from pathlib import Path
import ast

# ============ 1) brain.py: MODE_PROMPTS + parametro modo ============
bp = Path("core/brain.py")
b = bp.read_text(encoding="utf-8-sig")
log = []

# Diccionario de modos extensos
if "MODE_PROMPTS" not in b:
    i = b.find("_MODELOS = [")
    modes = '''MODE_PROMPTS = {
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

'''
    b = b[:i] + modes + b[i:]
    log.append("MODE_PROMPTS")

# Firma con modo
old_sig = "def pensar(texto_usuario: str, historial=None) -> str:"
new_sig = "def pensar(texto_usuario: str, historial=None, modo=None) -> str:"
if old_sig in b:
    b = b.replace(old_sig, new_sig, 1); log.append("firma modo")

# Inyectar mensaje de modo tras el system prompt
old_msg = '    messages = [{"role": "system", "content": SYSTEM_PROMPT}]'
new_msg = ('''    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if modo and modo in MODE_PROMPTS:
        messages.append({"role": "system", "content": MODE_PROMPTS[modo]})''')
if old_msg in b and "MODE_PROMPTS[modo]" not in b:
    b = b.replace(old_msg, new_msg, 1); log.append("mensaje de modo")

# Creatividad alta en modo extenso
if "temperature=0.7," in b:
    b = b.replace("temperature=0.7,", "temperature=0.9 if modo else 0.7,", 1)
    log.append("temperatura dinamica")

bp.write_text(b, encoding="utf-8", newline="\n")

# ============ 2) modern_window: pasar modo al worker ============
mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")

old_init = '''    def __init__(self, texto, historial=None):
        super().__init__()
        self._texto = texto
        self._historial = historial or []

    def run(self):
        try:
            from core import brain
            resp = brain.pensar(self._texto, self._historial)'''
new_init = '''    def __init__(self, texto, historial=None, modo=None):
        super().__init__()
        self._texto = texto
        self._historial = historial or []
        self._modo = modo

    def run(self):
        try:
            from core import brain
            resp = brain.pensar(self._texto, self._historial, self._modo)'''
if old_init in t:
    t = t.replace(old_init, new_init, 1); log.append("worker modo")

old_wk = "        worker = _ChatWorker(text, hist)"
new_wk = "        worker = _ChatWorker(text, hist, getattr(self, \"_chat_mode\", None))"
if old_wk in t:
    t = t.replace(old_wk, new_wk, 1); log.append("send modo")

old_chip = "    self._add_chat_bubble(label, is_user=True)"
new_chip = "    self._add_chat_bubble(label, is_user=True)\n    self._chat_mode = label"
if old_chip in t and "_chat_mode = label" not in t:
    t = t.replace(old_chip, new_chip, 1); log.append("chip activa modo")

mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
print("OK", log)
