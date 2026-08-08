from pathlib import Path

lm = '''from __future__ import annotations

import getpass
import hashlib
import hmac
import json
import socket
from datetime import datetime
from pathlib import Path

SECRET = b"willpovoice-2026-secret"
TRIAL_DAYS = 7
DATA_DIR = Path.home() / ".willpovoice"
DATA_FILE = DATA_DIR / "license.json"


def get_machine_id() -> str:
    raw = ""

    try:
        import winreg

        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\Microsoft\\Cryptography"
        )
        raw, _ = winreg.QueryValueEx(key, "MachineGuid")
        winreg.CloseKey(key)
    except Exception:
        raw = f"{socket.gethostname()}|{getpass.getuser()}|willpo"

    return hashlib.sha256(raw.encode()).hexdigest()[:8].upper()


def generate_key(machine_id: str) -> str:
    digest = hmac.new(SECRET, machine_id.upper().encode(), hashlib.sha256).hexdigest()
    body = digest[:16].upper()
    return f"WVP-{body[0:4]}-{body[4:8]}-{body[8:12]}-{body[12:16]}"


def validate_key(key: str, machine_id: str) -> bool:
    clean = "".join(key.strip().upper().split())
    return hmac.compare_digest(clean, generate_key(machine_id))


def load_data() -> dict:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_data(data: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def check_status() -> tuple:
    data = load_data()
    machine_id = get_machine_id()

    key = data.get("license_key", "")

    if key and validate_key(key, machine_id):
        return "licensed", 0

    first_run = data.get("first_run", "")
    now = datetime.now()

    if not first_run:
        first_run = now.isoformat()
        data["first_run"] = first_run
        save_data(data)

    days_left = TRIAL_DAYS - (now - datetime.fromisoformat(first_run)).days

    if days_left >= 0:
        return "trial", days_left

    return "expired", 0
'''

Path("core").mkdir(exist_ok=True)
Path("core/license_manager.py").write_text(lm, encoding="utf-8")

text = Path("ui/main_window.py").read_text(encoding="utf-8")
report = []

if "from urllib.parse import quote" not in text:
    text = text.replace("import sys\n", "import sys\nfrom urllib.parse import quote\n", 1)
    report.append("import quote")

if "from core import license_manager" not in text:
    text = text.replace(
        "class MainWindow(QMainWindow):",
        "from core import license_manager\n\n\nclass MainWindow(QMainWindow):",
        1,
    )
    report.append("import license_manager")

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

if "class LicenseDialog" not in text:
    text = text.replace(
        "class MainWindow(QMainWindow):",
        dialog + "class MainWindow(QMainWindow):",
        1,
    )
    report.append("LicenseDialog")

if "def _check_license" not in text:
    methods = '''    def _check_license(self) -> bool:
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
    text = text.replace(
        "    def _apply_theme(self) -> None:",
        methods + "    def _apply_theme(self) -> None:",
        1,
    )
    report.append("_check_license")

if "_license_checked" not in text:
    old_show = "    def showEvent(self, event):\n        super().showEvent(event)\n"
    new_show = old_show + '''
        if not getattr(self, "_license_checked", False):
            self._license_checked = True

            if not self._check_license():
                self.close()
                return
'''
    text = text.replace(old_show, new_show, 1)
    report.append("showEvent licencia")

Path("ui/main_window.py").write_text(text, encoding="utf-8")
print("Licencia integrada:", report)
