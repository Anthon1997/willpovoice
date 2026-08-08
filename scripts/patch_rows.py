from pathlib import Path

path = Path("ui") / "main_window.py"
text = path.read_text(encoding="utf-8")

text = text.replace(
    "    QGroupBox,",
    "    QFrame,\n    QGroupBox,",
)
text = text.replace(
    "    QVBoxLayout,",
    "    QVBoxLayout,\n    QWidgetAction,",
)

start = text.find("        self.open_menu = QMenu(self)")
end = text.find("        self.open_file_button.installEventFilter(self)")

if start == -1 or end == -1:
    print("ERROR: anclas no encontradas")
else:
    end += len("        self.open_file_button.installEventFilter(self)")

    new_block = '''        self.open_menu = QMenu(self)
        self.open_menu.setMinimumWidth(260)
        self.open_menu.setStyleSheet(
            "QMenu { background-color: #0e3a46; border: 1px solid #1f4a55; "
            "border-radius: 6px; padding: 0px; } "
            "QMenu::separator { height: 1px; background: #1f5a68; }"
        )

        self._add_menu_row(
            self._format_icon("#4da3ff", "TXT"),
            "Texto plano  (.txt, .md, .log)",
            lambda: self._open_document(
                "Archivos de texto (*.txt *.md *.log *.csv)"
            ),
        )
        self.open_menu.addSeparator()
        self._add_menu_row(
            self._format_icon("#e02020", "PDF"),
            "Documento PDF  (.pdf)",
            lambda: self._open_document("Documentos PDF (*.pdf)"),
        )
        self.open_menu.addSeparator()
        self._add_menu_row(
            self._format_icon("#2b7de9", "DOC"),
            "Word moderno  (.docx)",
            lambda: self._open_document("Documentos Word (*.docx)"),
        )
        self.open_menu.addSeparator()
        self._add_menu_row(
            self._format_icon("#185abd", "DOC"),
            "Word antiguo  (.doc, requiere Word)",
            lambda: self._open_document("Word antiguo (*.doc)"),
        )
        self.open_menu.addSeparator()
        self._add_menu_row(
            self._format_icon("#f2a33c", "RTF"),
            "Formato enriquecido  (.rtf)",
            lambda: self._open_document("Formato enriquecido (*.rtf)"),
        )
        self.open_menu.addSeparator()
        self._add_menu_row(
            self._format_icon("#9b59f6", "WEB"),
            "Pagina web  (.html)",
            lambda: self._open_document("Paginas web (*.html *.htm)"),
        )
        self.open_menu.addSeparator()
        self._add_menu_row(
            self._format_icon("#4de3b0", "TODO"),
            "Todos los formatos",
            lambda: self._open_document(
                "Todos (*.txt *.md *.log *.csv *.pdf *.docx *.doc *.rtf "
                "*.html *.htm)"
            ),
        )
        self.open_file_button.installEventFilter(self)'''

    text = text[:start] + new_block + text[end:]

row_method = '''    def _add_menu_row(self, icon: QIcon, label: str, handler) -> None:
        row = QFrame()
        row.setObjectName("openMenuRow")
        row.setCursor(Qt.CursorShape.PointingHandCursor)
        row.setStyleSheet(
            "QFrame#openMenuRow { background: transparent; } "
            "QFrame#openMenuRow:hover { background: #1596a8; } "
            "QFrame#openMenuRow QLabel { background: transparent; }"
        )

        layout = QHBoxLayout(row)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        icon_label = QLabel()
        icon_label.setPixmap(icon.pixmap(20, 24))
        layout.addWidget(icon_label)

        text_label = QLabel(label)
        text_label.setStyleSheet("color: #eaf7f4;")
        layout.addWidget(text_label)
        layout.addStretch()

        row.mouseReleaseEvent = lambda event: (
            self.open_menu.close(),
            handler(),
        )

        action = QWidgetAction(self.open_menu)
        action.setDefaultWidget(row)
        self.open_menu.addAction(action)

'''

if "def _add_menu_row" not in text:
    i = text.find("    def _format_icon(self")
    if i != -1:
        text = text[:i] + row_method + text[i:]

path.write_text(text, encoding="utf-8")
print("Filas profesionales con icono pegado al texto.")
