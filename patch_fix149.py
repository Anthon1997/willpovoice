from pathlib import Path
import re, ast

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

# ---- 1. RECOPILACION ----
print("resize(950, 650) count:", t.count("self.resize(950, 650)"))
print("dialog.exec() count:", t.count("dialog.exec()"))

# ---- 2. Helper de centrado en pantalla ----
if "def _center_on_screen" not in t:
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
    # Insertar antes de _resource_path
    if "@staticmethod" in t:
        i = t.find("@staticmethod")
        t = t[:i] + helper + t[i:]
        print("2. Helper _center_on_screen agregado.")

# ---- 3. Centrar MainWindow al final del __init__ ----
old_init = """        self.resize(950, 650)

    @staticmethod
    def _resource_path"""
new_init = """        self.resize(950, 650)
        self._center_on_screen(self)

    @staticmethod
    def _resource_path"""
if old_init in t:
    t = t.replace(old_init, new_init, 1)
    print("3. MainWindow centrado en pantalla al arrancar.")

# ---- 4. Licencia: flags + centrado + raise ----
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
if old_check in t:
    t = t.replace(old_check, new_check, 1)
    print("4. Dialogo de licencia centrado + al frente.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)

# ---- 5. Aplicar lo mismo a modern_window si existe ----
mp = Path("ui/modern_window.py")
if mp.exists():
    mt = mp.read_text(encoding="utf-8")
    print("=== modern_window ===")
    print("resize(950, 650):", mt.count("self.resize(950, 650)"))
    print("dialog.exec():", mt.count("dialog.exec()"))
    print("_check_license:", "_check_license" in mt)
