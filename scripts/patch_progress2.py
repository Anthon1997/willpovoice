from pathlib import Path

path = Path("ui") / "main_window.py"
text = path.read_text(encoding="utf-8")

old1 = """        self.export_progress = QProgressDialog(
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

old2 = """        self.export_progress = QProgressDialog(
            "Exportando audio...", None, 0, 0, self
        )
        self.export_progress.setWindowTitle("Exportando")
        self.export_progress.setModal(True)
        self.export_progress.show()"""

text = text.replace(old1, "        self._start_export_progress()")
text = text.replace(old2, "        self._start_export_progress()")

new_methods = '''    def _start_export_progress(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("Exportando")
        dialog.setModal(True)
        dialog.setFixedWidth(380)

        layout = QVBoxLayout(dialog)

        label = QLabel("Exportando audio...")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        row = QHBoxLayout()

        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(0)
        row.addWidget(bar, 1)

        pct = QLabel("0%")
        pct.setFixedWidth(48)
        pct.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        row.addWidget(pct)

        layout.addLayout(row)

        dialog.show()

        self.export_progress = dialog
        self._export_bar = bar
        self._export_pct = pct

        self._export_tick_timer = QTimer(self)
        self._export_tick_timer.timeout.connect(self._tick_export_progress)
        self._export_tick_timer.start(120)

    def _tick_export_progress(self) -> None:
        bar = getattr(self, "_export_bar", None)

        if bar is None:
            return

        if bar.value() < 90:
            bar.setValue(bar.value() + 2)

        pct = getattr(self, "_export_pct", None)

        if pct is not None:
            pct.setText(f"{bar.value()}%")

    def _finish_export_progress(self) -> None:
        timer = getattr(self, "_export_tick_timer", None)

        if timer is not None:
            timer.stop()
            self._export_tick_timer = None

        bar = getattr(self, "_export_bar", None)

        if bar is not None:
            bar.setValue(100)

        pct = getattr(self, "_export_pct", None)

        if pct is not None:
            pct.setText("100%")

        prog = getattr(self, "export_progress", None)

        if prog is not None:
            prog.close()
            self.export_progress = None

'''

start = text.find("    def _tick_export_progress")

if start != -1:
    end = text.find("    def ", start + 10)
    end2 = text.find("    def ", end + 10)

    if end != -1 and end2 != -1:
        text = text[:start] + new_methods + text[end2:]

path.write_text(text, encoding="utf-8")
print("Barra progresiva con porcentaje lista.")
