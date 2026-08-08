from pathlib import Path

path = Path("ui") / "main_window.py"
text = path.read_text(encoding="utf-8")

old1 = """        self.cover_label = QLabel()
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._cover_pixmap = None
        cover_path = self._resource_path(Path("assets") / "icons" / "portada.png")

        if cover_path.exists():
            self._cover_pixmap = QPixmap(str(cover_path))
            main_layout.addWidget(self.cover_label)
            self._rescale_cover()"""
new1 = """        self.cover_label = QLabel()
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._cover_pixmap = None
        self._cover_player = None
        cover_video = self._resource_path(Path("assets") / "icons" / "portada.webm")

        if not cover_video.exists():
            cover_video = self._resource_path(Path("assets") / "icons" / "portada.mp4")

        cover_path = self._resource_path(Path("assets") / "icons" / "portada.png")

        if cover_video.exists():
            from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
            from PySide6.QtMultimediaWidgets import QVideoWidget

            self.cover_video = QVideoWidget()
            self.cover_video.setFixedHeight(150)
            self.cover_video.setAspectRatioMode(
                Qt.AspectRatioMode.KeepAspectRatioByExpanding
            )
            main_layout.addWidget(self.cover_video)

            self._cover_player = QMediaPlayer(self)
            audio = QAudioOutput(self)
            audio.setMuted(True)
            self._cover_player.setAudioOutput(audio)
            self._cover_player.setSource(QUrl.fromLocalFile(str(cover_video)))
            self._cover_player.setLoops(QMediaPlayer.Loops.Infinite)
            self._cover_player.errorOccurred.connect(self._cover_failed)
            self._cover_player.play()
        elif cover_path.exists():
            self._cover_pixmap = QPixmap(str(cover_path))
            main_layout.addWidget(self.cover_label)
            self._rescale_cover()"""
text = text.replace(old1, new1)

method = '''    def _cover_failed(self, *args) -> None:
        video = getattr(self, "cover_video", None)

        if video is not None:
            video.hide()

        cover_path = self._resource_path(Path("assets") / "icons" / "portada.png")

        if cover_path.exists():
            self._cover_pixmap = QPixmap(str(cover_path))

            if self.cover_label.parent() is None:
                self.centralWidget().layout().insertWidget(0, self.cover_label)

            self._rescale_cover()

'''

if "def _cover_failed" not in text:
    i = text.find("    def _rescale_cover(self) -> None:")
    if i != -1:
        text = text[:i] + method + text[i:]

path.write_text(text, encoding="utf-8")
print("Portada de video en bucle lista.")
