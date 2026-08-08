from pathlib import Path
import re

path = Path("ui") / "main_window.py"
text = path.read_text(encoding="utf-8")

text = text.replace(
    "from PySide6.QtCore import Qt, QThread, QTimer, QUrl, Signal, QSize",
    "from PySide6.QtCore import QEvent, Qt, QThread, QTimer, QUrl, Signal, QSize",
)
text = text.replace("    QMainWindow,", "    QMainWindow,\n    QMenu,")

if "from core import file_reader" not in text:
    text = text.replace(
        "from core import license_manager",
        "from core import file_reader\nfrom core import license_manager",
    )

text = text.replace('QPushButton("Abrir TXT")', 'QPushButton("Abrir")')

text = re.sub(
    r"self\.open_file_button\.clicked\.connect\(self\.\w+\)",
    "self.open_file_button.clicked.connect(self._show_open_menu)",
    text,
)

anchor = '        self.open_file_button = QPushButton("Abrir")'
menu_block = anchor + '''
        self.open_menu = QMenu(self)
        self.open_menu.addAction(
            "Texto plano  (.txt, .md, .log)",
            lambda: self._open_document("Archivos de texto (*.txt *.md *.log *.csv)"),
        )
        self.open_menu.addAction(
            "PDF  (.pdf)",
            lambda: self._open_document("Documentos PDF (*.pdf)"),
        )
        self.open_menu.addAction(
            "Word  (.docx)",
            lambda: self._open_document("Documentos Word (*.docx)"),
        )
        self.open_menu.addAction(
            "Word antiguo  (.doc, requiere Word)",
            lambda: self._open_document("Word antiguo (*.doc)"),
        )
        self.open_menu.addAction(
            "RTF  (.rtf)",
            lambda: self._open_document("Formato enriquecido (*.rtf)"),
        )
        self.open_menu.addAction(
            "Web  (.html)",
            lambda: self._open_document("Paginas web (*.html *.htm)"),
        )
        self.open_menu.addSeparator()
        self.open_menu.addAction(
            "Todos los formatos",
            lambda: self._open_document(
                "Todos (*.txt *.md *.log *.csv *.pdf *.docx *.doc *.rtf *.html *.htm)"
            ),
        )
        self.open_file_button.installEventFilter(self)'''
text = text.replace(anchor, menu_block)

methods = '''    def _show_open_menu(self) -> None:
        pos = self.open_file_button.mapToGlobal(
            QPoint(0, self.open_file_button.height())
        )
        self.open_menu.popup(pos)

    def _open_document(self, filter_text: str) -> None:
        path_str, _ = QFileDialog.getOpenFileName(
            self, "Abrir documento", "", filter_text
        )

        if not path_str:
            return

        try:
            content = file_reader.extract_text(Path(path_str))
        except Exception as exc:
            QMessageBox.warning(
                self, "WillpoVoice", f"No se pudo leer el archivo: {exc}"
            )
            return

        self.text_edit.setPlainText(content)
        self.statusBar().showMessage(
            f"Documento cargado: {Path(path_str).name}"
        )

    def eventFilter(self, obj, event):
        if obj is self.open_file_button and event.type() == QEvent.Type.HoverEnter:
            self._show_open_menu()

        return super().eventFilter(obj, event)

'''

if "def _show_open_menu" not in text:
    i = text.find("    def show_help(self) -> None:")
    if i != -1:
        text = text[:i] + methods + text[i:]

path.write_text(text, encoding="utf-8")
print("Boton Abrir con menu desplegable listo.")
