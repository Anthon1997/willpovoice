from pathlib import Path

path = Path("ui") / "main_window.py"
text = path.read_text(encoding="utf-8")

old1 = """        self.progress = QProgressBar()
        self.progress.setRange(0, 0)"""
new1 = """        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)"""
text = text.replace(old1, new1)

old2 = """        if state == 0:
            if not self.has_started:
                self.has_started = True
                self.info_label.setText("Reproduciendo texto...")
                self.progress.hide()
        else:
            if self.has_started:
                self.timer.stop()
                self.close()
                return

            self.ticks_without_speech += 1

            if self.ticks_without_speech >= 50:
                self.info_label.setText("No se pudo iniciar la voz.")
                self.progress.hide()
                self.timer.stop()
                QTimer.singleShot(1500, self.close)"""
new2 = """        if state == 2:
            if not self.has_started:
                self.has_started = True
                self.info_label.setText("Reproduciendo texto...")
                self.progress.hide()
        elif state == 1 and self.has_started:
            self.timer.stop()
            self.close()
        else:
            if not self.has_started:
                self.ticks_without_speech += 1
                self.progress.setValue(
                    min(95, self.ticks_without_speech * 4)
                )

                if self.ticks_without_speech >= 50:
                    self.info_label.setText("No se pudo iniciar la voz.")
                    self.progress.hide()
                    self.timer.stop()
                    QTimer.singleShot(1500, self.close)"""
text = text.replace(old2, new2)

path.write_text(text, encoding="utf-8")
print("Barra de descarga gradual lista.")
