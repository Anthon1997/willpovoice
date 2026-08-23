from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")
log = []

# ---------- 1) Fondo transparente (azul marino del app) ----------
old_bg = "    chat_widget = QWidget()\n    self._chat_layout = QVBoxLayout(chat_widget)"
new_bg = ('    chat_widget = QWidget()\n'
          '    chat_widget.setStyleSheet("background: transparent;")\n'
          '    self._chat_layout = QVBoxLayout(chat_widget)')
if old_bg in t:
    t = t.replace(old_bg, new_bg, 1); log.append("chat_widget transparente")

old_vp = "    self._chat_scroll.setWidget(chat_widget)"
new_vp = ('    self._chat_scroll.setWidget(chat_widget)\n'
          '    self._chat_scroll.viewport().setStyleSheet("background: transparent;")\n'
          '    page5.setStyleSheet("background: transparent;")')
if old_vp in t:
    t = t.replace(old_vp, new_vp, 1); log.append("viewport transparente")

# ---------- 2) Worker a nivel modulo + slot robusto ----------
old_send_start = "def _send_chat_message(self):"
old_send_end = "def _add_chat_bubble(self, text, is_user, temp=False):"
i = t.find(old_send_start)
j = t.find(old_send_end)
if i != -1 and j != -1:
    new_block = '''from PySide6.QtCore import QThread as _QThread, pyqtSignal as _pyqtSignal


class _ChatWorker(_QThread):
    finished = _pyqtSignal(str)

    def __init__(self, texto):
        super().__init__()
        self._texto = texto

    def run(self):
        try:
            from core import brain
            resp = brain.pensar(self._texto)
        except Exception as exc:
            resp = f"Error de conexion con la IA: {exc}"
        self.finished.emit(resp)


def _send_chat_message(self):
    import traceback
    try:
        text = self._chat_input.text().strip()
        if not text:
            return
        from PySide6.QtCore import QSettings
        settings = QSettings("WillpoVoice", "WillpoVoice")
        api_key = settings.value("groq_api_key", "")
        if not api_key:
            self._chat_banner.setVisible(True)
            return
        from core import brain
        brain.GROQ_API_KEY = api_key
        self._add_chat_bubble(text, is_user=True)
        self._chat_input.clear()
        thinking = self._add_chat_bubble(
            "Pensando...", is_user=False, temp=True)
        worker = _ChatWorker(text)
        self._chat_worker = worker
        worker.finished.connect(
            lambda r: self._on_chat_response(r, thinking))
        worker.start()
    except Exception as exc:
        traceback.print_exc()
        try:
            self._add_chat_bubble(f"Error al enviar: {exc}", is_user=False)
        except Exception:
            pass


'''
    t = t[:i] + new_block + t[j:]
    log.append("slot robusto + worker modulo")

# ---------- 3) _on_chat_response con adapter defensivo ----------
old_resp_start = "def _on_chat_response(self, response, temp_bubble):"
old_resp_end = "MainWindow._configure_groq_key = _configure_groq_key"
i = t.find(old_resp_start)
j = t.find(old_resp_end)
if i != -1 and j != -1:
    new_resp = '''def _on_chat_response(self, response, temp_bubble):
    if temp_bubble is not None:
        try:
            temp_bubble.setParent(None)
            temp_bubble.deleteLater()
        except Exception:
            pass
    self._add_chat_bubble(response, is_user=False)
    ad = getattr(self, "adapter", None) or getattr(self, "sapi_adapter", None)
    if ad is not None:
        try:
            ad.speak(response)
        except Exception as exc:
            print(f"TTS fallo: {exc}")


'''
    t = t[:i] + new_resp + t[j:]
    log.append("respuesta con adapter defensivo")

mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
print("OK", log)

# ---------- 4) Diagnostico de paginas ----------
import re
for m in re.finditer(r"page\d = QWidget\(\)|QVBoxLayout\(page\d\)|addWidget\(page\d\)", t):
    ln = t[:m.start()].count("\n") + 1
    print(f"  L{ln}: {m.group()}")
