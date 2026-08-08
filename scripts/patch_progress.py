from pathlib import Path

path = Path("ui") / "main_window.py"
text = path.read_text(encoding="utf-8")

old_prog = """        self.export_progress = QProgressDialog("Exportando audio...", None, 0, 0, self)
        self.export_progress.setWindowTitle("Exportando")
        self.export_progress.setModal(True)
        self.export_progress.show()"""

new_prog = """        self.export_progress = QProgressDialog(
            "Exportando audio...", None, 0, 100, self
        )
        self.export_progress.setWindowTitle("Exportando")
        self.export_progress.setModal(True)
        self.export_progress.setCancelButton(None)
        self.export_progress.setValue(0)
        self.export_progress.show()

        self._export_tick_timer = QTimer(self)
        self._export_tick_timer.timeout.connect(self._tick_export_progress)
        self._export_tick_timer.start(120)"""

text = text.replace(old_prog, new_prog)

old_close = """        if getattr(self, "export_progress", None):
            self.export_progress.close()
            self.export_progress = None"""

new_close = """        self._finish_export_progress()"""

text = text.replace(old_close, new_close)

methods = '''    def _tick_export_progress(self) -> None:
        prog = getattr(self, "export_progress", None)

        if prog is None:
            return

        if prog.value() < 90:
            prog.setValue(prog.value() + 2)

    def _finish_export_progress(self) -> None:
        timer = getattr(self, "_export_tick_timer", None)

        if timer is not None:
            timer.stop()
            self._export_tick_timer = None

        prog = getattr(self, "export_progress", None)

        if prog is not None:
            prog.setValue(100)
            prog.close()
            self.export_progress = None

'''

if "def _tick_export_progress" not in text:
    i = text.find("    def export_wav(self) -> None:")
    if i != -1:
        text = text[:i] + methods + text[i:]

path.write_text(text, encoding="utf-8")
print("Progreso progresivo de exportacion listo.")
