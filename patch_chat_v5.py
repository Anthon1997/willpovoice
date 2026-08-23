from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")
log = []

# ================= 1) Nueva pagina Chat IA (mockup) =================
s = t.find("    # ---------- PAGINA 5: CHAT IA ----------")
e = t.find("    self.pages.addWidget(page5)")
if s == -1 or e == -1:
    raise SystemExit("ERROR: bloque pagina 5 no encontrado")
e += len("    self.pages.addWidget(page5)")

new_page = '''    # ---------- PAGINA 5: CHAT IA ----------
    page5 = QWidget()
    page5.setStyleSheet("background: transparent;")
    p5 = QVBoxLayout(page5)
    p5.setContentsMargins(24, 20, 24, 20)
    p5.setSpacing(14)

    self._chat_bg = QLabel(page5)
    self._chat_bg.setStyleSheet("background: transparent;")
    self._chat_bg.lower()

    h5 = QHBoxLayout()
    h5.setSpacing(12)
    ico5 = QLabel()
    ico5.setPixmap(make_icon("sparkles", "#bc8cff", 30))
    h5.addWidget(ico5)
    tcol = QVBoxLayout()
    tcol.setSpacing(2)
    t5 = QLabel("Chat IA")
    t5.setStyleSheet(f"color: {TEXT}; font-size: 20px; font-weight: 800;")
    tcol.addWidget(t5)
    s5 = QLabel("Asistente inteligente de WillpoVoice")
    s5.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
    tcol.addWidget(s5)
    h5.addLayout(tcol)
    h5.addStretch(1)
    btn_config = QPushButton("  Configurar API Key")
    btn_config.setIcon(QIcon(make_icon("key", "#7cb7ff", 14)))
    btn_config.setCursor(Qt.CursorShape.PointingHandCursor)
    btn_config.setStyleSheet(
        "QPushButton { background: transparent; color: #cfe3ff;"
        " border: 1px solid #2f4c79; border-radius: 16px;"
        " padding: 7px 14px; font-size: 11.5px; font-weight: 600; }"
        " QPushButton:hover { background: rgba(88,166,255,25); }")
    btn_config.clicked.connect(self._configure_groq_key)
    h5.addWidget(btn_config)
    p5.addLayout(h5)

    self._chat_banner = QFrame()
    self._chat_banner.setStyleSheet(
        "QFrame { background: #1c1f2e; border: 1px solid #4a3f7a; border-radius: 10px; }")
    bv = QVBoxLayout(self._chat_banner)
    bv.setContentsMargins(16, 12, 16, 12)
    bv.setSpacing(8)
    bt1 = QLabel("Configura tu API Key de Groq para usar el Chat IA")
    bt1.setStyleSheet(f"color: {TEXT}; font-size: 13px; font-weight: 600;")
    bv.addWidget(bt1)
    bt2 = QLabel("Obtén tu clave gratis en console.groq.com (sin tarjeta de crédito)")
    bt2.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
    bv.addWidget(bt2)
    btn_get_key = QPushButton("Obtener API Key gratis")
    btn_get_key.setCursor(Qt.CursorShape.PointingHandCursor)
    btn_get_key.setStyleSheet(
        f"QPushButton {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
        f" stop:0 {BLUE}, stop:1 {PURPLE}); color: white; border: none;"
        " border-radius: 8px; padding: 8px 16px; font-weight: 600; }}")
    btn_get_key.clicked.connect(
        lambda: QDesktopServices.openUrl(QUrl("https://console.groq.com/keys")))
    bv.addWidget(btn_get_key, 0, Qt.AlignmentFlag.AlignLeft)
    p5.addWidget(self._chat_banner)

    self._chat_scroll = QScrollArea()
    self._chat_scroll.setWidgetResizable(True)
    self._chat_scroll.setStyleSheet(
        "QScrollArea { border: none; background: transparent; }")
    chat_widget = QWidget()
    chat_widget.setStyleSheet("background: transparent;")
    self._chat_layout = QVBoxLayout(chat_widget)
    self._chat_layout.setContentsMargins(0, 0, 0, 0)
    self._chat_layout.setSpacing(14)
    self._chat_layout.addStretch(1)
    self._chat_scroll.setWidget(chat_widget)
    self._chat_scroll.viewport().setStyleSheet("background: transparent;")
    p5.addWidget(self._chat_scroll, 1)

    bar = QFrame()
    bar.setObjectName("chatBar")
    bar.setStyleSheet(
        "#chatBar { background: #0d1220; border: 1px solid #263050;"
        " border-radius: 24px; }")
    bh = QHBoxLayout(bar)
    bh.setContentsMargins(8, 6, 8, 6)
    bh.setSpacing(8)
    orb = QLabel()
    orb.setFixedSize(40, 40)
    orb.setPixmap(make_icon("sparkles", "#bc8cff", 20))
    orb.setAlignment(Qt.AlignmentFlag.AlignCenter)
    orb.setStyleSheet(
        "border: 1.5px solid #6b3fa8; border-radius: 20px; background: transparent;")
    bh.addWidget(orb)
    self._chat_input = QLineEdit()
    self._chat_input.setFixedHeight(40)
    self._chat_input.setPlaceholderText("Escribe tu pregunta...")
    self._chat_input.setStyleSheet(
        "QLineEdit { background: transparent; border: none; color: #e6edf3;"
        " font-size: 13px; padding: 0 6px; }")
    self._chat_input.returnPressed.connect(self._send_chat_message)
    bh.addWidget(self._chat_input, 1)
    btn_send = QPushButton()
    btn_send.setFixedSize(40, 40)
    btn_send.setCursor(Qt.CursorShape.PointingHandCursor)
    btn_send.setIcon(QIcon(_chat_svg(
        "M2.01 21 23 12 2.01 3 2 10l15 2-15 2z", "#ffffff", 18)))
    btn_send.setStyleSheet(
        "QPushButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
        " stop:0 #8d75ff, stop:1 #6d5df0); border: none; border-radius: 12px; }"
        " QPushButton:hover { background: #9d87ff; }")
    btn_send.clicked.connect(self._send_chat_message)
    bh.addWidget(btn_send)
    p5.addWidget(bar)

    self.pages.addWidget(page5)'''

t = t[:s] + new_page + t[e:]
log.append("pagina mockup")

# ================= 2) Burbujas + helpers =================
s2 = t.find("def _add_chat_bubble(self, text, is_user, temp=False):")
e2 = t.find("def _on_chat_response(self, response, temp_bubble):")
if s2 == -1 or e2 == -1:
    raise SystemExit("ERROR: _add_chat_bubble no encontrado")

new_bubbles = '''def _chat_svg(path_data, color, size):
    from PySide6.QtSvg import QSvgRenderer
    from PySide6.QtCore import QByteArray
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
           f'<path fill="{color}" d="{path_data}"/></svg>')
    r = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    r.render(p)
    p.end()
    return pm


class _Bubble(QWidget):
    def __init__(self, text, is_user, ts, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        v = QVBoxLayout(self)
        v.setContentsMargins(16, 12, 16, 8)
        v.setSpacing(6)
        lbl = QLabel(text)
        lbl.setWordWrap(True)
        lbl.setStyleSheet(
            "color: #ffffff; font-size: 12.5px; background: transparent;")
        v.addWidget(lbl)
        trow = QHBoxLayout()
        trow.setSpacing(4)
        trow.addStretch(1)
        tlabel = QLabel(ts + ("  \\u2713\\u2713" if is_user else ""))
        tlabel.setStyleSheet(
            "color: " + ("rgba(255,255,255,0.75)" if is_user else "#8b949e") +
            "; font-size: 9.5px; background: transparent;")
        trow.addWidget(tlabel)
        v.addLayout(trow)

    def paintEvent(self, ev):
        from PySide6.QtGui import (QPainter, QPainterPath,
                                   QLinearGradient, QColor)
        from PySide6.QtCore import QRectF
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect().adjusted(0, 0, 0, -7))
        path = QPainterPath()
        path.addRoundedRect(r, 14, 14)
        if self.is_user:
            x = r.right() - 22
            path.moveTo(x, r.bottom() - 4)
            path.lineTo(x + 16, r.bottom() - 6)
            path.lineTo(x + 10, self.height() - 1)
            path.closeSubpath()
            g = QLinearGradient(0, 0, self.width(), self.height())
            g.setColorAt(0, "#8d75ff")
            g.setColorAt(1, "#6d5df0")
            p.fillPath(path, g)
        else:
            x = r.left() + 8
            path.moveTo(x, r.bottom() - 4)
            path.lineTo(x + 14, r.bottom() - 6)
            path.lineTo(x - 4, self.height() - 1)
            path.closeSubpath()
            p.fillPath(path, QColor("#10162a"))
            p.setPen(QColor("#263050"))
            p.drawPath(path)
        p.end()


def _add_chat_bubble(self, text, is_user, temp=False):
    from PySide6.QtCore import QTime
    ts = QTime.currentTime().toString("h:mm AP")
    row = QHBoxLayout()
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(10)
    if not is_user:
        av = QLabel()
        av.setFixedSize(40, 40)
        av.setPixmap(self.windowIcon().pixmap(24, 24))
        av.setAlignment(Qt.AlignmentFlag.AlignCenter)
        av.setStyleSheet(
            "background: #0d1220; border: 2px solid #7c5cff;"
            " border-radius: 20px;")
        row.addWidget(av, 0, Qt.AlignmentFlag.AlignTop)
    bub = _Bubble(text, is_user, ts)
    bub.setMaximumWidth(560)
    if is_user:
        row.addStretch(1)
        row.addWidget(bub)
    else:
        row.addWidget(bub)
        row.addStretch(1)
    wrap = QWidget()
    wrap.setLayout(row)
    wrap.setProperty("temp", temp)
    self._chat_layout.insertWidget(self._chat_layout.count() - 1, wrap)
    self._chat_scroll.verticalScrollBar().setValue(
        self._chat_scroll.verticalScrollBar().maximum())
    return wrap


'''
t = t[:s2] + new_bubbles + t[e2:]
log.append("burbujas mockup")

# ================= 3) Fondo decorativo + layout =================
anchor_sw = "    self.pages.setCurrentIndex(index)"
if "if index == 5:" not in t and anchor_sw in t:
    i = t.find(anchor_sw) + len(anchor_sw)
    t = t[:i] + "\n    if index == 5:\n        self._layout_chat_bg()" + t[i:]
    log.append("bg en switch")

anchor_att = "MainWindow._configure_groq_key = _configure_groq_key"
if "def _layout_chat_bg" not in t and anchor_att in t:
    i = t.find(anchor_att)
    bg_fn = '''def _layout_chat_bg(self):
    try:
        import sys as _sys
        from PySide6.QtSvg import QSvgRenderer
        base = Path(getattr(_sys, "_MEIPASS",
                            Path(__file__).resolve().parents[1]))
        if not getattr(self, "_chat_bg_pix", None):
            pm = QPixmap(1400, 900)
            pm.fill(Qt.GlobalColor.transparent)
            pr = QPainter(pm)
            pr.setOpacity(0.28)
            sp = base / "assets" / "banner.svg"
            if sp.exists():
                QSvgRenderer(str(sp)).render(pr)
            pr.end()
            self._chat_bg_pix = pm
        w = self.pages.width() or 1200
        h = self.pages.height() or 800
        self._chat_bg.setGeometry(0, 0, w, h)
        self._chat_bg.setPixmap(
            self._chat_bg_pix.scaled(
                w, h, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation))
    except Exception:
        pass


'''
    t = t[:i] + bg_fn + t[i:]
    t = t.replace(anchor_att, "MainWindow._layout_chat_bg = _layout_chat_bg\n" + anchor_att, 1)
    log.append("_layout_chat_bg")

mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
for n in ("_send_chat_message", "_add_chat_bubble", "_layout_chat_bg"):
    assert f"MainWindow.{n} = {n}" in t or f"def {n}" in t, n
print("OK", log)
