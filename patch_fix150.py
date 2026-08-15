from pathlib import Path
import re, ast

# ================= main_window.py =================
p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

# 1. Eliminar el bloque roto insertado
broken = re.search(
    r"[ \t]*@staticmethod\n    def _center_on_screen\(widget\):[\s\S]*?"
    r"widget\.move\(QPoint\(x, y\)\)\n\n",
    t,
)
if broken:
    t = t.replace(broken.group(0), "", 1)
    print("1. Bloque roto eliminado de main_window.")

# 2. Insertar helper correcto dentro de MainWindow
helper = '''    @staticmethod
    def _center_on_screen(widget):
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QPoint
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        geo = screen.availableGeometry()
        x = geo.x() + (geo.width() - widget.width()) // 2
        y = geo.y() + (geo.height() - widget.height()) // 2
        widget.move(QPoint(x, y))

'''
anchor = "    @staticmethod\n    def _resource_path"
if anchor in t and "def _center_on_screen" not in t:
    t = t.replace(anchor, helper + anchor, 1)
    print("2. Helper correcto en MainWindow.")

p.write_text(t, encoding="utf-8")
try:
    ast.parse(t)
    print("main_window SINTAXIS OK")
except SyntaxError as e:
    print("main_window ERROR:", e.lineno, e.msg)

# ================= modern_window.py =================
mp = Path("ui/modern_window.py")
mt = mp.read_text(encoding="utf-8")

# 3. Funcion de centrado + asignacion
if "def _center_on_screen" not in mt:
    mt += '''

def _center_on_screen(widget):
    from PySide6.QtWidgets import QApplication
    screen = QApplication.primaryScreen()
    if screen is None:
        return
    geo = screen.availableGeometry()
    x = geo.x() + (geo.width() - widget.width()) // 2
    y = geo.y() + (geo.height() - widget.height()) // 2
    widget.move(QPoint(x, y))


MainWindow._center_on_screen = staticmethod(_center_on_screen)
'''
    print("3. Centrado en modern_window.")

# 4. Centrar ventana una vez en showEvent
old_se = "def showEvent(self, event):\n    super().showEvent(event)"
new_se = """def showEvent(self, event):
    super().showEvent(event)
    if not getattr(self, "_centered_once", False):
        self._centered_once = True
        self._center_on_screen(self)"""
if old_se in mt and "_centered_once" not in mt.split("def showEvent")[1][:400]:
    mt = mt.replace(old_se, new_se, 1)
    print("4. Ventana centrada al mostrarse.")

# 5. Licencia visible en modern_window
old_check = """        dialog = LicenseDialog(
            self,
            license_manager.get_machine_id(),
            days_left if state == "trial" else -1,
        )
        dialog.exec()"""
new_check = """        dialog = LicenseDialog(
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
if old_check in mt:
    mt = mt.replace(old_check, new_check, 1)
    print("5. Licencia visible en modern_window.")

mp.write_text(mt, encoding="utf-8")
try:
    ast.parse(mt)
    print("modern_window SINTAXIS OK")
except SyntaxError as e:
    print("modern_window ERROR:", e.lineno, e.msg)
