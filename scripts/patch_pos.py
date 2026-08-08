from pathlib import Path

path = Path("ui") / "main_window.py"
text = path.read_text(encoding="utf-8")

new_method = '''    def _position_near_target(self):
        parent = self.parent()

        if parent is None:
            return

        attr = None

        if self.targets and self.step < len(self.targets):
            attr = self.targets[self.step]

        if self.overlay:
            self.overlay.set_target(
                None if attr is None else getattr(parent, attr, None)
            )

        if attr is None:
            frame = parent.frameGeometry()
            self.move(
                frame.center().x() - self.width() // 2,
                frame.center().y() - self.height() // 2,
            )
            return

        target = getattr(parent, attr, None)

        if target is None:
            return

        pg = parent.frameGeometry()
        top_left = target.mapToGlobal(QPoint(0, 0))

        center_x = top_left.x() + target.width() // 2
        x = center_x - self.width() // 2
        x = min(max(x, pg.x() + 4), pg.right() - self.width() - 4)

        window_mid = pg.y() + pg.height() // 2

        if top_left.y() > window_mid:
            y = top_left.y() - self.height() - 20
        else:
            y = top_left.y() + target.height() + 12

        self.move(x, y)


'''

start = text.find("    def _position_near_target(self):")

if start != -1:
    end = text.find("    def ", start + 10)

    if end != -1:
        text = text[:start] + new_method + text[end:]
        path.write_text(text, encoding="utf-8")
        print("Posicionamiento corregido con distancia de la foto.")
    else:
        print("ERROR: no se encontro el fin del metodo.")
else:
    print("ERROR: no se encontro _position_near_target.")
