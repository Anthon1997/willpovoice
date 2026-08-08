from pathlib import Path

path = Path("ui") / "main_window.py"
text = path.read_text(encoding="utf-8")

new_setup = '''    def _setup_cover(self) -> None:
        frames_dir = self._resource_path(
            Path("assets") / "icons" / "portada_frames"
        )

        if frames_dir.exists():
            files = sorted(frames_dir.glob("*.jpg"))

            if files:
                from PySide6.QtCore import QByteArray

                self._cover_frames = [
                    QByteArray(f.read_bytes()) for f in files
                ]
                self._cover_index = 0
                self.cover_label.setParent(self.header_widget)
                self.cover_label.setGeometry(
                    0,
                    0,
                    self.header_widget.width(),
                    self.header_widget.height(),
                )
                self.cover_label.lower()

                for child in self.header_widget.findChildren(QWidget()):
                    if child is not self.cover_label:
                        child.raise_()

                self._cover_timer = QTimer(self)
                self._cover_timer.timeout.connect(self._advance_cover)
                self._cover_timer.start(100)
                self._advance_cover()
                return

        self._use_static_cover()

    def _advance_cover(self) -> None:
        frames = getattr(self, "_cover_frames", None)

        if not frames:
            return

        pix = QPixmap()
        pix.loadFromData(frames[self._cover_index])
        self._cover_index = (self._cover_index + 1) % len(frames)

        header = getattr(self, "header_widget", None)

        if header is not None and header.width() > 10:
            pix = pix.scaled(
                header.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )

        self.cover_label.setPixmap(pix)

'''

start = text.find("    def _setup_cover(self) -> None:")

if start != -1:
    end = text.find("    def ", start + 10)

    if end != -1:
        text = text[:start] + new_setup + text[end:]

path.write_text(text, encoding="utf-8")
print("Portada animada por fotogramas lista.")
