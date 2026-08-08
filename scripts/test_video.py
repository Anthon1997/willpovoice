import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import QUrl

app = QApplication(sys.argv)
w = QMainWindow()
v = QVideoWidget()
w.setCentralWidget(v)
w.resize(800, 200)

p = QMediaPlayer()
a = QAudioOutput()
p.setAudioOutput(a)
p.setSource(QUrl.fromLocalFile("assets/icons/portada.mp4"))
p.mediaStatusChanged.connect(lambda s: print("STATUS:", s))
p.errorOccurred.connect(lambda e, msg: print("ERROR:", e, msg))
p.play()

w.show()
sys.exit(app.exec())
