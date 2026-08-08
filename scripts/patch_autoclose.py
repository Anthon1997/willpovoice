from pathlib import Path

path = Path("ui") / "main_window.py"
text = path.read_text(encoding="utf-8")

text = text.replace(
    "from PySide6.QtGui import QBrush, QColor, QDesktopServices, QIcon, QFont, QMovie, QImageReader, QPainter, QPainterPath, QPen, QPixmap, QTransform",
    "from PySide6.QtGui import QBrush, QColor, QCursor, QDesktopServices, QIcon, QFont, QMovie, QImageReader, QPainter, QPainterPath, QPen, QPixmap, QTransform",
)

text = text.replace(
    "        self.open_file_button.installEventFilter(self)",
    "        self.open_file_button.installEventFilter(self)\n"
    "        self.open_menu.installEventFilter(self)",
)
text = text.replace(
    "        self.export_button.installEventFilter(self)",
    "        self.export_button.installEventFilter(self)\n"
    "        self.export_menu.installEventFilter(self)",
)

old_filter = """    def eventFilter(self, obj, event):
        if obj is self.open_file_button and event.type() == QEvent.Type.HoverEnter:
            self._show_open_menu()

        if obj is self.export_button and event.type() == QEvent.Type.HoverEnter:
            self._show_export_menu()

        return super().eventFilter(obj, event)"""
new_filter = """    def eventFilter(self, obj, event):
        if obj is self.open_file_button and event.type() == QEvent.Type.HoverEnter:
            self._show_open_menu()

        if obj is self.export_button and event.type() == QEvent.Type.HoverEnter:
            self._show_export_menu()

        if obj in (self.open_menu, self.export_menu) and event.type() == QEvent.Type.Leave:
            QTimer.singleShot(200, lambda menu=obj: self._close_if_out(menu))

        return super().eventFilter(obj, event)

    def _close_if_out(self, menu) -> None:
        if not menu.isVisible():
            return

        if menu.rect().contains(menu.mapFromGlobal(QCursor.pos())):
            return

        menu.close()"""
text = text.replace(old_filter, new_filter)

path.write_text(text, encoding="utf-8")
print("Autocierre de menus listo.")
