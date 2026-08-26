from pathlib import Path
import ast
import re

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")

# 1) Detectar todos los attaches sin def
names = re.findall(r"^MainWindow\.(\w+) = \1$", t, flags=re.M)
missing = [n for n in names if f"def {n}(" not in t]
print("missing:", missing)

bodies = {
"_configure_groq_key": '''def _configure_groq_key(self):
    self._switch_page(5)
    vis = self._chat_banner.isVisible()
    self._chat_banner.setVisible(not vis)
    if not vis:
        try:
            self._groq_key_input.setFocus()
        except Exception:
            pass


''',
"_save_groq_key": '''def _save_groq_key(self):
    from PySide6.QtCore import QSettings
    key = self._groq_key_input.text().strip()
    if not key:
        self.statusBar().showMessage("Ingresa tu API Key de Groq", 3000)
        return
    s = QSettings("WillpoVoice", "WillpoVoice")
    s.setValue("groq_api_key", key)
    try:
        import os
        os.environ["GROQ_API_KEY"] = key
        from core import brain
        brain.GROQ_API_KEY = key
    except Exception:
        pass
    self._chat_banner.setVisible(False)
    self._set_chat_locked(False)
    self._add_chat_bubble(
        "API Key conectada. \\u00a1Listo para chatear!", is_user=False)
    self.statusBar().showMessage("API Key de Groq conectada", 4000)


''',
"_delete_groq_key": '''def _delete_groq_key(self):
    from PySide6.QtCore import QSettings
    s = QSettings("WillpoVoice", "WillpoVoice")
    s.remove("groq_api_key")
    try:
        self._groq_key_input.clear()
    except Exception:
        pass
    self._set_chat_locked(True)
    self._chat_banner.setVisible(True)
    self._add_chat_bubble(
        "API Key eliminada. Configura una nueva cuando quieras.",
        is_user=False)


''',
}

if missing:
    anchor = f"MainWindow.{missing[0]} = {missing[0]}"
    i = t.find(anchor)
    code = "".join(bodies.get(n, f"# TODO: def {n} faltante\\n")
                   for n in missing)
    t = t[:i] + code + t[i:]

# 2) Inyeccion de key desde QSettings en cada llamada del worker
old_w = ("            from core import brain\n"
         "            resp = brain.pensar(self._texto, self._historial, self._modo)")
new_w = ("            from core import brain\n"
         "            try:\n"
         "                from PySide6.QtCore import QSettings\n"
         "                _k = QSettings(\"WillpoVoice\", \"WillpoVoice\").value(\n"
         "                    \"groq_api_key\", \"\")\n"
         "                if _k:\n"
         "                    brain.GROQ_API_KEY = _k\n"
         "            except Exception:\n"
         "                pass\n"
         "            resp = brain.pensar(self._texto, self._historial, self._modo)")
if old_w in t:
    t = t.replace(old_w, new_w, 1)
    print("key inyectada en worker")

mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
print("OK reconstruccion de attaches")
