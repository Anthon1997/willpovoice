from pathlib import Path

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")
log = []

# ---------- 1) Reemplazar cabecera de _show_no_tokens (conserva botones) ----------
start = t.find("def _show_no_tokens(self):")
if start == -1:
    print("ERROR: no existe _show_no_tokens")
else:
    cut = t.find("v.addWidget(t2)", start)
    if cut == -1:
        print("ERROR: no encontre addWidget(t2)")
    else:
        cut += len("v.addWidget(t2)")
        new_head = '''def _show_no_tokens(self):
    from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                   QPushButton, QFrame)
    from PySide6.QtGui import QDesktopServices
    from PySide6.QtCore import QUrl, QTimer
    import time
    d = QDialog(self)
    d.setModal(True)
    d.setFixedWidth(440)
    d.setWindowTitle("Tokens de prueba")
    d.setStyleSheet("QDialog { background: #0b0e14; }")
    v = QVBoxLayout(d)
    v.setContentsMargins(28, 24, 28, 22)
    v.setSpacing(10)
    ic = QLabel()
    ic.setPixmap(make_icon("coins", "#f5b544", 46))
    ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
    v.addWidget(ic)
    t1 = QLabel("¡Tokens de prueba agotados!")
    t1.setStyleSheet("color: #e6edf3; font-size: 18px; font-weight: 800;")
    t1.setAlignment(Qt.AlignmentFlag.AlignCenter)
    v.addWidget(t1)
    offer = QFrame()
    offer.setStyleSheet("QFrame { background: #1c1208; border: 1px solid #5a3a10; border-radius: 10px; }")
    ov = QVBoxLayout(offer)
    ov.setContentsMargins(14, 10, 14, 10)
    ov.setSpacing(6)
    row = QHBoxLayout()
    row.setSpacing(6)
    fire = QLabel("🔥")
    fire.setStyleSheet("font-size: 16px;")
    row.addWidget(fire)
    ot1 = QLabel("Oferta de bienvenida · 24 horas")
    ot1.setStyleSheet("color: #f5b544; font-weight: 800; font-size: 12px;")
    row.addWidget(ot1)
    row.addStretch(1)
    ov.addLayout(row)
    ot2 = QLabel("Tu primer mes Pro por S/5 (en vez de S/10)")
    ot2.setStyleSheet("color: #e6edf3; font-size: 13px; font-weight: 700;")
    ot2.setWordWrap(True)
    ov.addWidget(ot2)
    cd = QLabel()
    cd.setStyleSheet("color: #8b949e; font-size: 11px;")
    ov.addWidget(cd)
    v.addWidget(offer)
    v.addSpacing(4)
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
            cd.setText(f"Expira en: {h:02d}h {m:02d}m {s:02d}s")
        else:
            cd.setText("Oferta expirada · precio normal S/10")
    tick()
    timer = QTimer(d)
    timer.timeout.connect(tick)
    timer.start(1000)
    t2 = QLabel("Usaste tus 5,000 tokens de prueba. Continúa sin límites con un plan Pro.")
    t2.setStyleSheet("color: #8b949e; font-size: 11.5px;")
    t2.setAlignment(Qt.AlignmentFlag.AlignCenter)
    t2.setWordWrap(True)
    v.addWidget(t2)'''
        t = t[:start] + new_head + t[cut:]
        log.append("_show_no_tokens con oferta 24h")

# ---------- 2) Texto de la tarjeta Gratis en PlansDialog ----------
if '"10,000 tokens incluidos"' in t:
    t = t.replace('"10,000 tokens incluidos"', '"5,000 tokens incluidos"', 1)
    log.append("PlansDialog 5,000 tokens")

# ---------- 3) Toast recordatorio dia 5 (si faltaba) ----------
if "termina en 2 dias" not in t:
    anchor = "self._refresh_token_chip(state)"
    idx = t.find(anchor)
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
        t = t[:eol + 1] + toast + t[eol + 1:]
        log.append("toast dia 5")

mw.write_text(t, encoding="utf-8", newline="\n")
import ast
ast.parse(t)
print("SINTAXIS OK")
print("parches:", log)
