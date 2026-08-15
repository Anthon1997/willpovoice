from pathlib import Path
import re, ast

mp = Path("ui/modern_window.py")
mt = mp.read_text(encoding="utf-8")

# ---- 1. RECOPILACION ----
i = mt.find("def showEvent")
print("--- showEvent ---")
print(mt[i:i + 400])
j = mt.find("def _check_license")
print("--- _check_license ---")
print(mt[j:j + 600])

# ---- 2. Centrado en showEvent (indentacion 4) ----
old_se = "def showEvent(self, event):\n"
new_se = old_se + """    if not getattr(self, "_centered_once", False):
        self._centered_once = True
        self._center_on_screen(self)
"""
if "_centered_once" not in mt:
    mt = mt.replace(old_se, new_se, 1)
    print("2. Centrado en showEvent de modern.")

# ---- 3. Licencia visible (cuerpo a 4 espacios) ----
old_ck = re.search(
    r"    dialog = LicenseDialog\([\s\S]*?    dialog\.exec\(\)", mt)
if old_ck and "WindowStaysOnTopHint" not in mt:
    new_ck = """    dialog = LicenseDialog(
        self,
        license_manager.get_machine_id(),
        days_left if state == "trial" else -1,
    )
    dialog.setWindowFlags(
        dialog.windowFlags()
        | Qt.WindowType.WindowStaysOnTopHint
        | Qt.WindowType.Dialog
    )
    dialog.adjustSize()
    self._center_on_screen(dialog)
    dialog.show()
    dialog.raise_()
    dialog.activateWindow()
    dialog.exec()"""
    mt = mt.replace(old_ck.group(0), new_ck, 1)
    print("3. Licencia visible en modern.")

mp.write_text(mt, encoding="utf-8")

try:
    ast.parse(mt)
    print("modern_window SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
