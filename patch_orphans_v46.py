from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")
log = []

extra = ""

if not any(l.startswith("class _ChatWorker") for l in t.splitlines()):
    extra += '''
class _ChatWorker(QThread):
    resultado = Signal(str)

    def __init__(self, texto, historial=None, modo=None):
        super().__init__()
        self._texto = texto
        self._historial = historial or []
        self._modo = modo

    def run(self):
        try:
            from core import brain
            try:
                from PySide6.QtCore import QSettings
                _k = QSettings("WillpoVoice", "WillpoVoice").value(
                    "groq_api_key", "")
                if _k:
                    brain.GROQ_API_KEY = _k
            except Exception:
                pass
            resp = brain.pensar(self._texto, self._historial, self._modo)
        except Exception as exc:
            resp = f"Error de conexi\\u00f3n con la IA: {exc}"
        self.resultado.emit(resp)
'''
    log.append("_ChatWorker")

if not any(l.startswith("def _speak_head_icon(") for l in t.splitlines()):
    extra += '''
def _speak_head_icon(size=14):
    return _speak_head_svg(size)
'''
    log.append("_speak_head_icon")

if "_EYE_ON = " not in t:
    extra += '''
_EYE_ON = ("M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 "
           "11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 "
           "5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 "
           "3-1.34 3-3-1.34-3-3-3z")
_EYE_OFF = ("M12 7c2.76 0 5 2.24 5 5 0 .65-.13 1.26-.36 1.83l2.92 2.92c1.51-"
            "1.26 2.7-2.89 3.43-4.75-1.73-4.39-6-7.5-11-7.5-1.4 0-2.74.25-"
            "3.98.7l2.16 2.16C10.74 7.13 11.35 7 12 7zM2 4.27l2.28 2.28.46.46"
            "C3.08 8.3 1.78 10.02 1 12c1.73 4.39 6 7.5 11 7.5 1.55 0 3.03-.3"
            "4.38-.84l.42.42L19.73 22 21 20.73 3.27 3 2 4.27zM7.53 9.8l1.55"
            "1.55c-.05.21-.08.43-.08.65 0 1.66 1.34 3 3 3 .22 0 .44-.03.65-.08"
            "l1.55 1.55c-.67.37-1.43.59-2.2.59-2.76 0-5-2.24-5-5 0-.77.22-1.53"
            ".59-2.2z")
'''
    log.append("_EYE_ON/_EYE_OFF")

if extra:
    t = t.rstrip("\n") + "\n" + extra
    mw.write_text(t, encoding="utf-8", newline="\n")
    ast.parse(t)
    print("OK agregados:", log)
else:
    print("nada que agregar")
