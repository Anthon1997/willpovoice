from pathlib import Path
import ast

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

start = t.find("class LicenseDialog(QDialog):")
end = t.find("\nPREMIUM_PHOTOS")
print(f"Region dialogo: {start}..{end}")

new_dialog = '''class LicenseDialog(QDialog):
    def __init__(self, parent, machine_id: str, days_left: int):
        super().__init__(parent)
        self.activated_key = ""
        self.trial_accepted = False
        self.machine_id = machine_id

        BG = "#0b0f17"
        PANEL = "#0d1117"
        CARD = "#151a24"
        BORDER = "#262d3a"
        TEXT = "#e6edf3"
        MUTED = "#8b949e"
        PURPLE = "#7c5cff"
        BLUE = "#58a6ff"
        GOLD = "#f0a020"
        RED = "#ef4444"
        GREEN = "#2ea043"

        self.setWindowTitle("WillpoVoice - Licencia")
        self.setModal(True)
        self.setFixedSize(940, 660)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setStyleSheet(
            f"LicenseDialog {{ background: {BG}; }}"
            " QLabel { background: transparent; }"
            " QLineEdit { background: transparent; border: none;"
            f" color: {TEXT}; font-size: 12px; padding: 0; }}"
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        bar = QFrame()
        bar.setObjectName("licbar")
        bar.setFixedHeight(42)
        bar.setStyleSheet(
            f"#licbar {{ background: {PANEL}; border-bottom: 1px solid {BORDER}; }}")
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(12, 0, 6, 0)
        bl.setSpacing(10)
        blogo = QLabel()
        logo_p = MainWindow._resource_path(Path("assets") / "icons" / "logo.png")
        if not logo_p.exists():
            logo_p = MainWindow._resource_path(Path("assets") / "icons" / "icon.ico")
        if logo_p.exists():
            blogo.setPixmap(QPixmap(str(logo_p)).scaledToHeight(
                18, Qt.TransformationMode.SmoothTransformation))
        bl.addWidget(blogo)
        btitle = QLabel("WillpoVoice - Licencia")
        btitle.setStyleSheet(f"color: {TEXT}; font-size: 12px; font-weight: 600;")
        bl.addWidget(btitle)
        bl.addStretch()
        close_btn = QPushButton()
        close_btn.setFixedSize(34, 34)
        close_btn.setIcon(QIcon(_lic_pix("x", TEXT, 14)))
        close_btn.setIconSize(QSize(14, 14))
        close_btn.setStyleSheet(
            "QPushButton { background: transparent; border: none;"
            " border-radius: 8px; }"
            f" QPushButton:hover {{ background: {CARD}; }}"
        )
        close_btn.clicked.connect(self.reject)
        bl.addWidget(close_btn)
        root.addWidget(bar)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        root.addLayout(body, 1)

        left = QFrame()
        left.setObjectName("licleft")
        left.setFixedWidth(260)
        left.setStyleSheet(
            f"#licleft {{ background: #0a0d13; border-right: 1px solid {BORDER}; }}")
        lv = QVBoxLayout(left)
        lv.setContentsMargins(12, 12, 12, 12)
        lv.setSpacing(12)
        img = QLabel()
        img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img.setMinimumHeight(300)
        img.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
        left_img = MainWindow._resource_path(
            Path("assets") / "icons" / "licencia_left.png")
        if not left_img.exists():
            left_img = MainWindow._resource_path(
                Path("assets") / "icons" / "portada.png")
        if left_img.exists():
            img.setPixmap(QPixmap(str(left_img)))
            img.setScaledContents(True)
        lv.addWidget(img, 1)
        pcard = QFrame()
        pcard.setObjectName("pcard")
        pcard.setStyleSheet(
            "#pcard { background: rgba(18,21,29,235);"
            f" border: 1px solid {BORDER}; border-radius: 12px; }}")
        pv = QVBoxLayout(pcard)
        pv.setContentsMargins(14, 14, 14, 14)
        pv.setSpacing(12)
        pt = QLabel(
            f'WillpoVoice <span style="color:#8b7bff; font-weight:700;">'
            'Premium</span>')
        pt.setStyleSheet(f"color: {TEXT}; font-size: 13px; font-weight: 700;")
        pv.addWidget(pt)
        feats = [
            ("wave", "Voces naturales de alta calidad"),
            ("bolt", "Conversiones rapidas e ilimitadas"),
            ("shield", "Soporte prioritario y actualizaciones"),
            ("star", "Nuevas voces todas las semanas"),
        ]
        for kind, txt in feats:
            row = QHBoxLayout()
            row.setSpacing(10)
            ic = QLabel()
            ic.setPixmap(_lic_pix(kind, "#c9d1d9", 16))
            row.addWidget(ic, 0, Qt.AlignmentFlag.AlignTop)
            lb = QLabel(txt)
            lb.setStyleSheet(f"color: {MUTED}; font-size: 10.5px;")
            lb.setWordWrap(True)
            row.addWidget(lb)
            row.addStretch()
            pv.addLayout(row)
        lv.addWidget(pcard, 0)
        body.addWidget(left)

        right = QWidget()
        right.setObjectName("licright")
        right.setStyleSheet(
            "#licright { background: qlineargradient(x1:0,y1:0,x2:0,y2:1,"
            " stop:0 #0d1220, stop:1 #0b0e14); }")
        rv = QVBoxLayout(right)
        rv.setContentsMargins(36, 18, 36, 12)
        rv.setSpacing(10)

        logo = QLabel()
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if logo_p.exists():
            logo.setPixmap(QPixmap(str(logo_p)).scaledToHeight(
                62, Qt.TransformationMode.SmoothTransformation))
        rv.addWidget(logo)

        title = QLabel(
            '<span style="color:#ffffff; font-weight:800;">Willpo</span>'
            '<span style="color:#8b7bff; font-weight:800;">Voice</span>')
        title.setStyleSheet("font-size: 30px; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rv.addWidget(title)

        subtitle = QLabel("Convierte texto en voz con voces naturales")
        subtitle.setStyleSheet(f"color: {MUTED}; font-size: 12px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rv.addWidget(subtitle)
        rv.addSpacing(4)

        id_card = QFrame()
        id_card.setObjectName("idcard")
        id_card.setFixedHeight(46)
        id_card.setStyleSheet(
            f"#idcard {{ background: {CARD}; border: 1px solid {BORDER};"
            " border-radius: 10px; }")
        il = QHBoxLayout(id_card)
        il.setContentsMargins(14, 0, 8, 0)
        il.setSpacing(10)
        mic = QLabel()
        mic.setPixmap(_lic_pix("monitor", PURPLE, 16))
        il.addWidget(mic)
        idl = QLabel("ID de esta maquina:")
        idl.setStyleSheet(f"color: {TEXT}; font-size: 12px;")
        il.addWidget(idl)
        il.addStretch()
        idv = QLabel(machine_id)
        idv.setStyleSheet(f"color: {BLUE}; font-size: 14px; font-weight: 700;")
        il.addWidget(idv)
        copy_btn = QPushButton()
        copy_btn.setFixedSize(30, 30)
        copy_btn.setIcon(QIcon(_lic_pix("copy", MUTED, 14)))
        copy_btn.setIconSize(QSize(14, 14))
        copy_btn.setStyleSheet(
            "QPushButton { background: transparent; border: none;"
            " border-radius: 8px; }"
            f" QPushButton:hover {{ background: {BORDER}; }}"
        )
        copy_btn.setToolTip("Copiar ID de maquina")
        copy_btn.clicked.connect(self._copy_id)
        il.addWidget(copy_btn)
        rv.addWidget(id_card)

        trial_card = QFrame()
        trial_card.setObjectName("trialcard")
        trial_card.setFixedHeight(46)
        trial_card.setStyleSheet(
            f"#trialcard {{ background: {CARD}; border: 1px solid {BORDER};"
            " border-radius: 10px; }")
        tl = QHBoxLayout(trial_card)
        tl.setContentsMargins(14, 0, 14, 0)
        tl.addStretch()
        cr = QLabel()
        cr.setPixmap(_lic_pix("crown", GOLD, 16))
        tl.addWidget(cr)
        if days_left >= 0:
            tr_txt = (
                'Prueba gratuita:  <span style="color:' + GOLD + ';'
                ' font-weight:700;">' + str(days_left) +
                ' dia(s) restante(s)</span>')
        else:
            tr_txt = (
                '<span style="color:' + RED + '; font-weight:700;">'
                'El periodo de prueba ha terminado.</span>')
        trl = QLabel(tr_txt)
        trl.setStyleSheet(f"color: {TEXT}; font-size: 12px;")
        tl.addWidget(trl)
        tl.addStretch()
        rv.addWidget(trial_card)
        rv.addSpacing(2)

        kl = QLabel("Ingresa tu clave de licencia:")
        kl.setStyleSheet(f"color: {TEXT}; font-size: 12px;")
        rv.addWidget(kl)

        keyframe = QFrame()
        keyframe.setObjectName("keyframe")
        keyframe.setFixedHeight(44)
        keyframe.setStyleSheet(
            f"#keyframe {{ background: #10141c; border: 1.5px solid {PURPLE};"
            " border-radius: 10px; }")
        kf = QHBoxLayout(keyframe)
        kf.setContentsMargins(14, 0, 14, 0)
        kf.setSpacing(10)
        kicon = QLabel()
        kicon.setPixmap(_lic_pix("key", PURPLE, 16))
        kf.addWidget(kicon)
        self.key_edit = QLineEdit()
        self.key_edit.setPlaceholderText(
            "WVP-XXXX-XXXX-XXXX-XXXX  o  WVP2-...")
        kf.addWidget(self.key_edit)
        rv.addWidget(keyframe)

        hint_row = QHBoxLayout()
        hint_row.setSpacing(8)
        hi = QLabel()
        hi.setPixmap(_lic_pix("info", MUTED, 14))
        hint_row.addWidget(hi)
        self.hint_label = QLabel(
            "Puedes encontrar tu clave en el correo de compra.")
        self.hint_label.setStyleSheet(f"color: {MUTED}; font-size: 10.5px;")
        hint_row.addWidget(self.hint_label)
        hint_row.addStretch()
        rv.addLayout(hint_row)
        rv.addSpacing(2)

        activate = QPushButton("Activar Licencia")
        activate.setFixedHeight(44)
        activate.setCursor(Qt.CursorShape.PointingHandCursor)
        activate.setIcon(QIcon(_lic_pix("shield", "#ffffff", 18)))
        activate.setIconSize(QSize(18, 18))
        activate.setStyleSheet(
            "QPushButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            " stop:0 #6d5df0, stop:0.5 #7c5cff, stop:1 #6d5df0);"
            " color: white; border: none; border-radius: 10px;"
            " font-size: 14px; font-weight: 700; }"
            " QPushButton:hover { background: #8d75ff; }"
        )
        activate.clicked.connect(self.try_activate)
        rv.addWidget(activate)

        row2 = QHBoxLayout()
        row2.setSpacing(10)
        buy = QPushButton("Comprar por WhatsApp")
        buy.setFixedHeight(42)
        buy.setCursor(Qt.CursorShape.PointingHandCursor)
        buy.setIcon(QIcon(_lic_pix("wa", GREEN, 16)))
        buy.setIconSize(QSize(16, 16))
        buy.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {GREEN};"
            f" border: 1px solid {GREEN}; border-radius: 10px;"
            " font-size: 12px; font-weight: 600; }"
            " QPushButton:hover { background: rgba(46,160,67,35); }"
        )
        buy.clicked.connect(self.open_whatsapp)
        row2.addWidget(buy, 1)
        if days_left >= 0:
            trial_btn = QPushButton("Continuar en prueba")
            trial_btn.setFixedHeight(42)
            trial_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            trial_btn.setIcon(QIcon(_lic_pix("flask", "#c9d1d9", 16)))
            trial_btn.setIconSize(QSize(16, 16))
            trial_btn.setStyleSheet(
                f"QPushButton {{ background: transparent; color: #c9d1d9;"
                f" border: 1px solid {BORDER}; border-radius: 10px;"
                " font-size: 12px; font-weight: 600; }"
                f" QPushButton:hover {{ border-color: {MUTED}; }}"
            )
            trial_btn.clicked.connect(self.accept_trial)
            row2.addWidget(trial_btn, 1)
        rv.addLayout(row2)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {BORDER};")
        rv.addWidget(sep)

        footer = QHBoxLayout()
        footer.setSpacing(8)
        lo = QLabel()
        lo.setPixmap(_lic_pix("lock", MUTED, 13))
        footer.addWidget(lo)
        fl = QLabel("Tu informacion esta 100% segura y encriptada.")
        fl.setStyleSheet(f"color: {MUTED}; font-size: 10.5px;")
        footer.addWidget(fl)
        footer.addStretch()
        help_btn = QPushButton("Necesitas ayuda?")
        help_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        help_btn.setIcon(QIcon(_lic_pix("help", BLUE, 14)))
        help_btn.setIconSize(QSize(14, 14))
        help_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {BLUE};"
            " border: none; font-size: 11px; font-weight: 600; }"
            " QPushButton:hover { text-decoration: underline; }"
        )
        help_btn.clicked.connect(self.open_whatsapp)
        footer.addWidget(help_btn)
        rv.addLayout(footer)
        body.addWidget(right, 1)

        self._drag_pos = None

    def _copy_id(self):
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(self.machine_id)
        self.hint_label.setText("ID copiado al portapapeles.")
        self.hint_label.setStyleSheet("color: #58a6ff; font-size: 10.5px;")

    def mousePressEvent(self, event):
        self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def try_activate(self) -> None:
        key = self.key_edit.text()
        if license_manager.validate_key(key, self.machine_id):
            self.activated_key = "".join(key.strip().upper().split())
            self.accept()
        else:
            self.hint_label.setText("Clave invalida para esta maquina.")
            self.hint_label.setStyleSheet("color: #ef4444; font-size: 10.5px;")

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

if start != -1 and end != -1 and end > start:
    t = t[:start] + new_dialog + t[end:]
    print("Dialogo pulido reemplazado.")
else:
    print("AVISO: anclas no encontradas.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
