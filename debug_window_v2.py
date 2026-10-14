import sys
from app.logger import setup_logging
setup_logging()

from PySide6.QtWidgets import QApplication, QFrame
from PySide6.QtCore import QTimer
from ui.modern_window import MainWindow

app = QApplication(sys.argv)
w = MainWindow()
w.show()

def _rgb(img, x, y):
    x = max(0, min(img.width() - 1, int(x)))
    y = max(0, min(img.height() - 1, int(y)))
    c = img.pixelColor(x, y)
    return (c.red(), c.green(), c.blue(), c.alpha())

def probe():
    bar = w.findChild(QFrame, "playerBar")
    print("=== WINDOW PIPELINE PROBE ===")

    if bar is None:
        print("playerBar NO encontrado")
        QTimer.singleShot(200, app.quit)
        return

    eff = bar.graphicsEffect()
    print("effect:", eff)
    if eff:
        print("blur:", eff.blurRadius())
        print("offset:", eff.offset())
        print("color:", eff.color().getRgb())

    pix = w.grab()
    pix.save("window_grab.png")
    img = pix.toImage()

    tl = bar.mapTo(w, bar.rect().topLeft())
    br = bar.mapTo(w, bar.rect().bottomRight())

    print("window size:", img.width(), img.height())
    print("bar top-left en ventana:", tl.x(), tl.y())
    print("bar bottom-right en ventana:", br.x(), br.y())
    print("bar size:", bar.width(), bar.height())

    cx = tl.x() + bar.width() // 2
    below = tl.y() + bar.height()

    print("\n--- muestras centro debajo de la barra ---")
    print("x centro:", cx, "bar bottom y:", below)
    for y in range(below - 8, min(img.height(), below + 40), 4):
        print("y", y, _rgb(img, cx, y))

    print("\n--- muestras borde izquierdo/derecho de la sombra ---")
    mid_y = tl.y() + bar.height() // 2
    for x in (tl.x() - 24, tl.x() - 12, tl.x() - 4,
              tl.x() + bar.width() + 4,
              tl.x() + bar.width() + 12,
              tl.x() + bar.width() + 24):
        print("x", x, "y", mid_y, _rgb(img, x, mid_y))

    print("\n--- muestras fondo arriba/abajo para comparar ---")
    for y in (tl.y() - 20, tl.y() - 8, below + 8, below + 20, below + 32):
        print("bg y", y, _rgb(img, cx, y))

    print("\nArchivos guardados:")
    print(" - window_grab.png")
    print("Abre window_grab.png y mira la zona del reproductor.")

    QTimer.singleShot(200, app.quit)

QTimer.singleShot(1200, probe)
sys.exit(app.exec())
