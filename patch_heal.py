from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")
log = []

if "def _repair_engine" not in t:
    anchor = "def _on_lang_changed(self):"
    add = '''def _repair_engine(self):
    import sys, os
    if getattr(self, "_repair_tried", False):
        return
    base = os.path.dirname(sys.executable) if getattr(
        sys, "frozen", False) else os.getcwd()
    inst = os.path.join(base, "engine", "Installer.exe")
    if not os.path.exists(inst):
        return
    self._repair_tried = True
    import ctypes
    ret = ctypes.windll.shell32.ShellExecuteW(
        None, "runas", inst,
        "/VERYSILENT /SUPPRESSMSGBOXES /NORESTART", None, 0)
    if ret > 32:
        from PySide6.QtCore import QTimer
        self.statusBar().showMessage("Reparando motor de voces...")
        QTimer.singleShot(5000, self._load_voices)


'''
    if anchor in t:
        t = t.replace(anchor, add + anchor, 1)
        log.append("repair engine")

old = """        self._voices = voices
        self._refill_combo()"""
new = """        self._voices = voices
        if not any(self._is_premium(v) for v in voices):
            self._repair_engine()
        self._refill_combo()"""
if old in t and "_repair_engine()" not in t.split("_refill_combo")[0]:
    t = t.replace(old, new, 1)
    log.append("check premium")

if "MainWindow._repair_engine = _repair_engine" not in t:
    t += "\nMainWindow._repair_engine = _repair_engine\n"

p.write_text(t, encoding="utf-8", newline="\n")
print("SELF-HEAL:", log)
try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as ex:
    print("ERROR:", ex.lineno, ex.msg)
