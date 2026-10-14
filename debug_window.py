import sys
from app.logger import setup_logging
setup_logging()
from PySide6.QtWidgets import QApplication, QFrame
from PySide6.QtCore import QTimer
from ui.modern_window import MainWindow

app = QApplication(sys.argv)
w = MainWindow()
w.show()

def probe():
    bar = w.findChild(QFrame, "playerBar")
    print("effect:", bar.graphicsEffect())
    full = w.grab()
    full.save("window_grab.png")
    # posicion global de la barra dentro de la ventana
    tl = bar.mapTo(w, bar.rect().topLeft())
    print("bar top-left en ventana:", tl.x(), tl.y(), "w:", bar.width(), "h:", bar.height())
    img = full
    cx = tl.x() + bar.width()//2
    below = tl.y() + bar.height()
    print("muestreo columna x=", cx)
    for y in range(below-4, min(img.height(), below+26), 4):
        c = img.pixelColor(cx, y)
        print(" y", y, (c.red(), c.green(), c.blue()))
    # tambien a los lados
    for x in (tl.x()-8, tl.x()+bar.width()+8):
        c = img.pixelColor(max(0,min(img.width()-1,x)), tl.y()+bar.height()//2)
        print(" lado x", x, (c.red(), c.green(), c.blue()))
    QTimer.singleShot(200, app.quit)

QTimer.singleShot(1200, probe)
sys.exit(app.exec())
