from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")

anchor = "MainWindow._send_chat_message = _send_chat_message"
if "def _send_chat_message(self):" not in t and anchor in t:
    i = t.find(anchor)
    fn = '''def _send_chat_message(self):
    text = self._chat_input.text().strip()
    if not text:
        return
    self._add_chat_bubble(text, is_user=True)
    self._chat_input.clear()
    if not hasattr(self, "_chat_history"):
        self._chat_history = []
    hist = list(self._chat_history)
    self._chat_history.append({"role": "user", "content": text})
    try:
        thinking = self._add_chat_bubble(
            "Pensando...", is_user=False, temp=True)
        worker = _ChatWorker(text, hist, getattr(self, "_chat_mode", None))
        worker.resultado.connect(
            lambda r, tb=thinking: self._on_chat_response(r, tb))
        if not hasattr(self, "_chat_workers"):
            self._chat_workers = []
        self._chat_workers.append(worker)
        worker.finished.connect(
            lambda w=worker: self._chat_workers.remove(w)
            if w in self._chat_workers else None)
        worker.start()
    except Exception as exc:
        self._add_chat_bubble(f"Error al enviar: {exc}", is_user=False)


'''
    t = t[:i] + fn + t[i:]
    mw.write_text(t, encoding="utf-8", newline="\n")
    ast.parse(t)
    print("OK: _send_chat_message reconstruido")
else:
    print("nada que hacer")
