from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")
log = []

old_def = '''def _deferred_license(self):
    try:
        from PySide6.QtCore import QSettings
        _s = QSettings("WillpoVoice", "WillpoVoice")
        if str(_s.value("lic_dialog_ack", "0")) in ("1", "true", "True"):
            return
        _s.setValue("lic_dialog_ack", "1")
    except Exception:
        pass
    if not self._check_license():
        self.close()'''

new_def = '''def _deferred_license(self):
    ack = False
    try:
        from PySide6.QtCore import QSettings
        _s = QSettings("WillpoVoice", "WillpoVoice")
        ack = str(_s.value("lic_dialog_ack", "0")) in ("1", "true", "True")
        if not ack:
            _s.setValue("lic_dialog_ack", "1")
    except Exception:
        pass
    self._suppress_license_dialog = ack
    if not self._check_license():
        self.close()'''

if old_def in t:
    t = t.replace(old_def, new_def, 1)
    log.append("deferred sin return temprano")

old_lic = '''    if state == "licensed":
        self.license_label.setText("Version licenciada.")
        self.statusBar().showMessage("Version licenciada.")
        return True
    dialog = LicenseDialog('''

new_lic = '''    if state == "licensed":
        self.license_label.setText("Version licenciada.")
        self.statusBar().showMessage("Version licenciada.")
        return True
    if getattr(self, "_suppress_license_dialog", False) and state == "trial":
        return True
    dialog = LicenseDialog('''

if old_lic in t:
    t = t.replace(old_lic, new_lic, 1)
    log.append("dialogo suprimido solo en trial")

mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
print("OK", log)
