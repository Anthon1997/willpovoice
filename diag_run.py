import sys, traceback
from pathlib import Path
sys.path.insert(0, ".")

def excepthook(t, v, tb):
    msg = "".join(traceback.format_exception(t, v, tb))
    print("EXCEPCION NO CAPTURADA:")
    print(msg)
    Path("crash.log").write_text(msg, encoding="utf-8")
sys.excepthook = excepthook

from app.logger import setup_logging
setup_logging()
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import QTimer

try:
    from ui.modern_window import MainWindow
    print("UI CARGADA: modern_window")
except Exception as e:
    print("modern_window fallo:", type(e).__name__, e)
    from ui.main_window import MainWindow
    print("UI CARGADA: main_window (fallback)")

app = QApplication(sys.argv)
window = MainWindow()
window.show()

def inspect():
    print("=== INSPECCION a los 4s ===")
    print("visible:", window.isVisible(), "| tamano:", window.size().width(), "x", window.size().height())
    print("central:", window.centralWidget())
    kids = window.findChildren(QWidget)
    print("total widgets hijos:", len(kids))
    vis = [k for k in kids if k.isVisible()]
    print("hijos visibles:", len(vis))
    print("stylesheet ventana (chars):", len(window.styleSheet()))
    for k in kids[:12]:
        print("  -", type(k).__name__, repr(k.objectName()), "visible:", k.isVisible())

QTimer.singleShot(4000, inspect)
QTimer.singleShot(6000, app.quit)
sys.exit(app.exec())
