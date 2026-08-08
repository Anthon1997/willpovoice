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

if "from core import license_manager" not in text:
    if insert_before("class MainWindow(QMainWindow):", "from core import license_manager\n\n\n"):
        report.append("import license_manager")

if "class LicenseDialog" not in text:
    dialog = '''class LicenseDialog(QDialog):
    def __init__(self, parent, machine_id: str, days_left: int):
        super().__init__(parent)
        self.activated_key = ""
        self.trial_accepted = False
        self.machine_id = machine_id

        self.setWindowTitle("WillpoVoice - Licencia")
        self.setModal(True)
        self.setFixedWidth(430)

        layout = QVBoxLayout(self)

        title = QLabel("WillpoVoice")
        title.setStyleSheet("font-size: 20px; font-weight: 700;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        info = QLabel(f"ID de esta maquina: {machine_id}")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(info)

        if days_left >= 0:
            trial = QLabel(f"Prueba gratuita: {days_left} dia(s) restante(s)")
        else:
            trial = QLabel("El periodo de prueba ha terminado.")

        trial.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(trial)

        layout.addWidget(QLabel("Ingresa tu clave de licencia:"))

        self.key_edit = QLineEdit()
        self.key_edit.setPlaceholderText("WVP-XXXX-XXXX-XXXX-XXXX")
        layout.addWidget(self.key_edit)

        row = QHBoxLayout()

        activate = QPushButton("Activar")
        activate.clicked.connect(self.try_activate)
        row.addWidget(activate)

        buy = QPushButton("Comprar por WhatsApp")
        buy.clicked.connect(self.open_whatsapp)
        row.addWidget(buy)

        if days_left >= 0:
            trial_btn = QPushButton("Continuar en prueba")
            trial_btn.clicked.connect(self.accept_trial)
            row.addWidget(trial_btn)

        layout.addLayout(row)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #e05252;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.error_label)

    def try_activate(self) -> None:
        key = self.key_edit.text()

        if license_manager.validate_key(key, self.machine_id):
            self.activated_key = "".join(key.strip().upper().split())
            self.accept()
        else:
            self.error_label.setText("Clave invalida para esta maquina.")

    def open_whatsapp(self) -> None:
        msg = quote(
            f"Hola, quiero una licencia de WillpoVoice. "
            f"Mi ID de maquina: {self.machine_id}"
        )
        QDesktopServices.openUrl(QUrl(f"https://wa.me/51923073560?text={msg}"))

    def accept_trial(self) -> None:
        self.trial_accepted = True
        self.accept()


'''
    if insert_before("class MainWindow(QMainWindow):", dialog):
        report.append("LicenseDialog")

if "def _check_license" not in text:
    methods = '''    def showEvent(self, event):
        super().showEvent(event)

        if not getattr(self, "_license_checked", False):
            self._license_checked = True

            if not self._check_license():
                self.close()

            return

    def _check_license(self) -> bool:
        state, days_left = license_manager.check_status()

        if state == "licensed":
            self.statusBar().showMessage("Version licenciada.")
            return True

        dialog = LicenseDialog(
            self,
            license_manager.get_machine_id(),
            days_left if state == "trial" else -1,
        )
        dialog.exec()

        if dialog.activated_key:
            data = license_manager.load_data()
            data["license_key"] = dialog.activated_key
            license_manager.save_data(data)
            self.statusBar().showMessage("Licencia activada. Gracias!")
            return True

        return dialog.trial_accepted

'''
    if insert_before("    def _apply_theme", methods):
        report.append("metodos de licencia")

if "def show_help" not in text:
    block = '''    def show_help(self) -> None:
        wizard = HelpWizard(self)
        wizard.exec()

'''
    ok = insert_before("    def showEvent(self, event):", block)
    if not ok:
        ok = insert_before("    def _check_license", block)
    if not ok:
        ok = insert_before("    def _apply_theme", block)
    if ok:
        report.append("show_help")

path.write_text(text, encoding="utf-8")
print("Reparaciones:", report if report else "nada que reparar")
