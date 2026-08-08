from pathlib import Path

path = Path("ui") / "main_window.py"
text = path.read_text(encoding="utf-8")

text = text.replace(
    """    def _add_to_history(
        self, text: str, file_path: str | None = None
    ) -> None:
        items = self.settings.get("history", [])""",
    """    def _add_to_history(
        self, text: str, file_path: str | None = None
    ) -> None:
        text = (text or "").strip()

        if not text:
            return

        items = self.settings.get("history", [])""",
)

text = text.replace(
    """        self.text_edit.setPlainText(content)
        self._add_to_history(content, file_path=path_str)""",
    """        self.text_edit.setPlainText(content)
        self._loaded_file_path = path_str
        self._add_to_history(content, file_path=path_str)""",
)

text = text.replace(
    """            self.text_edit.setPlainText(content)
            self._add_to_history(content, file_path=path)""",
    """            self.text_edit.setPlainText(content)
            self._loaded_file_path = path
            self._add_to_history(content, file_path=path)""",
)

text = text.replace(
    "self._add_to_history(text)",
    'self._add_to_history(text, file_path=getattr(self, "_loaded_file_path", None))',
)
text = text.replace(
    "self._add_to_history(self.text_edit.toPlainText().strip())",
    'self._add_to_history(self.text_edit.toPlainText(), file_path=getattr(self, "_loaded_file_path", None))',
)

path.write_text(text, encoding="utf-8")
print("Historial sin duplicados listo.")
