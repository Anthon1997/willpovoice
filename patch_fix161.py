from pathlib import Path
import re, ast

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

helper = '''def _lic_pix(kind, color, s=18):
    from PySide6.QtCore import QPointF, QRectF
    from PySide6.QtGui import QPolygonF, QBrush
    import math
    pix = QPixmap(s, s)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    c = QColor(color)
    p.setPen(QPen(c, 1.6))
    m = s / 18.0
    if kind == "monitor":
        p.drawRoundedRect(QRectF(2*m, 3*m, 14*m, 10*m), 2, 2)
        p.drawLine(QPointF(9*m, 13*m), QPointF(9*m, 15*m))
        p.drawLine(QPointF(5*m, 15.5*m), QPointF(13*m, 15.5*m))
    elif kind == "copy":
        p.drawRoundedRect(QRectF(6*m, 6*m, 10*m, 10*m), 2, 2)
        p.drawRoundedRect(QRectF(3*m, 3*m, 10*m, 10*m), 2, 2)
    elif kind == "crown":
        pts = [QPointF(3*m, 13*m), QPointF(3*m, 6*m), QPointF(6.5*m, 9*m),
               QPointF(9*m, 4*m), QPointF(11.5*m, 9*m), QPointF(15*m, 6*m),
               QPointF(15*m, 13*m)]
        p.drawPolyline(QPolygonF(pts))
        p.drawLine(QPointF(3*m, 15*m), QPointF(15*m, 15*m))
    elif kind == "key":
        p.drawEllipse(QRectF(3*m, 10*m, 6*m, 6*m))
        p.drawLine(QPointF(8*m, 11*m), QPointF(15*m, 4*m))
        p.drawLine(QPointF(12*m, 7*m), QPointF(14*m, 9*m))
    elif kind == "info":
        p.drawEllipse(QRectF(2*m, 2*m, 14*m, 14*m))
        p.setBrush(QBrush(c))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(9*m, 5.5*m), 1.1*m, 1.1*m)
        p.setPen(QPen(c, 1.6))
        p.drawLine(QPointF(9*m, 8*m), QPointF(9*m, 13*m))
    elif kind == "shield":
        path = QPainterPath()
        path.moveTo(9*m, 2*m)
        path.lineTo(15*m, 4.5*m)
        path.lineTo(15*m, 9*m)
        path.cubicTo(15*m, 13*m, 12*m, 15.5*m, 9*m, 16.5*m)
        path.cubicTo(6*m, 15.5*m, 3*m, 13*m, 3*m, 9*m)
        path.closeSubpath()
        p.drawPath(path)
        p.drawLine(QPointF(6.5*m, 9*m), QPointF(8.5*m, 11*m))
        p.drawLine(QPointF(8.5*m, 11*m), QPointF(12*m, 6.5*m))
    elif kind == "wa":
        p.drawEllipse(QRectF(2*m, 2*m, 14*m, 14*m))
        p.drawLine(QPointF(5*m, 16*m), QPointF(6*m, 13*m))
        p.drawArc(QRectF(6*m, 6*m, 6*m, 6*m), 30*16, 120*16)
    elif kind == "flask":
        p.drawLine(QPointF(7*m, 2*m), QPointF(7*m, 7*m))
        p.drawLine(QPointF(11*m, 2*m), QPointF(11*m, 7*m))
        p.drawLine(QPointF(7*m, 7*m), QPointF(4*m, 14*m))
        p.drawLine(QPointF(11*m, 7*m), QPointF(14*m, 14*m))
        p.drawLine(QPointF(4*m, 14*m), QPointF(14*m, 14*m))
        p.drawLine(QPointF(5.5*m, 11*m), QPointF(12.5*m, 11*m))
    elif kind == "lock":
        p.drawRoundedRect(QRectF(4*m, 8*m, 10*m, 8*m), 2, 2)
        p.drawArc(QRectF(6*m, 3*m, 6*m, 8*m), 0, 180*16)
    elif kind == "help":
        p.drawEllipse(QRectF(2*m, 2*m, 14*m, 14*m))
        p.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        p.drawText(QRectF(2*m, 1*m, 14*m, 15*m), Qt.AlignmentFlag.AlignCenter, "?")
    elif kind == "wave":
        for i, h in enumerate([4, 8, 12, 8, 4]):
            x = (3 + i * 3) * m
            p.drawLine(QPointF(x, (9 - h / 2)*m), QPointF(x, (9 + h / 2)*m))
    elif kind == "bolt":
        poly = QPolygonF([QPointF(10*m, 2*m), QPointF(5*m, 10*m), QPointF(9*m, 10*m),
                          QPointF(8*m, 16*m), QPointF(13*m, 8*m), QPointF(9*m, 8*m)])
        p.drawPolyline(poly)
    elif kind == "star":
        pts = []
        for i in range(10):
            ang = math.radians(-90 + i * 36)
            r = 7*m if i % 2 == 0 else 3*m
            pts.append(QPointF(9*m + r*math.cos(ang), 9*m + r*math.sin(ang)))
        p.drawPolyline(QPolygonF(pts))
    elif kind == "x":
        p.drawLine(QPointF(5*m, 5*m), QPointF(13*m, 13*m))
        p.drawLine(QPointF(13*m, 5*m), QPointF(5*m, 13*m))
    p.end()
    return pix


'''

new_dialog = helper + '''class LicenseDialog(QDialog):
    def __init__(self, parent, machine_id: str, days_left: int):
        super().__init__(parent)
        self.activated_key = ""
        self.trial_accepted = False
        self.machine_id = machine_id

        BG = "#0b0f17"
        PANEL = "#0d1117"
        CARD = "#141922"
        BORDER = "#242b38"
        TEXT = "#e6edf3"
        MUTED = "#8b949e"
        PURPLE = "#7c5cff"
        BLUE = "#58a6ff"
        GOLD = "#f0a020"
        RED = "#ef4444"
        GREEN = "#2ea043"

        self.setWindowTitle("WillpoVoice - Licencia")
        self.setModal(True)
        self.setFixedSize(1080, 780)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setStyleSheet(f"LicenseDialog {{ background: {BG}; }}")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ---------- barra de titulo ----------
        bar = QFrame()
        bar.setFixedHeight(46)
        bar.setStyleSheet(
            f"QFrame {{ background: {PANEL}; border-bottom: 1px solid {BORDER}; }}")
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(14, 0, 8, 0)
        bl.setSpacing(10)
        blogo = QLabel()
        logo_p = MainWindow._resource_path(Path("assets") / "icons" / "logo.png")
        if not logo_p.exists():
            logo_p = MainWindow._resource_path(Path("assets") / "icons" / "icon.ico")
        if logo_p.exists():
            blogo.setPixmap(QPixmap(str(logo_p)).scaledToHeight(
                20, Qt.TransformationMode.SmoothTransformation))
        bl.addWidget(blogo)
        btitle = QLabel("WillpoVoice - Licencia")
        btitle.setStyleSheet(f"color: {TEXT}; font-size: 13px; font-weight: 600;")
        bl.addWidget(btitle)
        bl.addStretch()
        close_btn = QPushButton()
        close_btn.setFixedSize(36, 36)
        close_btn.setIcon(QIcon(_lic_pix("x", TEXT, 16)))
        close_btn.setIconSize(QSize(16, 16))
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

        # ---------- panel izquierdo ----------
        left = QFrame()
        left.setFixedWidth(300)
        left.setStyleSheet(
            f"QFrame {{ background: #0a0d13; border-right: 1px solid {BORDER}; }}")
        lv = QVBoxLayout(left)
        lv.setContentsMargins(0, 0, 0, 0)
        lv.setSpacing(14)
        img = QLabel()
        img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img.setMinimumHeight(360)
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
        pcard.setStyleSheet(
            f"QFrame {{ background: #12151d; border: 1px solid {BORDER};"
            " border-radius: 12px; }")
        pv = QVBoxLayout(pcard)
        pv.setContentsMargins(16, 16, 16, 16)
        pv.setSpacing(14)
        pt = QLabel(
            f'WillpoVoice <span style="color:#8b7bff; font-weight:700;">'
            'Premium</span>')
        pt.setStyleSheet(f"color: {TEXT}; font-size: 14px; font-weight: 700;")
        pv.addWidget(pt)
        feats = [
            ("wave", "Voces naturales\\nde alta calidad"),
            ("bolt", "Conversiones rapidas\\ne ilimitadas"),
            ("shield", "Soporte prioritario\\ny actualizaciones"),
            ("star", "Nuevas voces\\ntodas las semanas"),
        ]
        for kind, txt in feats:
            row = QHBoxLayout()
            row.setSpacing(12)
            ic = QLabel()
            ic.setPixmap(_lic_pix(kind, "#c9d1d9", 18))
            row.addWidget(ic, 0, Qt.AlignmentFlag.AlignTop)
            lb = QLabel(txt)
            lb.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
            row.addWidget(lb)
            row.addStretch()
            pv.addLayout(row)
        lv.addWidget(pcard, 0)
        lv.addSpacing(14)
        body.addWidget(left)

        # ---------- panel derecho ----------
        right = QWidget()
        right.setStyleSheet("background: transparent;")
        rv = QVBoxLayout(right)
        rv.setContentsMargins(40, 26, 40, 16)
        rv.setSpacing(12)

        logo = QLabel()
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if logo_p.exists():
            logo.setPixmap(QPixmap(str(logo_p)).scaledToHeight(
                76, Qt.TransformationMode.SmoothTransformation))
        rv.addWidget(logo)

        title = QLabel(
            '<span style="color:#ffffff; font-weight:800;">Willpo</span>'
            '<span style="color:#8b7bff; font-weight:800;">Voice</span>')
        title.setStyleSheet("font-size: 34px; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rv.addWidget(title)

        subtitle = QLabel("Convierte texto en voz con voces naturales")
        subtitle.setStyleSheet(f"color: {MUTED}; font-size: 13px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rv.addWidget(subtitle)
        rv.addSpacing(6)

        id_card = QFrame()
        id_card.setFixedHeight(52)
        id_card.setStyleSheet(
            f"QFrame {{ background: {CARD}; border: 1px solid {BORDER};"
            " border-radius: 10px; }")
        il = QHBoxLayout(id_card)
        il.setContentsMargins(16, 0, 10, 0)
        il.setSpacing(12)
        mic = QLabel()
        mic.setPixmap(_lic_pix("monitor", PURPLE, 18))
        il.addWidget(mic)
        idl = QLabel("ID de esta maquina:")
        idl.setStyleSheet(f"color: {TEXT}; font-size: 13px;")
        il.addWidget(idl)
        il.addStretch()
        idv = QLabel(machine_id)
        idv.setStyleSheet(
            f"color: {BLUE}; font-size: 15px; font-weight: 700;")
        il.addWidget(idv)
        copy_btn = QPushButton()
        copy_btn.setFixedSize(32, 32)
        copy_btn.setIcon(QIcon(_lic_pix("copy", MUTED, 16)))
        copy_btn.setIconSize(QSize(16, 16))
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
        trial_card.setFixedHeight(52)
        trial_card.setStyleSheet(
            f"QFrame {{ background: {CARD}; border: 1px solid {BORDER};"
            " border-radius: 10px; }")
        tl = QHBoxLayout(trial_card)
        tl.setContentsMargins(16, 0, 16, 0)
        tl.addStretch()
        cr = QLabel()
        cr.setPixmap(_lic_pix("crown", GOLD, 18))
        tl.addWidget(cr)
        if days_left >= 0:
            tr_txt = (
                f'Prueba gratuita:  <span style="color:{GOLD};'
                f' font-weight:700;">{days_left} dia(s) restante(s)</span>')
        else:
            tr_txt = (
                f'<span style="color:{RED}; font-weight:700;">'
                'El periodo de prueba ha terminado.</span>')
        trl = QLabel(tr_txt)
        trl.setStyleSheet(f"color: {TEXT}; font-size: 13px;")
        tl.addWidget(trl)
        tl.addStretch()
        rv.addWidget(trial_card)
        rv.addSpacing(2)

        kl = QLabel("Ingresa tu clave de licencia:")
        kl.setStyleSheet(f"color: {TEXT}; font-size: 13px;")
        rv.addWidget(kl)

        key_wrap = QFrame()
        key_wrap.setFixedHeight(48)
        key_wrap.setStyleSheet(
            "QFrame { background: transparent; border: none; }")
        kw = QHBoxLayout(key_wrap)
        kw.setContentsMargins(0, 0, 0, 0)
        self.key_edit = QLineEdit()
        self.key_edit.setPlaceholderText(
            "WVP-XXXX-XXXX-XXXX-XXXX  o  WVP2-...")
        self.key_edit.setStyleSheet(
            f"QLineEdit {{ background: #10141c; color: {TEXT};"
            f" border: 1.5px solid {PURPLE}; border-radius: 10px;"
            " padding: 0 14px 0 44px; font-size: 13px; }"
        )
        key_icon = QLabel(key_wrap)
        key_icon.setPixmap(_lic_pix("key", PURPLE, 18))
        key_icon.setGeometry(16, 15, 18, 18)
        kw.addWidget(self.key_edit)
        rv.addWidget(key_wrap)

        hint_row = QHBoxLayout()
        hint_row.setSpacing(8)
        hi = QLabel()
        hi.setPixmap(_lic_pix("info", MUTED, 15))
        hint_row.addWidget(hi)
        self.hint_label = QLabel(
            "Puedes encontrar tu clave en el correo de compra.")
        self.hint_label.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
        hint_row.addWidget(self.hint_label)
        hint_row.addStretch()
        rv.addLayout(hint_row)
        rv.addSpacing(4)

        activate = QPushButton("Activar Licencia")
        activate.setFixedHeight(48)
        activate.setCursor(Qt.CursorShape.PointingHandCursor)
        activate.setIcon(QIcon(_lic_pix("shield", "#ffffff", 20)))
        activate.setIconSize(QSize(20, 20))
        activate.setStyleSheet(
            "QPushButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            " stop:0 #6d5df0, stop:0.5 #7c5cff, stop:1 #6d5df0);"
            " color: white; border: none; border-radius: 10px;"
            " font-size: 15px; font-weight: 700; }"
            " QPushButton:hover { background: #8d75ff; }"
        )
        activate.clicked.connect(self.try_activate)
        rv.addWidget(activate)

        row2 = QHBoxLayout()
        row2.setSpacing(12)
        buy = QPushButton("Comprar por WhatsApp")
        buy.setFixedHeight(46)
        buy.setCursor(Qt.CursorShape.PointingHandCursor)
        buy.setIcon(QIcon(_lic_pix("wa", GREEN, 18)))
        buy.setIconSize(QSize(18, 18))
        buy.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {GREEN};"
            f" border: 1px solid {GREEN}; border-radius: 10px;"
            " font-size: 13px; font-weight: 600; }}"
            " QPushButton:hover { background: rgba(46,160,67,35); }"
        )
        buy.clicked.connect(self.open_whatsapp)
        row2.addWidget(buy, 1)
        if days_left >= 0:
            trial_btn = QPushButton("Continuar en prueba")
            trial_btn.setFixedHeight(46)
            trial_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            trial_btn.setIcon(QIcon(_lic_pix("flask", "#c9d1d9", 18)))
            trial_btn.setIconSize(QSize(18, 18))
            trial_btn.setStyleSheet(
                f"QPushButton {{ background: transparent; color: #c9d1d9;"
                f" border: 1px solid {BORDER}; border-radius: 10px;"
                " font-size: 13px; font-weight: 600; }}"
                f" QPushButton:hover {{ border-color: {MUTED}; }}"
            )
            trial_btn.clicked.connect(self.accept_trial)
            row2.addWidget(trial_btn, 1)
        rv.addLayout(row2)
        rv.addSpacing(2)

        footer = QHBoxLayout()
        footer.setSpacing(8)
        lo = QLabel()
        lo.setPixmap(_lic_pix("lock", MUTED, 14))
        footer.addWidget(lo)
        fl = QLabel("Tu informacion esta 100% segura y encriptada.")
        fl.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
        footer.addWidget(fl)
        footer.addStretch()
        help_btn = QPushButton("Necesitas ayuda?")
        help_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        help_btn.setIcon(QIcon(_lic_pix("help", BLUE, 15)))
        help_btn.setIconSize(QSize(15, 15))
        help_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {BLUE};"
            " border: none; font-size: 12px; font-weight: 600; }}"
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
        self.hint_label.setStyleSheet("color: #58a6ff; font-size: 11px;")

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
            self.hint_label.setStyleSheet("color: #ef4444; font-size: 11px;")

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

t = re.sub(
    r"(?:def _lic_pix[\s\S]*?)?class LicenseDialog\(QDialog\):[\s\S]*?"
    r"(?=\nPREMIUM_PHOTOS|\nclass MainWindow)",
    new_dialog,
    t,
    count=1,
)
print("LicenseDialog recreado tal cual la foto.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
