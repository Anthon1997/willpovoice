from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")

# Localizar funcion
start = t.find("def _show_no_tokens(self):")
if start == -1:
    print("ERROR: no existe _show_no_tokens"); raise SystemExit(1)

# Ir hasta el siguiente def al mismo nivel
# buscar el patron "\ndef " despues de start
cut = t.find("\ndef ", start + 1)
if cut == -1:
    # si no hay mas defs, usar hasta el final
    cut = len(t)
else:
    # conservar la primera \n del siguiente def
    cut += 1

new_fn = '''def _show_no_tokens(self):
    from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                   QPushButton, QFrame, QSpacerItem, QSizePolicy)
    from PySide6.QtGui import (QDesktopServices, QFont, QColor,
                               QLinearGradient, QPainter, QBrush)
    from PySide6.QtCore import QUrl, QTimer, Qt
    import time

    d = QDialog(self)
    d.setModal(True)
    d.setFixedSize(520, 640)
    d.setWindowTitle("Tokens agotados")
    d.setStyleSheet(
        "QDialog { background: #0a0d12; }"
        "QLabel { background: transparent; }")

    v = QVBoxLayout(d)
    v.setContentsMargins(0, 0, 0, 0)
    v.setSpacing(0)

    # ---------- HEADER con gradiente ----------
    header = QFrame()
    header.setFixedHeight(130)
    header.setStyleSheet(
        "QFrame { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
        " stop:0 #3a1f5c, stop:0.5 #5a2e8c, stop:1 #7c3fa0);"
        " border-radius: 0 0 18px 18px; }")
    hv = QVBoxLayout(header)
    hv.setContentsMargins(28, 18, 28, 16)
    hv.setSpacing(4)
    top = QHBoxLayout()
    top.setSpacing(8)
    warn = QLabel("⚠️")
    warn.setStyleSheet("font-size: 14px; background: transparent;")
    top.addWidget(warn)
    warn_t = QLabel("Acceso limitado")
    warn_t.setStyleSheet(
        "color: rgba(255,255,255,0.85); font-size: 12px;"
        " font-weight: 600; letter-spacing: 1px; text-transform: uppercase;"
        " background: transparent;")
    top.addWidget(warn_t)
    top.addStretch(1)
    hv.addLayout(top)
    title = QLabel("Tokens de prueba agotados")
    title.setStyleSheet(
        "color: white; font-size: 24px; font-weight: 800;"
        " background: transparent;")
    hv.addWidget(title)
    sub = QLabel("Has usado tus 5,000 tokens de bienvenida")
    sub.setStyleSheet(
        "color: rgba(255,255,255,0.75); font-size: 12px;"
        " background: transparent;")
    hv.addWidget(sub)
    v.addWidget(header)

    body = QVBoxLayout()
    body.setContentsMargins(28, 22, 28, 22)
    body.setSpacing(14)

    # ---------- BANNER OFERTA 24H (glow dorado) ----------
    offer = QFrame()
    offer.setStyleSheet(
        "QFrame { background: #14101f;"
        " border: 1.5px solid #6b3fa8;"
        " border-radius: 14px; }")
    ov = QVBoxLayout(offer)
    ov.setContentsMargins(18, 16, 18, 16)
    ov.setSpacing(10)

    # badge
    badge = QLabel("🔥  OFERTA LIMITADA · 24 HORAS")
    badge.setStyleSheet(
        "QLabel { background: #f5b544; color: #1a0f05;"
        " font-size: 10px; font-weight: 800; letter-spacing: 1.5px;"
        " padding: 4px 10px; border-radius: 4px; }")
    badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
    badge.setFixedHeight(22)
    ov.addWidget(badge, 0, Qt.AlignmentFlag.AlignCenter)

    # headline
    oh = QLabel("Tu primer mes Pro al 50% de descuento")
    oh.setStyleSheet(
        "color: #ffffff; font-size: 16px; font-weight: 700;")
    oh.setAlignment(Qt.AlignmentFlag.AlignCenter)
    oh.setWordWrap(True)
    ov.addWidget(oh)

    # precio tachado + nuevo
    price_row = QHBoxLayout()
    price_row.setSpacing(10)
    price_row.addStretch(1)
    old_price = QLabel("S/ 10")
    old_price.setStyleSheet(
        "color: #8b949e; font-size: 20px; font-weight: 500;"
        " text-decoration: line-through;")
    price_row.addWidget(old_price)
    new_price = QLabel("S/ 5")
    new_price.setStyleSheet(
        "color: #f5b544; font-size: 34px; font-weight: 900;")
    price_row.addWidget(new_price)
    price_row.addStretch(1)
    ov.addLayout(price_row)

    # timer grande
    cd = QLabel("00:00:00")
    cd.setAlignment(Qt.AlignmentFlag.AlignCenter)
    cd.setStyleSheet(
        "QLabel { background: #0a0d12; color: #ffffff;"
        " font-size: 26px; font-weight: 800;"
        " font-family: 'Consolas', 'Courier New', monospace;"
        " padding: 10px 18px; border-radius: 8px;"
        " letter-spacing: 3px; }")
    ov.addWidget(cd)
    cd_label = QLabel("tiempo restante para aprovechar la oferta")
    cd_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    cd_label.setStyleSheet(
        "color: #8b949e; font-size: 10px;"
        " text-transform: uppercase; letter-spacing: 1.2px;")
    ov.addWidget(cd_label)

    body.addWidget(offer)

    # ---------- QUE INCLUYE ----------
    inc = QLabel("Al activar tu plan Pro obtienes:")
    inc.setStyleSheet(
        "color: #c9d1d9; font-size: 11px; font-weight: 600;"
        " text-transform: uppercase; letter-spacing: 1px;")
    body.addWidget(inc)

    feats = [
        ("⚡", "20,000 tokens mensuales renovables"),
        ("🎙️", "Todas las voces premium sin restricciones"),
        ("📝", "Hasta 20,000 caracteres por conversión"),
        ("💬", "Soporte directo por Discord"),
    ]
    for icon, text in feats:
        row = QHBoxLayout()
        row.setSpacing(10)
        ico = QLabel(icon)
        ico.setStyleSheet("font-size: 14px;")
        row.addWidget(ico)
        tx = QLabel(text)
        tx.setStyleSheet("color: #c9d1d9; font-size: 12px;")
        row.addWidget(tx)
        row.addStretch(1)
        body.addLayout(row)

    body.addSpacing(4)

    # ---------- BOTONES ----------
    # WhatsApp (verde) - grande, principal
    b_wa = QPushButton("  💬  Comprar por WhatsApp  ")
    b_wa.setFixedHeight(44)
    b_wa.setCursor(Qt.CursorShape.PointingHandCursor)
    b_wa.setStyleSheet(
        "QPushButton { background: #25D366; color: white;"
        " border: none; border-radius: 10px;"
        " font-size: 13px; font-weight: 700; }"
        " QPushButton:hover { background: #20ba5a; }"
        " QPushButton:pressed { background: #18994a; }")
    body.addWidget(b_wa)

    # Discord (indigo) - secundario
    b_dc = QPushButton("  🎮  Comprar por Discord  ")
    b_dc.setFixedHeight(40)
    b_dc.setCursor(Qt.CursorShape.PointingHandCursor)
    b_dc.setStyleSheet(
        "QPushButton { background: #5865F2; color: white;"
        " border: none; border-radius: 10px;"
        " font-size: 13px; font-weight: 600; }"
        " QPushButton:hover { background: #4752c4; }"
        " QPushButton:pressed { background: #3c45a5; }")
    body.addWidget(b_dc)

    # Ya tengo licencia
    b_lk = QPushButton("Ya tengo una clave de licencia")
    b_lk.setFixedHeight(30)
    b_lk.setCursor(Qt.CursorShape.PointingHandCursor)
    b_lk.setStyleSheet(
        "QPushButton { background: transparent;"
        " color: #8b949e; border: none;"
        " font-size: 11px; text-decoration: underline; }"
        " QPushButton:hover { color: #c9d1d9; }")
    body.addWidget(b_lk)

    v.addLayout(body)

    # ---------- CONECTORES ----------
    def open_wa():
        QDesktopServices.openUrl(QUrl(YAPE_URL_MENSUAL))
    def open_dc():
        try:
            QDesktopServices.openUrl(QUrl(DISCORD_URL))
        except Exception:
            pass
    def open_license():
        from add_license import show_license_dialog
        show_license_dialog(self)
        d.accept()
    b_wa.clicked.connect(open_wa)
    b_dc.clicked.connect(open_dc)
    b_lk.clicked.connect(open_license)

    # ---------- COUNTDOWN ----------
    offer_state = trial_tokens.get_offer()
    offer_id = "no_tokens_v1"
    if offer_state and offer_state.get("id") == offer_id:
        end_ts = int(offer_state["ts"]) + 86400
    else:
        end_ts = int(time.time()) + 86400
        trial_tokens.set_offer_claimed(offer_id)

    def tick():
        left = max(0, end_ts - int(time.time()))
        h, rem = divmod(left, 3600)
        m, s = divmod(rem, 60)
        if left > 0:
            cd.setText(f"{h:02d}:{m:02d}:{s:02d}")
        else:
            cd.setText("--:--:--")
            cd.setStyleSheet(
                "QLabel { background: #0a0d12; color: #8b949e;"
                " font-size: 26px; font-weight: 800;"
                " padding: 10px 18px; border-radius: 8px;"
                " letter-spacing: 3px; }")
    tick()
    timer = QTimer(d)
    timer.timeout.connect(tick)
    timer.start(1000)

    d.exec()


'''

t = t[:start] + new_fn + t[cut:]

mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
print("SINTAXIS OK")
print("parches: _show_no_tokens rediseñado (premium)")
