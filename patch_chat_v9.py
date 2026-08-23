from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")
log = []
print("ChatWorker presente:", "class _ChatWorker" in t)

# ============ 1) Re-inyectar _ChatWorker si falta ============
if "class _ChatWorker" not in t:
    i = t.find("def _send_chat_message(self):")
    if i == -1:
        raise SystemExit("ERROR: _send_chat_message no encontrado")
    worker = '''from PySide6.QtCore import QThread as _QThread, Signal as _ChatSignal


class _ChatWorker(_QThread):
    resultado = _ChatSignal(str)

    def __init__(self, texto):
        super().__init__()
        self._texto = texto

    def run(self):
        try:
            from core import brain
            resp = brain.pensar(self._texto)
        except Exception as exc:
            resp = f"Error de conexion con la IA: {exc}"
        self.resultado.emit(resp)


'''
    t = t[:i] + worker + t[i:]
    log.append("ChatWorker re-inyectado")

# ============ 2) Bloquear input hasta tener key ============
anchor_bar = "    p5.addWidget(bar)"
if "self._chat_send_btn = btn_send" not in t and anchor_bar in t:
    i = t.find(anchor_bar) + len(anchor_bar)
    lock_init = '''
    self._chat_send_btn = btn_send
    from PySide6.QtCore import QSettings as _QS
    _has_key = bool(_QS("WillpoVoice", "WillpoVoice").value("groq_api_key", ""))
    self._set_chat_locked(not _has_key)'''
    t = t[:i] + lock_init + t[i:]
    log.append("lock init")

# ============ 3) Metodo _set_chat_locked ============
anchor_att = "MainWindow._save_groq_key = _save_groq_key"
if "def _set_chat_locked" not in t and anchor_att in t:
    i = t.find(anchor_att)
    fn = '''def _set_chat_locked(self, locked):
    try:
        self._chat_input.setEnabled(not locked)
        self._chat_send_btn.setEnabled(not locked)
        self._chat_input.setPlaceholderText(
            "Configura tu API Key para empezar..." if locked
            else "Escribe tu pregunta...")
        self._chat_send_btn.setStyleSheet(
            "QPushButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            " stop:0 #8d75ff, stop:1 #6d5df0); border: none;"
            " border-radius: 12px; }"
            " QPushButton:hover { background: #9d87ff; }"
            " QPushButton:disabled { background: #232c47; }")
        self._chat_input.setStyleSheet(
            "QLineEdit { background: transparent; border: none;"
            " color: #e6edf3; font-size: 13px; padding: 0 6px; }"
            " QLineEdit:disabled { color: #55618a; }")
    except Exception:
        pass


MainWindow._set_chat_locked = _set_chat_locked
'''
    t = t[:i] + fn + t[i:]
    log.append("_set_chat_locked")

# ============ 4) Desbloquear al guardar key ============
old_save = "    self._chat_banner.setVisible(False)\n    self._add_chat_bubble("
new_save = ("    self._chat_banner.setVisible(False)\n"
            "    self._set_chat_locked(False)\n"
            "    self._add_chat_bubble(")
if old_save in t and "self._set_chat_locked(False)" not in t.split("def _save_groq_key")[1].split("def _toggle_key_vis")[0]:
    t = t.replace(old_save, new_save, 1)
    log.append("unlock al guardar")

mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
assert "class _ChatWorker" in t
assert "MainWindow._set_chat_locked = _set_chat_locked" in t
print("OK", log)
