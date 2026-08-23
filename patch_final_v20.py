from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")
log = []

# ============ 1) Dialogo de licencia: solo primera vez ============
i = t.find("def _deferred_license(self):")
if i != -1 and "lic_dialog_ack" not in t:
    j = t.find("\n", i) + 1
    gate = '''    try:
        from PySide6.QtCore import QSettings
        _s = QSettings("WillpoVoice", "WillpoVoice")
        if str(_s.value("lic_dialog_ack", "0")) in ("1", "true", "True"):
            return
        _s.setValue("lic_dialog_ack", "1")
    except Exception:
        pass
'''
    t = t[:j] + gate + t[j:]
    log.append("licencia una vez")

# ============ 2) Multilingue Premium por defecto al abrir ============
anchor = "self._switch_page(0)"
if "startswith(\"Multiling\")" not in t and anchor in t:
    idx = t.find(anchor) + len(anchor)
    block = '''
    try:
        for _i in range(self.lang_combo.count()):
            if self.lang_combo.itemText(_i).startswith("Multiling"):
                self.lang_combo.setCurrentIndex(_i)
                break
        self._on_lang_changed()
    except Exception:
        pass'''
    t = t[:idx] + block + t[idx:]
    log.append("multilingue default")

mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
print("OK", log)
