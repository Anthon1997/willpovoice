from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")

s = t.find("def _speak_chat_text(self, txt):")
e = t.find("MainWindow._speak_chat_text = _speak_chat_text")
if s == -1 or e == -1:
    raise SystemExit("ERROR: _speak_chat_text no encontrado")
e += len("MainWindow._speak_chat_text = _speak_chat_text")

new_fn = '''def _speak_chat_text(self, txt):
    """Habla el texto con Seraphina por defecto (motor del app)."""
    eng = getattr(self, "engine", None)
    if eng is None:
        return
    try:
        ok = False
        try:
            ok = bool(eng.select_voice("Seraphina"))
        except Exception:
            ok = False
        if hasattr(eng, "speak_async"):
            eng.speak_async(txt)
        else:
            eng.speak(txt)
        self.statusBar().showMessage(
            "Hablando con Seraphina" if ok else "Hablando con voz actual",
            2500)
    except Exception as exc:
        print(f"TTS fallo: {exc}")


MainWindow._speak_chat_text = _speak_chat_text'''

t = t[:s] + new_fn + t[e:]
mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
print("OK: _speak_chat_text con engine + Seraphina")
