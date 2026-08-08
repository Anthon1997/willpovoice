from pathlib import Path

path = Path("ui") / "main_window.py"
text = path.read_text(encoding="utf-8")

delegate = '''class BannerDelegate(QStyledItemDelegate):
    def __init__(self, window, parent=None):
        super().__init__(parent)
        self.window = window

    def paint(self, painter, option, index):
        es_row = getattr(self.window, "_es_header_index", None)

        if es_row is not None and index.row() == es_row:
            canvas = getattr(self.window, "_spain_canvas", None)

            if canvas is not None:
                painter.drawPixmap(option.rect, canvas, canvas.rect())

        super().paint(painter, option, index)


'''

if "class BannerDelegate" in text:
    print("BannerDelegate ya existe.")
else:
    for anchor in [
        "class LicenseDialog(QDialog):",
        "class LicenseDialog",
        "class MainWindow(QMainWindow):",
    ]:
        if anchor in text:
            text = text.replace(anchor, delegate + anchor, 1)
            path.write_text(text, encoding="utf-8")
            print(f"Insertado antes de: {anchor}")
            break
    else:
        print("Ningun ancla encontrada!")
