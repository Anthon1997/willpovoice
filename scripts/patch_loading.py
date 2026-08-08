from pathlib import Path

path = Path("ui") / "main_window.py"
text = path.read_text(encoding="utf-8")

if "QProgressBar" not in text.split("\n")[0:50]:
    text = text.replace(
        "QLabel,",
        "QLabel,\n    QProgressBar,",
        1,
    )

old_class = '''class SpeakingDialog(QDialog):
    def __init__(self, parent, engine):
        super().__init__(parent)
        self.engine = engine
        self.setWindowTitle("Reproduciendo")
        self.setModal(False)
        self.setFixedWidth(260)

        layout = QVBoxLayout(self)

        self.gif_label = QLabel()
        gif_path = MainWindow._resource_path(Path("assets") / "icons" / "spectrum.gif")

        if not gif_path.exists():
            gif_path = MainWindow._resource_path(Path("assets") / "icons" / "palette.gif")

        if gif_path.exists():
            self.movie = QMovie(str(gif_path))
            self.movie.setScaledSize(QSize(132, 64))
            self.gif_label.setMovie(self.movie)
            self.movie.start()

        self.gif_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.gif_label)

        self.info_label = QLabel("Reproduciendo texto...")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)

        self.stop_button = QPushButton("Detener")
        self.stop_button.clicked.connect(self.stop_and_close)
        layout.addWidget(self.stop_button)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_state)
        self.timer.start(300)

    def check_state(self):
        try:
            state = self.engine.adapter.sapi.Status.RunningState
        except Exception:
            state = 1

        if state == 1:
            self.timer.stop()
            self.close()

    def stop_and_close(self):
        try:
            self.engine.stop()
        except Exception:
            pass

        self.timer.stop()
        self.close()'''

new_class = '''class SpeakingDialog(QDialog):
    def __init__(self, parent, engine):
        super().__init__(parent)
        self.engine = engine
        self.setWindowTitle("Reproduciendo")
        self.setModal(False)
        self.setFixedWidth(260)
        self.has_started = False
        self.ticks_without_speech = 0

        layout = QVBoxLayout(self)

        self.gif_label = QLabel()
        gif_path = MainWindow._resource_path(Path("assets") / "icons" / "spectrum.gif")

        if not gif_path.exists():
            gif_path = MainWindow._resource_path(Path("assets") / "icons" / "palette.gif")

        if gif_path.exists():
            self.movie = QMovie(str(gif_path))
            self.movie.setScaledSize(QSize(132, 64))
            self.gif_label.setMovie(self.movie)
            self.movie.start()

        self.gif_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.gif_label)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(8)
        layout.addWidget(self.progress)

        self.info_label = QLabel("Preparando voz...")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)

        self.stop_button = QPushButton("Detener")
        self.stop_button.clicked.connect(self.stop_and_close)
        layout.addWidget(self.stop_button)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_state)
        self.timer.start(300)

    def check_state(self):
        try:
            state = self.engine.adapter.sapi.Status.RunningState
        except Exception:
            state = 1

        if state == 0:
            if not self.has_started:
                self.has_started = True
                self.info_label.setText("Reproduciendo texto...")
                self.progress.hide()
        else:
            if self.has_started:
                self.timer.stop()
                self.close()
                return

            self.ticks_without_speech += 1

            if self.ticks_without_speech >= 50:
                self.info_label.setText("No se pudo iniciar la voz.")
                self.progress.hide()
                self.timer.stop()
                QTimer.singleShot(1500, self.close)

    def stop_and_close(self):
        try:
            self.engine.stop()
        except Exception:
            pass

        self.timer.stop()
        self.close()'''

if old_class in text:
    text = text.replace(old_class, new_class)
    path.write_text(text, encoding="utf-8")
    print("SpeakingDialog actualizado con barra de carga.")
else:
    print("ERROR: no se encontro la clase exacta. Verificar indentacion.")
