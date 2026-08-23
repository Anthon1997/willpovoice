from pathlib import Path
import ast

# ============ 1) brain.py: pensar con historial ============
bp = Path("core/brain.py")
b = bp.read_text(encoding="utf-8-sig")
log = []

old_def = "def pensar(texto_usuario: str) -> str:"
new_def = "def pensar(texto_usuario: str, historial=None) -> str:"
if old_def in b:
    b = b.replace(old_def, new_def, 1); log.append("firma historial")

old_anchor = "    ultimo_error = None"
hist_block = ('''    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if historial:
        messages.extend(historial[-12:])
    messages.append({"role": "user", "content": texto})

    ultimo_error = None''')
if old_anchor in b and "messages = [{\"role\": \"system\"" not in b:
    b = b.replace(old_anchor, hist_block, 1); log.append("messages con historial")

old_msgs = '''                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": texto},
                ],'''
if old_msgs in b:
    b = b.replace(old_msgs, "                messages=messages,", 1)
    log.append("usa messages")

bp.write_text(b, encoding="utf-8", newline="\n")

# ============ 2) modern_window: memoria de conversacion ============
mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")

# Worker con historial
old_w = '''    def __init__(self, texto):
        super().__init__()
        self._texto = texto

    def run(self):
        try:
            from core import brain
            resp = brain.pensar(self._texto)'''
new_w = '''    def __init__(self, texto, historial=None):
        super().__init__()
        self._texto = texto
        self._historial = historial or []

    def run(self):
        try:
            from core import brain
            resp = brain.pensar(self._texto, self._historial)'''
if old_w in t:
    t = t.replace(old_w, new_w, 1); log.append("worker historial")

# _send_chat_message: capturar y guardar historial
old_send = '''        self._add_chat_bubble(text, is_user=True)
        self._chat_input.clear()
        thinking = self._add_chat_bubble(
            "Pensando...", is_user=False, temp=True)
        worker = _ChatWorker(text)'''
new_send = '''        self._add_chat_bubble(text, is_user=True)
        self._chat_input.clear()
        if not hasattr(self, "_chat_history"):
            self._chat_history = []
        hist = list(self._chat_history)
        self._chat_history.append({"role": "user", "content": text})
        thinking = self._add_chat_bubble(
            "Pensando...", is_user=False, temp=True)
        worker = _ChatWorker(text, hist)'''
if old_send in t:
    t = t.replace(old_send, new_send, 1); log.append("send historial")

# _on_chat_response: guardar respuesta IA
old_resp = '''    self._add_chat_bubble(response, is_user=False)
    ad = getattr(self, "adapter", None) or getattr(self, "sapi_adapter", None)'''
new_resp = '''    self._add_chat_bubble(response, is_user=False)
    if hasattr(self, "_chat_history"):
        self._chat_history.append(
            {"role": "assistant", "content": response})
    ad = getattr(self, "adapter", None) or getattr(self, "sapi_adapter", None)'''
if old_resp in t:
    t = t.replace(old_resp, new_resp, 1); log.append("resp historial")

# _on_chat_chip: los chips tambien dejan contexto
old_chip = "    self._add_chat_bubble(respuestas.get(label, \"\"), is_user=False)"
new_chip = '''    resp = respuestas.get(label, "")
    if not hasattr(self, "_chat_history"):
        self._chat_history = []
    self._chat_history.append({"role": "user", "content": label})
    self._chat_history.append({"role": "assistant", "content": resp})
    self._add_chat_bubble(resp, is_user=False)'''
if old_chip in t:
    t = t.replace(old_chip, new_chip, 1); log.append("chips historial")

mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
print("OK", log)
