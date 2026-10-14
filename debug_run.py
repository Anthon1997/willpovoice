import sys
from app.logger import setup_logging
setup_logging()
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from ui.modern_window import MainWindow

app = QApplication(sys.argv)
w = MainWindow()
w.show()

def probe():
    bar = w.findChild(type(w), "playerBar") or None
    from PySide6.QtWidgets import QFrame
    bar = w.findChild(QFrame, "playerBar")
    print("=== PROBE playerBar ===")
    print("LIGHT_MODE:", __import__("ui.modern_window", fromlist=["LIGHT_MODE"]).LIGHT_MODE)
    if bar is None:
        print("!! playerBar NO encontrado")
    else:
        eff = bar.graphicsEffect()
        print("widget:", bar, "objectName:", bar.objectName())
        print("rect:", bar.rect(), "visible:", bar.isVisible())
        print("parent:", bar.parentWidget().objectName() or type(bar.parentWidget()))
        print("graphicsEffect:", eff)
        if eff:
            print("  blur:", eff.blurRadius(), "offset:", eff.offset(), "color:", eff.color().getRgb())
        print("styleSheet:", bar.styleSheet()[:120])
        # capturas renderizadas
        try:
            bar.grab().save("player_widget.png")
            print("guardado player_widget.png")
        except Exception as e:
            print("grab widget fail:", e)
        try:
            pw = bar.parentWidget()
            pw.grab().save("player_parent.png")
            print("guardado player_parent.png (aqui se ve la sombra)")
        except Exception as e:
            print("grab parent fail:", e)
    QTimer.singleShot(200, app.quit)

QTimer.singleShot(1200, probe)
sys.exit(app.exec())
