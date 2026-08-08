from pathlib import Path

path = Path("ui") / "main_window.py"
text = path.read_text(encoding="utf-8")

text = text.replace(
    "from PySide6.QtGui import QBrush, QColor, QDesktopServices, QIcon, QMovie, QImageReader, QPainter, QPainterPath, QPixmap, QTransform",
    "from PySide6.QtGui import QBrush, QColor, QDesktopServices, QIcon, QFont, QMovie, QImageReader, QPainter, QPainterPath, QPixmap, QTransform",
)

start = text.find("        self.open_menu = QMenu(self)")
end = text.find("        self.open_file_button.installEventFilter(self)")

if start == -1 or end == -1:
    print("ERROR: anclas del menu no encontradas")
else:
    end += len("        self.open_file_button.installEventFilter(self)")

    new_block = '''        self.open_menu = QMenu(self)
        self.open_menu.setMinimumWidth(250)
        self.open_menu.setIconSize(QSize(18, 18))
        self.open_menu.setStyleSheet(
            "QMenu { background-color: #10333c; border: 1px solid #1f4a55; "
            "border-radius: 8px; padding: 6px; } "
            "QMenu::item { padding: 9px 26px 9px 10px; border-radius: 5px; "
            "color: #e6f4f1; } "
            "QMenu::item:selected { background-color: #17606d; } "
            "QMenu::separator { height: 1px; background: #1f4a55; "
            "margin: 5px 8px; }"
        )

        self.open_menu.addAction(
            self._format_icon("#4da3ff", "TXT"),
            "Texto plano  (.txt, .md, .log)",
            lambda: self._open_document(
                "Archivos de texto (*.txt *.md *.log *.csv)"
            ),
        )
        self.open_menu.addAction(
            self._format_icon("#e05252", "PDF"),
            "Documento PDF  (.pdf)",
            lambda: self._open_document("Documentos PDF (*.pdf)"),
        )
        self.open_menu.addAction(
            self._format_icon("#2b7de9", "DOC"),
            "Word moderno  (.docx)",
            lambda: self._open_document("Documentos Word (*.docx)"),
        )
        self.open_menu.addAction(
            self._format_icon("#185abd", "DOC"),
            "Word antiguo  (.doc, requiere Word)",
            lambda: self._open_document("Word antiguo (*.doc)"),
        )
        self.open_menu.addAction(
            self._format_icon("#f2a33c", "RTF"),
            "Formato enriquecido  (.rtf)",
            lambda: self._open_document("Formato enriquecido (*.rtf)"),
        )
        self.open_menu.addAction(
            self._format_icon("#9b59f6", "WEB"),
            "Pagina web  (.html)",
            lambda: self._open_document("Paginas web (*.html *.htm)"),
        )
        self.open_menu.addSeparator()
        self.open_menu.addAction(
            self._format_icon("#4de3b0", "TODO"),
            "Todos los formatos",
            lambda: self._open_document(
                "Todos (*.txt *.md *.log *.csv *.pdf *.docx *.doc *.rtf "
                "*.html *.htm)"
            ),
        )
        self.open_file_button.installEventFilter(self)'''

    text = text[:start] + new_block + text[end:]

icon_method = '''    def _format_icon(self, color: str, label: str) -> QIcon:
        pix = QPixmap(20, 20)
        pix.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(1, 1, 18, 18, 4, 4)
        painter.setPen(QColor("white"))
        painter.setFont(QFont("Segoe UI", 6, QFont.Weight.Bold))
        painter.drawText(pix.rect(), Qt.AlignmentFlag.AlignCenter, label)
        painter.end()

        return QIcon(pix)

'''

if "def _format_icon" not in text:
    i = text.find("    def _show_open_menu(self) -> None:")
    if i != -1:
        text = text[:i] + icon_method + text[i:]

path.write_text(text, encoding="utf-8")
print("Menu profesional con iconos listo.")
