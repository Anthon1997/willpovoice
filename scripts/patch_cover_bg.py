from pathlib import Path

path = Path("ui") / "main_window.py"
text = path.read_text(encoding="utf-8")

report = []

old_block = text[text.find("        self.cover_label = QLabel()"):text.find("        header_layout = QHBoxLayout()")]
if old_block:
    new_block = '''        self.cover_label = QLabel()
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._cover_pixmap = None
        self._cover_player = None
        self._cover_video_path = self._resource_path(
            Path("assets") / "icons" / "portada.webm"
        )

        if not self._cover_video_path.exists():
            self._cover_video_path = self._resource_path(
                Path("assets") / "icons" / "portada.mp4"
            )

        self._cover_image_path = self._resource_path(
            Path("assets") / "icons" / "portada.png"
        )

'''
    text = text.replace(old_block, new_block)
    report.append("bloque de rutas")

text = text.replace(
    "        header_layout = QHBoxLayout()",
    "        self.header_widget = QWidget()\n"
    "        self.header_widget.setFixedHeight(170)\n"
    "        header_layout = QHBoxLayout(self.header_widget)",
)

text = text.replace(
    "        main_layout.addLayout(header_layout)",
    "        main_layout.addWidget(self.header_widget)\n"
    "        self._setup_cover()",
)
report.append("contenedor de encabezado")

def replace_method(name, new_body):
    global text
    start = text.find(f"    def {name}(")
    if start == -1:
        return False
    end = text.find("    def ", start + 10)
    if end == -1:
        return False
    text = text[:start] + new_body + "\n" + text[end:]
    return True

setup_cover = '''    def _setup_cover(self) -> None:
        video_path = getattr(self, "_cover_video_path", None)

        if video_path is not None and video_path.exists():
            from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
            from PySide6.QtMultimediaWidgets import QVideoWidget

            self.cover_video = QVideoWidget(self.header_widget)
            self.cover_video.setAspectRatioMode(
                Qt.AspectRatioMode.KeepAspectRatioByExpanding
            )
            self.cover_video.setGeometry(
                0, 0, self.header_widget.width(), self.header_widget.height()
            )
            self.cover_video.lower()

            self._cover_player = QMediaPlayer(self)
            audio = QAudioOutput(self)
            audio.setMuted(True)
            self._cover_player.setAudioOutput(audio)
            self._cover_player.setSource(QUrl.fromLocalFile(str(video_path)))
            self._cover_player.setLoops(QMediaPlayer.Loops.Infinite)
            self._cover_player.errorOccurred.connect(self._cover_failed)
            self._cover_player.mediaStatusChanged.connect(self._cover_status)
            self._cover_player.play()
            return

        self._use_static_cover()

    def _cover_status(self, status) -> None:
        if int(status) == 6:
            self._cover_failed()

    def _use_static_cover(self) -> None:
        image_path = getattr(self, "_cover_image_path", None)

        if image_path is None or not image_path.exists():
            return

        self._cover_pixmap = QPixmap(str(image_path))
        self.cover_label.setParent(self.header_widget)
        self.cover_label.setGeometry(
            0, 0, self.header_widget.width(), self.header_widget.height()
        )
        self.cover_label.lower()
        self._rescale_cover()

    def _cover_failed(self, *args) -> None:
        video = getattr(self, "cover_video", None)

        if video is not None:
            video.hide()

        self._use_static_cover()

    def _rescale_cover(self) -> None:
        pix = getattr(self, "_cover_pixmap", None)

        if pix is None or pix.isNull():
            return

        self.cover_label.setPixmap(
            pix.scaled(
                self.header_widget.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)

        header = getattr(self, "header_widget", None)

        if header is None:
            return

        video = getattr(self, "cover_video", None)

        if video is not None:
            video.setGeometry(0, 0, header.width(), header.height())

        if getattr(self, "_cover_pixmap", None) is not None:
            self.cover_label.setGeometry(0, 0, header.width(), header.height())
            self._rescale_cover()
'''

for name in ("_rescale_cover", "resizeEvent", "_cover_failed"):
    replace_method(name, "")

i = text.find("    def show_help(self) -> None:")
if i != -1 and "def _setup_cover" not in text:
    text = text[:i] + setup_cover + "\n" + text[i:]
    report.append("metodos de portada")

path.write_text(text, encoding="utf-8")
print("Cambios:", report)
