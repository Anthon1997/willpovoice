from pathlib import Path

path = Path("ui") / "main_window.py"
text = path.read_text(encoding="utf-8")

old1 = """    def __init__(self, parent=None):
        super().__init__(parent)
        self.step = 0
        self.setWindowTitle("Ayuda de WillpoVoice")"""
new1 = """    def __init__(self, parent=None, targets=None):
        super().__init__(parent)
        self.step = 0
        self.targets = targets or []
        self.setWindowTitle("Ayuda de WillpoVoice")"""
text = text.replace(old1, new1)

old2 = """        if self.step == len(self.STEPS) - 1:
            self.next_button.setText("Finalizar")
        else:
            self.next_button.setText("Siguiente ->")"""
new2 = """        if self.step == len(self.STEPS) - 1:
            self.next_button.setText("Finalizar")
        else:
            self.next_button.setText("Siguiente ->")

        self._position_near_target()

    def _position_near_target(self):
        parent = self.parent()

        if parent is None:
            return

        attr = None

        if self.targets and self.step < len(self.targets):
            attr = self.targets[self.step]

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

        point = target.mapToGlobal(QPoint(0, target.height()))
        pg = parent.frameGeometry()
        x = min(max(point.x(), pg.x()), pg.right() - self.width())
        y = point.y() + 8

        if y + self.height() > pg.bottom():
            y = point.y() - self.height() - 8

        self.move(x, y)"""
text = text.replace(old2, new2)

old3 = """    def show_help(self) -> None:
        wizard = HelpWizard(self)
        wizard.exec()"""
new3 = """    def show_help(self) -> None:
        wizard = HelpWizard(
            self,
            targets=[
                None,
                "voice_combo",
                "text_edit",
                "rate_slider",
                "speak_button",
                "stop_button",
                "export_button",
                "history_combo",
                "help_button",
            ],
        )
        wizard.exec()"""
text = text.replace(old3, new3)

path.write_text(text, encoding="utf-8")
print("Tour interactivo listo.")
