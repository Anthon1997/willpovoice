from pathlib import Path

path = Path("ui") / "main_window.py"
text = path.read_text(encoding="utf-8")

old_add = """    def _add_to_history(self, text: str) -> None:
        items = self.settings.get("history", [])

        if text in items:
            items.remove(text)

        items.insert(0, text)
        self.settings["history"] = items[: self.MAX_HISTORY]
        self._load_history()"""

new_add = """    def _add_to_history(
        self, text: str, file_path: str | None = None
    ) -> None:
        items = self.settings.get("history", [])

        kind = "text"
        label = "Texto manual"
        ext = "txt"

        if file_path:
            kind = "file"
            p = Path(file_path)
            label = p.name
            ext = p.suffix.lstrip(".").lower() or "txt"

        entry = {
            "content": text,
            "kind": kind,
            "label": label,
            "ext": ext,
        }

        items = [
            it if isinstance(it, dict) else {
                "content": it, "kind": "text", "label": "Texto manual", "ext": "txt"
            }
            for it in items
        ]

        items = [it for it in items if it.get("content") != text]
        items.insert(0, entry)
        self.settings["history"] = items[: self.MAX_HISTORY]
        self._load_history()"""

text = text.replace(old_add, new_add)

old_load = """    def _load_history(self) -> None:
        self._history_full = list(self.settings.get("history", []))
        self.history_combo.clear()

        for item in self._history_full:
            display = item if len(item) <= 80 else item[:77] + "..."
            self.history_combo.addItem(display)"""

new_load = """    def _load_history(self) -> None:
        raw = self.settings.get("history", [])
        self._history_full = []

        for it in raw:
            if isinstance(it, dict):
                self._history_full.append(it)
            else:
                self._history_full.append(
                    {"content": it, "kind": "text", "label": "Texto manual", "ext": "txt"}
                )

        self.history_combo.clear()

        color_map = {
            "pdf": "#e02020",
            "doc": "#185abd",
            "docx": "#2b7de9",
            "rtf": "#f2a33c",
            "html": "#9b59f6",
            "htm": "#9b59f6",
            "txt": "#4da3ff",
            "md": "#4da3ff",
            "log": "#4da3ff",
            "csv": "#4da3ff",
        }

        label_map = {
            "pdf": "PDF",
            "doc": "DOC",
            "docx": "DOC",
            "rtf": "RTF",
            "html": "WEB",
            "htm": "WEB",
            "txt": "TXT",
            "md": "MD",
            "log": "LOG",
            "csv": "CSV",
        }

        for entry in self._history_full:
            ext = entry.get("ext", "txt").lower()
            color = color_map.get(ext, "#4da3ff")
            badge = label_map.get(ext, ext.upper()[:3])
            icon = self._format_icon(color, badge)
            display = entry.get("label", "Sin titulo")
            self.history_combo.addItem(icon, display)"""

text = text.replace(old_load, new_load)

old_on = """    def on_history_selected(self, index: int) -> None:
        if 0 <= index < len(self._history_full):
            self.text_edit.setPlainText(self._history_full[index])"""

new_on = """    def on_history_selected(self, index: int) -> None:
        if 0 <= index < len(self._history_full):
            entry = self._history_full[index]
            self.text_edit.setPlainText(entry.get("content", ""))"""

text = text.replace(old_on, new_on)

old_open = """        try:
            content = Path(path).read_text(encoding="utf-8", errors="ignore")
            self.text_edit.setPlainText(content)
            self.statusBar().showMessage(f"Archivo cargado: {path}")"""

new_open = """        try:
            content = Path(path).read_text(encoding="utf-8", errors="ignore")
            self.text_edit.setPlainText(content)
            self._add_to_history(content, file_path=path)
            self.statusBar().showMessage(f"Archivo cargado: {path}")"""

text = text.replace(old_open, new_open)

old_open_doc = """        try:
            content = file_reader.extract_text(Path(path_str))
        except Exception as exc:
            QMessageBox.warning(
                self, "WillpoVoice", f"No se pudo leer el archivo: {exc}"
            )
            return

        self.text_edit.setPlainText(content)
        self.statusBar().showMessage(
            f"Documento cargado: {Path(path_str).name}"
        )"""

new_open_doc = """        try:
            content = file_reader.extract_text(Path(path_str))
        except Exception as exc:
            QMessageBox.warning(
                self, "WillpoVoice", f"No se pudo leer el archivo: {exc}"
            )
            return

        self.text_edit.setPlainText(content)
        self._add_to_history(content, file_path=path_str)
        self.statusBar().showMessage(
            f"Documento cargado: {Path(path_str).name}"
        )"""

text = text.replace(old_open_doc, new_open_doc)

path.write_text(text, encoding="utf-8")
print("Historial con iconos de formato listo.")
