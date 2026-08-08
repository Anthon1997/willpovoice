from pathlib import Path

path = Path("ui") / "main_window.py"
text = path.read_text(encoding="utf-8")

text = text.replace(
    "self.export_button.clicked.connect(self.export_wav)",
    "self.export_button.clicked.connect(self._show_export_menu)",
)

anchor = '        self.export_button.setIcon(self._button_icon("save.png"))'
export_menu_block = anchor + '''
        self.export_menu = QMenu(self)
        self.export_menu.setMinimumWidth(260)
        self.export_menu.setStyleSheet(
            "QMenu { background-color: #0e3a46; border: 1px solid #1f4a55; "
            "border-radius: 6px; padding: 0px; } "
            "QMenu::separator { height: 1px; background: #1f5a68; }"
        )
        self._add_menu_row(
            self._audio_icon("#4da3ff", "WAV"),
            "Audio WAV  (.wav, sin compresion)",
            self.export_wav,
            menu=self.export_menu,
        )
        self.export_menu.addSeparator()
        self._add_menu_row(
            self._audio_icon("#f2a33c", "MP3"),
            "Audio MP3  (.mp3, comprimido)",
            self.export_mp3,
            menu=self.export_menu,
        )
        self.export_button.installEventFilter(self)'''
text = text.replace(anchor, export_menu_block)

text = text.replace(
    "    def _add_menu_row(self, icon: QIcon, label: str, handler) -> None:",
    "    def _add_menu_row(self, icon: QIcon, label: str, handler, menu=None) -> None:",
)
text = text.replace(
    "            self.open_menu.close(),",
    "            (menu or self.open_menu).close(),",
)
text = text.replace(
    """        action = QWidgetAction(self.open_menu)
        action.setDefaultWidget(row)
        self.open_menu.addAction(action)""",
    """        target_menu = menu or self.open_menu
        action = QWidgetAction(target_menu)
        action.setDefaultWidget(row)
        target_menu.addAction(action)""",
)

old_filter = """    def eventFilter(self, obj, event):
        if obj is self.open_file_button and event.type() == QEvent.Type.HoverEnter:
            self._show_open_menu()

        return super().eventFilter(obj, event)"""
new_filter = """    def eventFilter(self, obj, event):
        if obj is self.open_file_button and event.type() == QEvent.Type.HoverEnter:
            self._show_open_menu()

        if obj is self.export_button and event.type() == QEvent.Type.HoverEnter:
            self._show_export_menu()

        return super().eventFilter(obj, event)"""
text = text.replace(old_filter, new_filter)

new_methods = '''    def _show_export_menu(self) -> None:
        pos = self.export_button.mapToGlobal(
            QPoint(0, self.export_button.height())
        )
        self.export_menu.popup(pos)

    def _audio_icon(self, color: str, label: str) -> QIcon:
        pix = QPixmap(22, 26)
        pix.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        body = QColor(color)
        dark = body.darker(160)

        page = QPainterPath()
        page.moveTo(4, 1)
        page.lineTo(14, 1)
        page.lineTo(21, 8)
        page.lineTo(21, 22)
        page.quadTo(21, 25, 18, 25)
        page.lineTo(4, 25)
        page.quadTo(1, 25, 1, 22)
        page.lineTo(1, 4)
        page.quadTo(1, 1, 4, 1)
        page.closeSubpath()
        painter.fillPath(page, body)

        fold = QPainterPath()
        fold.moveTo(14, 1)
        fold.lineTo(21, 8)
        fold.lineTo(14, 8)
        fold.closeSubpath()
        painter.fillPath(fold, dark)

        painter.setPen(QColor("white"))
        painter.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
        painter.drawText(
            QRect(1, 6, 21, 9), Qt.AlignmentFlag.AlignCenter, label
        )

        painter.setPen(QPen(QColor("white"), 1.6))
        painter.drawEllipse(6, 19, 5, 4)
        painter.drawLine(11, 21, 11, 14)
        painter.drawLine(11, 14, 15, 13)
        painter.end()

        return QIcon(pix)

    def export_mp3(self) -> None:
        import tempfile

        text = self.text_edit.toPlainText().strip()

        if not text:
            self.statusBar().showMessage("Escribe un texto antes de exportar.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar audio MP3",
            "willpovoice_audio.mp3",
            "Archivos MP3 (*.mp3)",
        )

        if not path:
            return

        if not path.lower().endswith(".mp3"):
            path += ".mp3"

        self._mp3_final_path = path
        temp_wav = tempfile.mktemp(suffix=".wav")

        voice = self.voice_combo.currentText().strip()

        self.statusBar().showMessage("Exportando audio...")

        self.export_progress = QProgressDialog(
            "Exportando audio...", None, 0, 0, self
        )
        self.export_progress.setWindowTitle("Exportando")
        self.export_progress.setModal(True)
        self.export_progress.show()

        self.export_worker = ExportWorker(
            exporter=self.exporter,
            text=text,
            path=temp_wav,
            voice=voice,
            rate=self.rate_slider.value(),
            volume=self.volume_slider.value(),
        )
        self.export_worker.export_ok.connect(self.on_export_ok)
        self.export_worker.export_error.connect(self.on_export_error)
        self.export_worker.start()

'''

if "def export_mp3" not in text:
    i = text.find("    def export_wav(self) -> None:")
    if i != -1:
        text = text[:i] + new_methods + text[i:]

old_ok = '''    def on_export_ok(self, path: str) -> None:
        if getattr(self, "export_progress", None):
            self.export_progress.close()
            self.export_progress = None

        self._add_to_history(self.text_edit.toPlainText().strip())
        self.statusBar().showMessage(f"Audio guardado en: {path}")

        QMessageBox.information(
            self,
            "Exportación exitosa",
            f"El audio se guardó correctamente en:\\n{path}",
        )'''
new_ok = '''    def on_export_ok(self, path: str) -> None:
        if getattr(self, "export_progress", None):
            self.export_progress.close()
            self.export_progress = None

        final_path = path
        mp3_target = getattr(self, "_mp3_final_path", None)

        if mp3_target:
            self._mp3_final_path = None

            try:
                from core.mp3_encoder import wav_to_mp3

                wav_to_mp3(path, mp3_target)
                Path(path).unlink(missing_ok=True)
                final_path = mp3_target
            except Exception as exc:
                QMessageBox.warning(
                    self, "Error", f"No se pudo convertir a MP3:\\n{exc}"
                )
                return

        self._add_to_history(self.text_edit.toPlainText().strip())
        self.statusBar().showMessage(f"Audio guardado en: {final_path}")

        QMessageBox.information(
            self,
            "Exportación exitosa",
            f"El audio se guardó correctamente en:\\n{final_path}",
        )'''
text = text.replace(old_ok, new_ok)

path.write_text(text, encoding="utf-8")
print("Menu Exportar con WAV/MP3 listo.")
