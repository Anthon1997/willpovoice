from pathlib import Path

path = Path("ui") / "main_window.py"
text = path.read_text(encoding="utf-8")

text = text.replace("""    def showEvent(self, event):
        super().showEvent(event)

        if not getattr(self, "_license_checked", False):
            self._license_checked = True

            if not self._check_license():
                self.close()

            return

""", "")

start = text.find("    def _check_license")
end = text.find("    def _apply_theme")
if start != -1 and end != -1 and end > start:
    text = text[:start] + text[end:]

start = text.find("class LicenseDialog")
if start != -1:
    nxt = text.find("\nclass ", start + 1)
    if nxt != -1:
        text = text[:start] + text[nxt + 1:]

text = text.replace("from core import license_manager\n", "")

path.write_text(text, encoding="utf-8")
print("Licencias eliminadas de la interfaz.")
