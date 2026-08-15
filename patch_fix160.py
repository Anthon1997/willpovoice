from pathlib import Path
import re, ast

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

new_dialog = '''class LicenseDialog(QDialog):
    def __init__(self, parent, machine_id: str, days_left: int):
        super().__init__(parent)
        self.activated_key = ""
        self.trial_accepted = False
        self.machine_id = machine_id

        BG = "#0d1220"
        CARD = "#141b30"
        BORDER = "#232f4b"
        TEXT = "#eef2fa"
        MUTED = "#8fa0bd"
        PURPLE = "#7c5cff"
        GOLD = "#f5b301"
        RED = "#ef4444"
        GREEN = "#10b981"

        self.setWindowTitle("WillpoVoice - Licencia")
        self.setModal(True)
        self.setFixedWidth(460)
        self.setStyleSheet(
            f"LicenseDialog {{ background: {BG}; }}"
            f" QLabel {{ background: transparent; color: {TEXT}; }}"
            f" QLineEdit {{ background: {CARD}; color: {TEXT};"
            f" border: 1px solid {BORDER}; border-radius: 10px;"
            " padding: 10px 12px; font-size: 12px; }"
            f" QLineEdit:focus {{ border-color: {PURPLE}; }}"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 22, 28, 22)
        layout.setSpacing(8)

        logo = QLabel()
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = MainWindow._resource_path(
            Path("assets") / "icons" / "logo.png")
        if not logo_path.exists():
            logo_path = MainWindow._resource_path(
                Path("assets") / "icons" / "icon.ico")
        if logo_path.exists():
            logo.setPixmap(QPixmap(str(logo_path)).scaledToHeight(
                52, Qt.TransformationMode.SmoothTransformation))
        layout.addWidget(logo)

        title = QLabel("WillpoVoice")
        title.setStyleSheet("font-size: 22px; font-weight: 800;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Convierte texto en voz con voces naturales")
        subtitle.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(6)

        id_box = QFrame()
        id_box.setStyleSheet(
            f"QFrame {{ background: {CARD}; border: 1px solid {BORDER};"
            " border-radius: 10px; }"
        )
        idl = QHBoxLayout(id_box)
        idl.setContentsMargins(12, 8, 12, 8)
        id_label = QLabel(f"ID de esta maquina:  {machine_id}")
        id_label.setStyleSheet(
            f"color: {MUTED}; font-size: 11px; font-family: Consolas;")
        id_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse)
        id_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        idl.addWidget(id_label)
        layout.addWidget(id_box)

        if days_left >= 0:
            trial = QLabel(f"Prueba gratuita: {days_left} dia(s) restante(s)")
            trial.setStyleSheet(
                f"color: {GOLD}; font-size: 11px; font-weight: 600;")
        else:
            trial = QLabel("El periodo de prueba ha terminado.")
            trial.setStyleSheet(
                f"color: {RED}; font-size: 11px; font-weight: 600;")
        trial.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(trial)

        layout.addSpacing(4)

        key_label = QLabel("Ingresa tu clave de licencia:")
        key_label.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
        layout.addWidget(key_label)

        self.key_edit = QLineEdit()
        self.key_edit.setPlaceholderText(
            "WVP-XXXX-XXXX-XXXX-XXXX  o  WVP2-...")
        layout.addWidget(self.key_edit)

        activate = QPushButton("Activar")
        activate.setCursor(Qt.CursorShape.PointingHandCursor)
        activate.setStyleSheet(
            "QPushButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f" stop:0 #5b3df0, stop:1 {PURPLE}); color: white;"
            " border: none; border-radius: 10px; padding: 10px 18px;"
            " font-size: 12px; font-weight: 700; }"
            " QPushButton:hover { background: #8d75ff; }"
        )
        activate.clicked.connect(self.try_activate)
        layout.addWidget(activate)

        row = QHBoxLayout()
        row.setSpacing(8)
        buy = QPushButton("Comprar por WhatsApp")
        buy.setCursor(Qt.CursorShape.PointingHandCursor)
        buy.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {GREEN};"
            f" border: 1px solid {GREEN}; border-radius: 10px;"
            " padding: 9px 12px; font-size: 11px; font-weight: 600; }"
            " QPushButton:hover { background: rgba(16,185,129,40); }"
        )
        buy.clicked.connect(self.open_whatsapp)
        row.addWidget(buy)

        if days_left >= 0:
            trial_btn = QPushButton("Continuar en prueba")
            trial_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            trial_btn.setStyleSheet(
                f"QPushButton {{ background: transparent; color: {MUTED};"
                f" border: 1px solid {BORDER}; border-radius: 10px;"
                " padding: 9px 12px; font-size: 11px; font-weight: 600; }"
                f" QPushButton:hover {{ color: {TEXT}; border-color: {MUTED}; }}"
            )
            trial_btn.clicked.connect(self.accept_trial)
            row.addWidget(trial_btn)
        layout.addLayout(row)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet(f"color: {RED}; font-size: 11px;")
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

if re.search(r"class LicenseDialog\(QDialog\):", t):
    t = re.sub(
        r"class LicenseDialog\(QDialog\):[\s\S]*?(?=\nPREMIUM_PHOTOS|\nclass MainWindow)",
        new_dialog,
        t,
        count=1,
    )
    print("LicenseDialog rediseñado con estilo moderno.")
else:
    print("AVISO: LicenseDialog no encontrado.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
