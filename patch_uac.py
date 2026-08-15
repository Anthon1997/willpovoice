from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

old = """    def install_and_quit(self, path):
        from PySide6.QtCore import QProcess
        from PySide6.QtWidgets import QApplication
        self.status.setText("Instalando... la app se cerrara.")
        QProcess.startDetached(
            path, ["/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART"])
        QApplication.quit()"""

new = """    def install_and_quit(self, path):
        import ctypes
        from PySide6.QtWidgets import QApplication
        self.status.setText("Instalando... la app se cerrara.")
        args = "/VERYSILENT /SUPPRESSMSGBOXES /NORESTART"
        ret = ctypes.windll.shell32.ShellExecuteW(
            None, "runas", path, args, None, 1)
        if ret > 32:
            QApplication.quit()
        else:
            self.status.setText("Instalacion cancelada por el usuario.")
            self.dl_btn.setEnabled(True)"""

if old in t:
    t = t.replace(old, new, 1)
    p.write_text(t, encoding="utf-8")
    print("install_and_quit ahora lanza el instalador con UAC.")
else:
    print("ANCLA no encontrada.")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
