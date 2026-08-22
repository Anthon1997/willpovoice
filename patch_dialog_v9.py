from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")

start = t.find("def _show_no_tokens(self):")
if start == -1:
    raise SystemExit("ERROR: no existe _show_no_tokens")
cands = []
for marker in ("MainWindow._show_no_tokens", "\nclass PaymentDialog", "\ndef _open_plans"):
    i = t.find(marker, start + 10)
    if i != -1:
        cands.append(i)
cut = min(cands)

new_fn = r'''def _show_no_tokens(self):
    from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                   QPushButton, QFrame)
    from PySide6.QtGui import (QDesktopServices, QPixmap, QPainter, QIcon,
                               QColor)
    from PySide6.QtCore import QUrl, QTimer, Qt, QByteArray, QSize
    from PySide6.QtSvg import QSvgRenderer
    import time
    import sys as _sys

    def _svg(path_data, color, size):
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
               f'<path fill="{color}" d="{path_data}"/></svg>')
        r = QSvgRenderer(QByteArray(svg.encode("utf-8")))
        pm = QPixmap(size, size)
        pm.fill(Qt.GlobalColor.transparent)
        p = QPainter(pm)
        r.render(p)
        p.end()
        return pm

    IC_WARN = "M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"
    IC_ZAP = "M13 2 3 14h9l-1 8 10-12h-9l1-8z"
    IC_SHIELD = ("M12 1 3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 "
                 "9-12V5l-9-4zm-2 16-4-4 1.41-1.41L10 14.17l6.59-6.59L18 "
                 "9l-8 8z")
    IC_GIFT = ("M20 6h-2.18c.11-.31.18-.65.18-1 0-1.66-1.34-3-3-3-1.05 0-"
               "1.96.54-2.5 1.35l-.5.67-.5-.68C10.96 2.54 10.05 2 9 2 7.34 "
               "2 6 3.34 6 5c0 .35.07.69.18 1H4c-1.11 0-1.99.89-1.99 2L2 "
               "19c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V8c0-1.11-.89-2-2-2zm-"
               "5-2c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zM9 4c.55 "
               "0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm11 15H4v-2h16v2z"
               "m0-5H4V8h5.08L7 10.83 8.62 12 11 8.76l1-1.36 1 1.36L15.38 "
               "12 17 10.83 14.92 8H20v6z")
    IC_MIC = ("M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 "
              "1.66 1.34 3 3 3zm5.3-3c0 3-2.54 5.1-5.3 5.1S6.7 14 6.7 11H5c0 "
              "3.41 2.72 6.23 6 6.72V21h2v-3.28c3.28-.48 6-3.3 6-6.72h-1.7z")
    IC_DOC = ("M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 2 2h12c1.1 0 "
              "2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 "
              "9H13z")
    IC_HEAD = ("M12 1c-4.97 0-9 4.03-9 9v7c0 1.66 1.34 3 3 3h3v-8H5v-2c0-"
               "3.87 3.13-7 7-7s7 3.13 7 7v2h-4v8h3c1.66 0 3-1.34 3-3v-7c0-"
               "4.97-4.03-9-9-9z")
    IC_WA = ("M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471"
             "-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644"
             ".075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653"
             "-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149"
             "-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669"
             "-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01"
             "-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 "
             "2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 "
             "4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118."
             "571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-"
             ".074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-"
             "5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 "
             "0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 "
             "1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 "
             "9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 "
             "0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305"
             "-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 "
             "11.893-11.893a11.821 11.821 0 00-3.485-8.413Z")
    IC_DC = ("M20.317 4.37a19.79 19.79 0 0 0-4.885-1.515.074.074 0 0 0-.079"
             ".037c-.21.375-.444.865-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64"
             " 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0"
             " 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099"
             " 18.058a.082.082 0 0 0 .031.056 19.9 19.9 0 0 0 5.993 3.03.078"
             ".078 0 0 0 .084-.028 14.09 14.09 0 0 0 1.226-1.994.076.076 0 0"
             " 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008"
             "-.128 10.2 10.2 0 0 0 .372-.291.074.074 0 0 1 .077-.01c3.928"
             " 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246"
             ".198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873"
             ".892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076"
             ".076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0"
             " 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031"
             "-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956"
             "-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956"
             " 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0"
             "-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0"
             " 1.333-.946 2.418-2.157 2.418Z")

    W, H = 560, 800
    d = QDialog(self)
    d.setModal(True)
    d.setFixedSize(W, H)
    d.setWindowTitle("Compra Tokens")
    d.setStyleSheet(
        "QDialog { background: #0a0d12; }"
        " QLabel { background: transparent; border: none; }")

    # ---------- FONDO: tu imagen + overlay ----------
    bg = QLabel(d)
    bg.setGeometry(0, 0, W, H)
    bg.lower()
    pm = QPixmap(W, H)
    pm.fill(QColor("#0a0d12"))
    p = QPainter(pm)
    base = Path(getattr(_sys, "_MEIPASS",
                        Path(__file__).resolve().parents[1]))
    src = None
    for cand in ("assets/icons/tokens_bg.png", "assets/img/tokens_bg.png",
                 "assets/tokens_bg.png"):
        cp = base / cand
        if cp.exists():
            src = cp
            break
    if src is not None:
        scaled = QPixmap(str(src)).scaled(
            W, H, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation)
        p.drawPixmap((W - scaled.width()) // 2,
                     (H - scaled.height()) // 2, scaled)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor(10, 13, 18, 175))
    p.drawRect(0, 0, W, H)
    p.end()
    bg.setPixmap(pm)

    v = QVBoxLayout(d)
    v.setContentsMargins(30, 26, 30, 24)
    v.setSpacing(12)

    # ---------- HEADER marketing ----------
    top = QHBoxLayout()
    top.setSpacing(8)
    warn = QLabel()
    warn.setPixmap(_svg(IC_WARN, "#f5b544", 15))
    top.addWidget(warn)
    warn_t = QLabel("ACCESO LIMITADO")
    warn_t.setStyleSheet(
        "color: #bc8cff; font-size: 11px; font-weight: 700;"
        " letter-spacing: 2px;")
    top.addWidget(warn_t)
    top.addStretch(1)
    v.addLayout(top)

    t1 = QLabel("Compra")
    t1.setStyleSheet("color: #ffffff; font-size: 32px; font-weight: 900;")
    v.addWidget(t1)
    t2 = QLabel("Tokens")
    t2.setStyleSheet("color: #6f8cff; font-size: 32px; font-weight: 900;")
    v.addWidget(t2)
    sub = QLabel("M\u00e1s tokens, m\u00e1s posibilidades.\n"
                 "Convierte texto en voz sin l\u00edmites.")
    sub.setStyleSheet("color: #8b949e; font-size: 12px;")
    v.addWidget(sub)
    v.addSpacing(2)

    # ---------- 3 MINI CARDS ----------
    cards = QHBoxLayout()
    cards.setSpacing(10)
    for path, color, ctitle, cdesc in [
        (IC_ZAP, "#bc8cff", "M\u00e1s conversiones", "Convierte m\u00e1s texto en voz"),
        (IC_SHIELD, "#58a6ff", "Seguro y r\u00e1pido", "Transacciones 100% seguras"),
        (IC_GIFT, "#f5b544", "Bonos exclusivos", "Tokens extra en cada compra"),
    ]:
        fr = QFrame()
        fr.setObjectName("ntCard")
        fr.setStyleSheet(
            "#ntCard { background: rgba(22,27,34,200);"
            " border: 1px solid rgba(124,92,255,70); border-radius: 10px; }")
        fv = QVBoxLayout(fr)
        fv.setContentsMargins(12, 10, 12, 10)
        fv.setSpacing(5)
        icl = QLabel()
        icl.setPixmap(_svg(path, color, 18))
        fv.addWidget(icl)
        ttl = QLabel(ctitle)
        ttl.setStyleSheet("color: #e6edf3; font-size: 11px; font-weight: 700;")
        fv.addWidget(ttl)
        dsc = QLabel(cdesc)
        dsc.setStyleSheet("color: #8b949e; font-size: 9.5px;")
        dsc.setWordWrap(True)
        fv.addWidget(dsc)
        cards.addWidget(fr)
    v.addLayout(cards)

    # ---------- OFERTA 24H ----------
    offer = QFrame()
    offer.setObjectName("ntOffer")
    offer.setStyleSheet(
        "#ntOffer { background: rgba(20,16,31,220);"
        " border: 1.5px solid #6b3fa8; border-radius: 14px; }")
    ov = QVBoxLayout(offer)
    ov.setContentsMargins(18, 14, 18, 14)
    ov.setSpacing(8)
    badge = QLabel("  OFERTA LIMITADA  \u00b7  24 HORAS")
    badge.setStyleSheet(
        "QLabel { background: #f5b544; color: #1a0f05; font-size: 10px;"
        " font-weight: 800; letter-spacing: 1.5px; padding: 4px 12px;"
        " border-radius: 4px; }")
    badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
    badge.setFixedHeight(22)
    ov.addWidget(badge, 0, Qt.AlignmentFlag.AlignCenter)
    oh = QLabel("Tu primer mes Pro al 50% de descuento")
    oh.setStyleSheet("color: #ffffff; font-size: 15px; font-weight: 700;")
    oh.setAlignment(Qt.AlignmentFlag.AlignCenter)
    ov.addWidget(oh)
    price_row = QHBoxLayout()
    price_row.setSpacing(10)
    price_row.addStretch(1)
    old_price = QLabel("S/ 10")
    old_price.setStyleSheet(
        "color: #8b949e; font-size: 20px; font-weight: 500;"
        " text-decoration: line-through;")
    price_row.addWidget(old_price)
    new_price = QLabel("S/ 5")
    new_price.setFixedHeight(44)
    new_price.setStyleSheet("color: #f5b544; font-size: 34px; font-weight: 900;")
    price_row.addWidget(new_price)
    price_row.addStretch(1)
    ov.addLayout(price_row)
    cd = QLabel("00:00:00")
    cd.setFixedHeight(58)
    cd.setAlignment(Qt.AlignmentFlag.AlignCenter)
    cd.setStyleSheet(
        "QLabel { background: #0a0d12; color: #ffffff; font-size: 26px;"
        " font-weight: 800; font-family: 'Consolas', monospace;"
        " border-radius: 8px; letter-spacing: 3px; }")
    ov.addWidget(cd)
    cd_label = QLabel("TIEMPO RESTANTE PARA APROVECHAR LA OFERTA")
    cd_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    cd_label.setStyleSheet("color: #8b949e; font-size: 9.5px; letter-spacing: 1.2px;")
    ov.addWidget(cd_label)
    v.addWidget(offer)

    # ---------- BOTONES ----------
    b_wa = QPushButton("  Comprar por WhatsApp  ")
    b_wa.setFixedHeight(44)
    b_wa.setCursor(Qt.CursorShape.PointingHandCursor)
    b_wa.setIcon(QIcon(_svg(IC_WA, "#ffffff", 20)))
    b_wa.setIconSize(QSize(20, 20))
    b_wa.setStyleSheet(
        "QPushButton { background: #25D366; color: white; border: none;"
        " border-radius: 10px; font-size: 13px; font-weight: 700; }"
        " QPushButton:hover { background: #20ba5a; }")
    v.addWidget(b_wa)
    b_dc = QPushButton("  Comprar por Discord  ")
    b_dc.setFixedHeight(40)
    b_dc.setCursor(Qt.CursorShape.PointingHandCursor)
    b_dc.setIcon(QIcon(_svg(IC_DC, "#ffffff", 20)))
    b_dc.setIconSize(QSize(20, 20))
    b_dc.setStyleSheet(
        "QPushButton { background: #5865F2; color: white; border: none;"
        " border-radius: 10px; font-size: 13px; font-weight: 600; }"
        " QPushButton:hover { background: #4752c4; }")
    v.addWidget(b_dc)
    b_lk = QPushButton("Ya tengo una clave de licencia")
    b_lk.setFixedHeight(28)
    b_lk.setCursor(Qt.CursorShape.PointingHandCursor)
    b_lk.setStyleSheet(
        "QPushButton { background: transparent; color: #8b949e; border: none;"
        " font-size: 11px; text-decoration: underline; }"
        " QPushButton:hover { color: #c9d1d9; }")
    v.addWidget(b_lk)

    b_wa.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(YAPE_URL_MENSUAL)))
    b_dc.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(DISCORD_URL)))
    b_lk.clicked.connect(lambda: (d.accept(), self._open_license_dialog()))

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
        cd.setText(f"{h:02d}:{m:02d}:{s:02d}" if left > 0 else "--:--:--")
    tick()
    timer = QTimer(d)
    timer.timeout.connect(tick)
    timer.start(1000)
    d.exec()


'''

t = t[:start] + new_fn + t[cut:]
mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
for n in ("_trial_gate", "_show_no_tokens", "_refresh_token_chip"):
    assert f"MainWindow.{n} = {n}" in t, f"FALTA {n}"
assert "class PaymentDialog" in t
print("SINTAXIS OK · diseño marketing con fondo")
