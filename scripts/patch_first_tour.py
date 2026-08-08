from pathlib import Path

path = Path("ui") / "main_window.py"
text = path.read_text(encoding="utf-8")

def insert_before(marker, block):
    global text
    i = text.find(marker)
    if i == -1:
        return False
    text = text[:i] + block + text[i:]
    return True

report = []

if "def _launch_first_tour" not in text:
    block = '''    def _launch_first_tour(self) -> None:
        self.settings["tour_seen"] = True

        for name in ("_save_settings", "save_settings"):
            fn = getattr(self, name, None)

            if callable(fn):
                try:
                    fn()
                except Exception:
                    pass

                break

        self.show_help()

    def showEvent(self, event):
        super().showEvent(event)

        if not getattr(self, "_tour_pending_checked", False):
            self._tour_pending_checked = True

            if not self.settings.get("tour_seen", False):
                QTimer.singleShot(400, self._launch_first_tour)

'''
    if insert_before("    def show_help(self) -> None:", block):
        report.append("tour automatico")

path.write_text(text, encoding="utf-8")
print("Cambios:", report if report else "nada que hacer")
