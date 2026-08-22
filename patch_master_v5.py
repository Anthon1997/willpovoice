from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")
log = []

# ---------- DISCORD_URL ----------
if "DISCORD_URL" not in t:
    idx = t.find("YAPE_URL_MENSUAL")
    if idx != -1:
        eol = t.find("\n", idx)
        t = t[:eol+1] + 'DISCORD_URL = "https://discord.com/invite/HpTZ9x8MG"\n' + t[eol+1:]
        log.append("discord url")

# ---------- Planes: 5,000 tokens ----------
if '"10,000 tokens incluidos"' in t:
    t = t.replace('"10,000 tokens incluidos"', '"5,000 tokens incluidos"', 1)
    log.append("planes 5000")

# ---------- _show_no_tokens premium (corte seguro) ----------
start = t.find("def _show_no_tokens(self):")
if start == -1:
    raise SystemExit("ERROR: no existe _show_no_tokens")
cands = []
for marker in ("MainWindow._show_no_tokens", "\nclass PaymentDialog", "\ndef _open_plans"):
    i = t.find(marker, start + 10)
    if i != -1:
        cands.append(i)
if not cands:
    raise SystemExit("ERROR: sin limite de corte")
cut = min(cands)

new_fn = '''def _show_no_tokens(self):
    from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                   QPushButton, QFrame)
    from PySide6.QtGui import QDesktopServices
    from PySide6.QtCore import QUrl, QTimer, Qt
    import time

    d = QDialog(self)
    d.setModal(True)
    d.setFixedSize(520, 640)
    d.setWindowTitle("Tokens agotados")
    d.setStyleSheet("QDialog { background: #0a0d12; } QLabel { background: transparent; }")

    v = QVBoxLayout(d)
    v.setContentsMargins(0, 0, 0, 0)
    v.setSpacing(0)

    header = QFrame()
    header.setFixedHeight(130)
    header.setStyleSheet(
        "QFrame { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
        " stop:0 #3a1f5c, stop:0.5 #5a2e8c, stop:1 #7c3fa0); }")
    hv = QVBoxLayout(header)
    hv.setContentsMargins(28, 18, 28, 16)
    hv.setSpacing(4)
    top = QHBoxLayout()
    top.setSpacing(8)
    warn = QLabel("\\u26a0\\ufe0f")
    warn.setStyleSheet("font-size: 14px;")
    top.addWidget(warn)
    warn_t = QLabel("ACCESO LIMITADO")
    warn_t.setStyleSheet(
        "color: rgba(255,255,255,0.85); font-size: 12px; font-weight: 600;"
        " letter-spacing: 1px;")
    top.addWidget(warn_t)
    top.addStretch(1)
    hv.addLayout(top)
    title = QLabel("Tokens de prueba agotados")
    title.setStyleSheet("color: white; font-size: 24px; font-weight: 800;")
    hv.addWidget(title)
    sub = QLabel("Has usado tus 5,000 tokens de bienvenida")
    sub.setStyleSheet("color: rgba(255,255,255,0.75); font-size: 12px;")
    hv.addWidget(sub)
    v.addWidget(header)

    body = QVBoxLayout()
    body.setContentsMargins(28, 22, 28, 22)
    body.setSpacing(14)

    offer = QFrame()
    offer.setStyleSheet(
        "QFrame { background: #14101f; border: 1.5px solid #6b3fa8;"
        " border-radius: 14px; }")
    ov = QVBoxLayout(offer)
    ov.setContentsMargins(18, 16, 18, 16)
    ov.setSpacing(10)
    badge = QLabel("\\U0001f525  OFERTA LIMITADA \\u00b7 24 HORAS")
    badge.setStyleSheet(
        "QLabel { background: #f5b544; color: #1a0f05; font-size: 10px;"
        " font-weight: 800; letter-spacing: 1.5px; padding: 4px 10px;"
        " border-radius: 4px; }")
    badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
    badge.setFixedHeight(22)
    ov.addWidget(badge, 0, Qt.AlignmentFlag.AlignCenter)
    oh = QLabel("Tu primer mes Pro al 50% de descuento")
    oh.setStyleSheet("color: #ffffff; font-size: 16px; font-weight: 700;")
    oh.setAlignment(Qt.AlignmentFlag.AlignCenter)
    oh.setWordWrap(True)
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
    new_price.setStyleSheet("color: #f5b544; font-size: 34px; font-weight: 900;")
    price_row.addWidget(new_price)
    price_row.addStretch(1)
    ov.addLayout(price_row)
    cd = QLabel("00:00:00")
    cd.setAlignment(Qt.AlignmentFlag.AlignCenter)
    cd.setStyleSheet(
        "QLabel { background: #0a0d12; color: #ffffff; font-size: 26px;"
        " font-weight: 800; font-family: 'Consolas', monospace;"
        " padding: 10px 18px; border-radius: 8px; letter-spacing: 3px; }")
    ov.addWidget(cd)
    cd_label = QLabel("TIEMPO RESTANTE PARA APROVECHAR LA OFERTA")
    cd_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    cd_label.setStyleSheet(
        "color: #8b949e; font-size: 10px; letter-spacing: 1.2px;")
    ov.addWidget(cd_label)
    body.addWidget(offer)

    inc = QLabel("AL ACTIVAR TU PLAN PRO OBTIENES:")
    inc.setStyleSheet(
        "color: #c9d1d9; font-size: 11px; font-weight: 600; letter-spacing: 1px;")
    body.addWidget(inc)
    for icon, text in [
        ("\\u26a1", "20,000 tokens mensuales renovables"),
        ("\\U0001f399\\ufe0f", "Todas las voces premium sin restricciones"),
        ("\\U0001f4dd", "Hasta 20,000 caracteres por conversi\\u00f3n"),
        ("\\U0001f4ac", "Soporte directo por Discord"),
    ]:
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

    b_wa = QPushButton("  \\U0001f4ac  Comprar por WhatsApp  ")
    b_wa.setFixedHeight(44)
    b_wa.setCursor(Qt.CursorShape.PointingHandCursor)
    b_wa.setStyleSheet(
        "QPushButton { background: #25D366; color: white; border: none;"
        " border-radius: 10px; font-size: 13px; font-weight: 700; }"
        " QPushButton:hover { background: #20ba5a; }")
    body.addWidget(b_wa)
    b_dc = QPushButton("  \\U0001f3ae  Comprar por Discord  ")
    b_dc.setFixedHeight(40)
    b_dc.setCursor(Qt.CursorShape.PointingHandCursor)
    b_dc.setStyleSheet(
        "QPushButton { background: #5865F2; color: white; border: none;"
        " border-radius: 10px; font-size: 13px; font-weight: 600; }"
        " QPushButton:hover { background: #4752c4; }")
    body.addWidget(b_dc)
    b_lk = QPushButton("Ya tengo una clave de licencia")
    b_lk.setFixedHeight(30)
    b_lk.setCursor(Qt.CursorShape.PointingHandCursor)
    b_lk.setStyleSheet(
        "QPushButton { background: transparent; color: #8b949e; border: none;"
        " font-size: 11px; text-decoration: underline; }"
        " QPushButton:hover { color: #c9d1d9; }")
    body.addWidget(b_lk)
    v.addLayout(body)

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
log.append("show_no_tokens premium")

# ---------- Toast dia 5 ----------
if "termina en 2 dias" not in t:
    idx = t.find("self._refresh_token_chip(state)")
    if idx != -1:
        eol = t.find("\n", idx)
        toast = '''
    try:
        from PySide6.QtWidgets import QMessageBox
        _st, _dl = license_manager.check_status()
        if _st == "trial" and _dl == 2:
            QTimer.singleShot(1200, lambda: QMessageBox.information(
                self, "Prueba gratuita",
                "Tu periodo de prueba termina en 2 dias.\\n"
                f"Te quedan {trial_tokens.balance():,} tokens de prueba.\\n\\n"
                "Compra un plan para no perder el acceso."))
    except Exception:
        pass
'''
        t = t[:eol+1] + toast + t[eol+1:]
        log.append("toast dia 5")

mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
for name in ("_trial_gate", "_show_no_tokens", "_refresh_token_chip", "_trial_spend"):
    assert f"MainWindow.{name} = {name}" in t, f"FALTA attach de {name}"
assert "class PaymentDialog" in t, "FALTA PaymentDialog"
print("SINTAXIS OK + ATTACHES OK + PaymentDialog OK")
print("parches:", log)
