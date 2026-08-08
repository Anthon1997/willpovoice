from pathlib import Path

path = Path("ui") / "main_window.py"
text = path.read_text(encoding="utf-8")

old1 = """    def set_target(self, widget):
        if widget is None:
            self.target_rect = None
        else:
            pos = widget.mapTo(self, QPoint(0, 0))
            self.target_rect = QRect(
                pos.x() - 6,
                pos.y() - 6,
                widget.width() + 12,
                widget.height() + 12,
            )

        self.update()"""
new1 = """    def set_target(self, widget):
        if widget is None:
            self.target_rect = None
        else:
            top_left = widget.mapToGlobal(QPoint(0, 0))
            overlay_top_left = self.mapToGlobal(QPoint(0, 0))
            x = top_left.x() - overlay_top_left.x()
            y = top_left.y() - overlay_top_left.y()
            self.target_rect = QRect(
                x - 6, y - 6, widget.width() + 12, widget.height() + 12
            )

        self.update()"""
text = text.replace(old1, new1)

old2 = """        point = target.mapToGlobal(QPoint(0, target.height()))
        pg = parent.frameGeometry()
        center = point.x() + target.width() // 2
        x = center - self.width() // 2
        x = min(max(x, pg.x() + 4), pg.right() - self.width() - 4)
        y = point.y() + 10

        if y + self.height() > pg.bottom():
            y = target.mapToGlobal(QPoint(0, 0)).y() - self.height() - 10

        self.move(x, y)"""
new2 = """        pg = parent.frameGeometry()
        top_left = target.mapToGlobal(QPoint(0, 0))

        center_x = top_left.x() + target.width() // 2
        x = center_x - self.width() // 2
        x = min(max(x, pg.x() + 4), pg.right() - self.width() - 4)

        window_mid = pg.y() + pg.height() // 2

        if top_left.y() > window_mid:
            y = top_left.y() - self.height() - 10
        else:
            y = top_left.y() + target.height() + 10

        self.move(x, y)"""
text = text.replace(old2, new2)

path.write_text(text, encoding="utf-8")
print("Spotlight exacto y ventana encima de botones.")
