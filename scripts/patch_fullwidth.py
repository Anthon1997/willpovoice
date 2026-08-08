from pathlib import Path

path = Path("ui") / "main_window.py"
text = path.read_text(encoding="utf-8")

text = text.replace(
    'title_label.setStyleSheet("font-size: 22px; font-weight: 700;")',
    'title_label.setStyleSheet("font-size: 22px; font-weight: 700; background: transparent;")',
)
text = text.replace(
    'subtitle_label.setStyleSheet("font-size: 12px;")',
    'subtitle_label.setStyleSheet("font-size: 12px; background: transparent;")',
)
text = text.replace(
    "        logo_label = QLabel()",
    '        logo_label = QLabel()\n        logo_label.setStyleSheet("background: transparent;")',
)
text = text.replace(
    "        self.header_widget = QWidget()\n        self.header_widget.setFixedHeight(170)",
    '        self.header_widget = QWidget()\n        self.header_widget.setFixedHeight(170)\n        self.header_widget.setStyleSheet("background: transparent;")',
)

old_place = """                self.cover_label.setParent(self.header_widget)
                self.cover_label.setGeometry(
                    0,
                    0,
                    self.header_widget.width(),
                    self.header_widget.height(),
                )
                self.cover_label.lower()

                for child in self.header_widget.findChildren(QWidget()):
                    if child is not self.cover_label:
                        child.raise_()"""
new_place = """                self.cover_label.setParent(self.centralWidget())
                self._place_cover()
                self.cover_label.lower()"""
text = text.replace(old_place, new_place)

old_static = """        self._cover_pixmap = QPixmap(str(image_path))
        self.cover_label.setParent(self.header_widget)
        self.cover_label.setGeometry(
            0, 0, self.header_widget.width(), self.header_widget.height()
        )
        self.cover_label.lower()
        self._rescale_cover()"""
new_static = """        self._cover_pixmap = QPixmap(str(image_path))
        self.cover_label.setParent(self.centralWidget())
        self._place_cover()
        self.cover_label.lower()
        self._rescale_cover()"""
text = text.replace(old_static, new_static)

place_method = '''    def _place_cover(self) -> None:
        central = self.centralWidget()
        header = getattr(self, "header_widget", None)

        if header is None:
            return

        bottom = header.y() + header.height()
        self.cover_label.setGeometry(0, 0, central.width(), bottom)

'''

if "def _place_cover" not in text:
    i = text.find("    def _setup_cover(self) -> None:")
    if i != -1:
        text = text[:i] + place_method + text[i:]

old_advance = """        header = getattr(self, "header_widget", None)

        if header is not None and header.width() > 10:
            pix = pix.scaled(
                header.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )

        self.cover_label.setPixmap(pix)"""
new_advance = """        if self.cover_label.width() > 10:
            pix = pix.scaled(
                self.cover_label.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )

        self.cover_label.setPixmap(pix)"""
text = text.replace(old_advance, new_advance)

old_rescale = """        self.cover_label.setPixmap(
            pix.scaled(
                self.header_widget.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
        )"""
new_rescale = """        self.cover_label.setPixmap(
            pix.scaled(
                self.cover_label.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
        )"""
text = text.replace(old_rescale, new_rescale)

def replace_method(name, new_body):
    global text
    start = text.find(f"    def {name}(")
    if start == -1:
        return
    end = text.find("    def ", start + 10)
    if end == -1:
        return
    text = text[:start] + new_body + "\n" + text[end:]

replace_method("resizeEvent", '''    def resizeEvent(self, event):
        super().resizeEvent(event)

        label = getattr(self, "cover_label", None)

        if label is None or label.parent() is None:
            return

        self._place_cover()

        if getattr(self, "_cover_frames", None):
            self._advance_cover()
        elif getattr(self, "_cover_pixmap", None) is not None:
            self._rescale_cover()
''')

path.write_text(text, encoding="utf-8")
print("Video extremo a extremo y sin recuadros.")
