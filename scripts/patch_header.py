from pathlib import Path

path = Path("ui") / "main_window.py"
text = path.read_text(encoding="utf-8")

start = text.find("        logo_label = QLabel()")
end = text.find("        main_layout.addWidget(self.header_widget)")

if start == -1 or end == -1:
    print("ERROR: anclas no encontradas", start, end)
else:
    new_block = '''        logo_label = QLabel()
        logo_label.setStyleSheet("background: transparent;")
        logo_path = self._resource_path(Path("assets") / "icons" / "logo.png")

        if not logo_path.exists():
            logo_path = self._resource_path(Path("assets") / "icons" / "icon.ico")

        if logo_path.exists():
            pixmap = QPixmap(str(logo_path)).scaledToHeight(
                48, Qt.TransformationMode.SmoothTransformation
            )
            logo_label.setPixmap(pixmap)

        title_label = QLabel("WillpoVoice")
        title_label.setStyleSheet(
            "font-size: 22px; font-weight: 700; background: transparent;"
        )

        subtitle_label = QLabel("Convierte texto en voz con voces naturales")
        subtitle_label.setStyleSheet("font-size: 12px; background: transparent;")

        text_container = QWidget()
        text_container.setStyleSheet("background: transparent;")
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(10, 0, 0, 0)
        text_layout.setSpacing(4)
        text_layout.addWidget(title_label)
        text_layout.addWidget(subtitle_label)

        header_layout.addWidget(logo_label, 0, Qt.AlignmentFlag.AlignVCenter)
        header_layout.addWidget(text_container, 0, Qt.AlignmentFlag.AlignVCenter)
        header_layout.addStretch()

'''
    text = text[:start] + new_block + text[end:]
    path.write_text(text, encoding="utf-8")
    print("Encabezado reconstruido: texto paralelo al logo.")
