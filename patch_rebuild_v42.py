from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")

s = t.find("class _HexIcon(QWidget):")
mp = t.find("    def paintEvent(self, ev):", s)
e = t.find("def _add_chat_bubble")
if s == -1 or mp == -1 or e == -1:
    raise SystemExit("ERROR: region no delimitada")

block = '''    def paintEvent(self, ev):
        import math
        from PySide6.QtGui import QPolygonF, QPen
        from PySide6.QtCore import QPointF
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        s = self.width()
        c = s / 2
        r = s / 2 - 2
        pts = [QPointF(c + r * math.cos(math.radians(60 * k - 30)),
                       c + r * math.sin(math.radians(60 * k - 30)))
               for k in range(6)]
        fill = QColor(self._color)
        fill.setAlpha(38)
        p.setBrush(fill)
        p.setPen(QPen(QColor(self._color), 1.5))
        p.drawPolygon(QPolygonF(pts))
        p.setPen(Qt.PenStyle.NoPen)
        ip = self._pix
        p.drawPixmap(int(c - ip.width() / 2), int(c - ip.height() / 2), ip)
        p.end()


def _medal_pixmap(w=34, h=50):
    """Medalla colgante: cinta vertical con muesca V y circulo con diamante."""
    from PySide6.QtSvg import QSvgRenderer
    from PySide6.QtCore import QByteArray
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 72">'
           '<defs>'
           '<linearGradient id="rb" x1="0" y1="0" x2="0" y2="1">'
           '<stop offset="0" stop-color="#8b5cf6"/>'
           '<stop offset="1" stop-color="#6d28d9"/>'
           '</linearGradient>'
           '<linearGradient id="cg" x1="0" y1="0" x2="1" y2="1">'
           '<stop offset="0" stop-color="#a78bfa"/>'
           '<stop offset="1" stop-color="#7c3aed"/>'
           '</linearGradient>'
           '</defs>'
           '<path d="M14 0 h20 v60 l-10 -9 -10 9 z" fill="url(#rb)"/>'
           '<path d="M14 0 h20 v5 h-20 z" fill="#5b21b6" opacity="0.55"/>'
           '<circle cx="24" cy="24" r="15" fill="url(#cg)"/>'
           '<circle cx="24" cy="24" r="15" fill="none" '
           'stroke="#e9d5ff" stroke-width="2"/>'
           '<path d="M18 21 h12 l4 5 -10 11 -10 -11 z" fill="#ffffff"/>'
           '<path d="M18 21 l6 5 6 -5 M24 26 v11 M14 26 h20" '
           'stroke="#ddd6fe" stroke-width="1" fill="none" opacity="0.8"/>'
           '</svg>')
    r = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    pm = QPixmap(w, h)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    r.render(p)
    p.end()
    return pm


class PlansDialog(QDialog):
    _GIFT = ("M20 6h-2.18c.11-.31.18-.65.18-1a3 3 0 0 0-5.5-1.65l-.5.67-.5-.68"
             "A3 3 0 0 0 6 5c0 .35.07.69.18 1H4a2 2 0 0 0-2 2v11a2 2 0 0 0 2 2h16"
             "a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2zm-5-2a1 1 0 1 1 0 2 1 1 0 0 1 0-2zM9 4"
             "a1 1 0 1 1 0 2 1 1 0 0 1 0-2zm11 15H4v-2h16v2zm0-5H4V8h5.08L7 10.83"
             " 8.62 12 11 8.76l1-1.36 1 1.36L15.38 12 17 10.83 14.92 8H20v6z")
    _CART = ("M7 18c-1.1 0-1.99.9-1.99 2S5.9 22 7 22s2-.9 2-2-.9-2-2-2zM1 2v2h2l3.6 7.59"
             "-1.35 2.45c-.16.28-.25.61-.25.96 0 1.1.9 2 2 2h12v-2H7.42c-.14 0-.25-.11"
             "-.25-.25l.03-.12.9-1.63h7.45c.75 0 1.41-.41 1.75-1.03l3.58-6.49A1 1 0 0 0 "
             "20 4H5.21l-.94-2H1zm16 16c-1.1 0-1.99.9-1.99 2s.89 2 1.99 2 2-.9 2-2"
             "-.9-2-2-2z")
    _CAL = ("M19 4h-1V2h-2v2H8V2H6v2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 "
            "2-2V6a2 2 0 0 0-2-2zm0 16H5V10h14v10zM5 8V6h14v2H5z")
    _REFRESH = ("M17.65 6.35A7.95 7.95 0 0 0 12 4a8 8 0 1 0 7.73 10h-2.08A6 6 0 1 1 "
                "12 6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z")
    _GEM = ("M6 3h12l4 6-10 12L2 9l4-6zm2 2L5.5 8.5 12 17l6.5-8.5L16 5H8z")
    _CHECK = "M9 16.17 4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"
    _BOLT = "M7 2v11h3v9l7-12h-4l4-8z"
    _SHIELD = ("M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm-2 "
               "16l-4-4 1.41-1.41L10 14.17l6.59-6.59L18 9l-8 8z")

    def __init__(self, parent):
        super().__init__(parent)
        self.setModal(True)
        self.setFixedWidth(540)
        try:
            from PySide6.QtGui import QGuiApplication
            _scr = QGuiApplication.primaryScreen()
            if _scr is not None:
                self.setMaximumHeight(
                    int(_scr.availableSize().height() * 0.92))
        except Exception:
            pass
        self.setWindowTitle("WillpoVoice Premium")
        self.setStyleSheet("PlansDialog { background: #0a0c14; }")
        self._bg = QLabel(self)
        self._bg.setStyleSheet("background: transparent;")
        self._bg.lower()

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }")
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        v = QVBoxLayout(content)
        v.setContentsMargins(22, 14, 22, 14)
        v.setSpacing(8)

        hd = QLabel()
        hd.setPixmap(make_icon("crown", "#f5b544", 32))
        hd.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(hd)
        t1 = QLabel('Elige tu <span style="color:#a78bfa;">plan</span>')
        t1.setStyleSheet(
            "color: #ffffff; font-size: 20px; font-weight: 800;")
        t1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(t1)
        t2 = QLabel('Voces <span style="color:#f472b6;">premium</span> reales, '
                    'sin l\\u00edmites artificiales.')
        t2.setStyleSheet("color: #9aa4c0; font-size: 11px;")
        t2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(t2)
        v.addSpacing(4)

        self._card(v, "#00d0ff", "flask", None, "Gratis", "S/ 0",
                   ["7 d\\u00edas de prueba", "5,000 tokens incluidos",
                    "Hasta 5,000 caracteres por conversi\\u00f3n",
                    "Todas las voces premium"],
                   btn_text="Iniciar prueba gratuita",
                   btn_icon=self._GIFT, solid=False,
                   on_buy=self._start_trial)
        self._card(v, "#a855f7", None, self._CAL, "Mensual", "S/ 10",
                   ["20,000 tokens al mes", "Hasta 20,000 caracteres",
                    "Todas las voces premium", "Soporte por Discord"],
                   btn_text="Comprar", btn_icon=self._CART, solid=False,
                   on_buy=lambda: self._buy(
                       "Mensual", 10, YAPE_URL_MENSUAL))
        self._card(v, "#ffb020", "star", None, "Lifetime", "S/ 30",
                   ["Uso ILIMITADO, sin tokens", "Caracteres ILIMITADOS",
                    "Voces nuevas para siempre",
                    "Soporte prioritario de por vida"],
                   btn_text="Comprar", btn_icon=None, solid=True,
                   badge="Recomendado", ribbon=True,
                   on_buy=lambda: self._buy(
                       "Lifetime", 30, YAPE_URL_LIFETIME))

        v.addSpacing(2)
        foot = QFrame()
        foot.setObjectName("plansFooter")
        foot.setStyleSheet(
            "#plansFooter { background: #10141f; border: 1px solid #1c2333;"
            " border-radius: 12px; }")
        fv = QHBoxLayout(foot)
        fv.setContentsMargins(14, 8, 14, 8)
        fv.setSpacing(10)
        for path, color, title, sub in [
            (self._SHIELD, "#4cc2ff", "Pago seguro",
             "Tus datos est\\u00e1n protegidos"),
            (self._BOLT, "#bc8cff", "Acceso inmediato",
             "Disfruta al instante"),
            (self._REFRESH, "#4cc2ff", "Sin renovaciones",
             "Pago \\u00fanico, para siempre"),
        ]:
            it = QHBoxLayout()
            it.setSpacing(10)
            ic = QLabel()
            ic.setPixmap(_chat_svg(path, color, 16))
            it.addWidget(ic)
            tx = QVBoxLayout()
            tx.setSpacing(2)
            a = QLabel(title)
            a.setStyleSheet(
                "color: #e6edf3; font-size: 10.5px; font-weight: 700;")
            tx.addWidget(a)
            b = QLabel(sub)
            b.setStyleSheet("color: #7d8590; font-size: 9px;")
            tx.addWidget(b)
            it.addLayout(tx)
            fv.addLayout(it)
            fv.addStretch(1)
        v.addWidget(foot)
        scroll.setWidget(content)
        outer.addWidget(scroll)
        content.adjustSize()
        try:
            from PySide6.QtGui import QGuiApplication
            _scr = QGuiApplication.primaryScreen()
            maxh = int(_scr.availableSize().height() * 0.92) if _scr else 900
        except Exception:
            maxh = 900
        want = content.sizeHint().height() + 46
        self.resize(540, min(want, maxh))
        scroll.setMinimumHeight(320)

    def _card(self, v, color, icon_kind, icon_path, name, price, feats,
              btn_text=None, btn_icon=None, solid=False, badge=None,
              ribbon=False, on_buy=None):
        def _A(c, a):
            return "#" + a + c[1:]
        card = QFrame()
        card.setObjectName("plancard_" + name)
        bord = color if badge else _A(color, "99")
        bgs = {"#00d0ff": "0b1322", "#a855f7": "130e26",
               "#ffb020": "181007"}
        rgb = bgs.get(color, "10141f")
        card.setStyleSheet(
            "#plancard_" + name + " { background: qlineargradient("
            "x1:0,y1:0,x2:0,y2:1, stop:0 #33" + rgb + ", stop:1 #14"
            + rgb + "); border: 1.5px solid " + bord +
            "; border-radius: 16px; }")
        cv = QVBoxLayout(card)
        cv.setContentsMargins(14, 12, 14, 12)
        cv.setSpacing(6)
        top = QHBoxLayout()
        top.setSpacing(14)
        if icon_kind:
            pix = make_icon(icon_kind, color, 22)
        else:
            pix = _chat_svg(icon_path, color, 22)
        top.addWidget(_HexIcon(pix, color, 44))
        nrow = QHBoxLayout()
        nrow.setSpacing(10)
        nm = QLabel(name)
        nm.setStyleSheet(
            "color: #ffffff; font-size: 14px; font-weight: 800;")
        nrow.addWidget(nm)
        if badge:
            bd = QLabel("\\u2605 " + badge)
            bd.setStyleSheet(
                "color: #f5b544; border: 1px solid #66f5b544;"
                " border-radius: 9px; padding: 2px 8px;"
                " font-size: 9px; font-weight: 700;"
                " background: rgba(245,181,68,20);")
            nrow.addWidget(bd)
        nrow.addStretch(1)
        pr = QLabel(price)
        pr.setStyleSheet(
            "color: " + color + "; border: 1px solid " + _A(color, "66") + ";"
            " border-radius: 12px; padding: 4px 12px;"
            " font-size: 12px; font-weight: 800;"
            " background: rgba(0,0,0,60);")
        nrow.addWidget(pr)
        top.addLayout(nrow)
        cv.addLayout(top)
        cv.addSpacing(2)
        for f in feats:
            fr = QHBoxLayout()
            fr.setSpacing(10)
            fr.setContentsMargins(6, 0, 0, 0)
            ck = QLabel()
            ck.setPixmap(_chat_svg(self._CHECK, color, 12))
            fr.addWidget(ck)
            fl = QLabel(f)
            fl.setStyleSheet("color: #c9d1d9; font-size: 10.5px;")
            fr.addWidget(fl)
            fr.addStretch(1)
            cv.addLayout(fr)
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(
            "border-top: 1px dashed " + _A(color, "44") + ";"
            " background: transparent;")
        cv.addWidget(sep)
        if btn_text:
            b = QPushButton(btn_text)
            b.setFixedHeight(36 if solid else 32)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            if solid:
                b.setStyleSheet(
                    "QPushButton { background: qlineargradient(x1:0,y1:0,"
                    "x2:1,y2:0, stop:0 #8d5cf0, stop:1 #6d2fd0);"
                    " color: white; border: none; border-radius: 12px;"
                    " font-weight: 800; font-size: 13px; }"
                    " QPushButton:hover { background: #9d70ff; }")
                b.setIcon(QIcon(make_icon("crown", "#fbbf24", 16)))
            else:
                b.setStyleSheet(
                    "QPushButton { background: transparent; color: "
                    + color + "; border: 1px solid " + _A(color, "88") + ";"
                    " border-radius: 10px; font-weight: 700;"
                    " font-size: 12px; }"
                    " QPushButton:hover { background: " + _A(color, "22") + "; }")
                if btn_icon:
                    b.setIcon(QIcon(_chat_svg(btn_icon, color, 15)))
            if on_buy:
                b.clicked.connect(on_buy)
            cv.addWidget(b)
        v.addWidget(card)
        if ribbon:
            gem = QLabel(card)
            gem.setFixedSize(34, 50)
            gem.setPixmap(_medal_pixmap(34, 50))
            gem.setStyleSheet("background: transparent;")
            host = v.parent()
            if host is not None:
                gem.setParent(host)

            def _place(g=gem, c=card, h=host):
                try:
                    from PySide6.QtCore import QPoint
                    if h is not None:
                        g.move(c.mapTo(h, QPoint(c.width() - 30, 0)))
                    else:
                        g.move(c.width() - 30, 0)
                    g.raise_()
                    g.show()
                except Exception:
                    pass
            QTimer.singleShot(0, _place)

    def _build_bg(self):
        import sys
        base = Path(getattr(sys, "_MEIPASS",
                            Path(__file__).resolve().parents[1]))
        src = base / "assets" / "icons" / "licencia_left.png"
        if not src.exists():
            return
        w = self.width()
        h = self.height()
        if w <= 0 or h <= 0:
            return
        out = QPixmap(w, h)
        out.fill(QColor("#0a0c14"))
        p = QPainter(out)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setOpacity(0.30)
        scaled = QPixmap(str(src)).scaled(
            w, h, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation)
        p.drawPixmap((w - scaled.width()) // 2,
                     (h - scaled.height()) // 2, scaled)
        p.end()
        self._bg.setPixmap(out)
        self._bg.setGeometry(0, 0, w, h)
        self._bg.lower()

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        self._build_bg()

    def _start_trial(self):
        try:
            state, days = license_manager.check_status()
        except Exception:
            state, days = "trial", 7
        d = TrialActivatedDialog(
            self, max(0, days if state == "trial" else 7))
        d.exec()

    def _buy(self, plan, price, yape_url):
        d = PaymentDialog(self, plan, price, yape_url)
        d.exec()


def _open_plans(self):
    d = PlansDialog(self)
    d.exec()
    try:
        st, _d = license_manager.check_status()
        self._refresh_token_chip(st)
    except Exception:
        pass


MainWindow._open_plans = _open_plans


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
                                   QLinearGradient, QColor, QPen)
        from PySide6.QtCore import QRectF
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect().adjusted(1, 1, -1, -8))
        body = QPainterPath()
        body.addRoundedRect(r, 14, 14)
        tail = QPainterPath()
        if self.is_user:
            x = r.right() - 12
            tail.moveTo(x, r.bottom() - 4)
            tail.cubicTo(x + 2, r.bottom(), x + 4, r.bottom() + 2,
                         x + 7, self.height() - 1)
            tail.cubicTo(x - 2, r.bottom() + 1, x - 8, r.bottom() - 1,
                         x - 14, r.bottom() - 4)
            tail.closeSubpath()
        else:
            x = r.left() + 12
            tail.moveTo(x, r.bottom() - 4)
            tail.cubicTo(x - 2, r.bottom(), x - 4, r.bottom() + 2,
                         x - 7, self.height() - 1)
            tail.cubicTo(x + 2, r.bottom() + 1, x + 8, r.bottom() - 1,
                         x + 14, r.bottom() - 4)
            tail.closeSubpath()
        path = body.united(tail)
        if self.is_user:
            g = QLinearGradient(0, 0, self.width(), self.height())
            g.setColorAt(0, QColor("#8d75ff"))
            g.setColorAt(1, QColor("#6d5df0"))
            p.fillPath(path, g)
        else:
            g = QLinearGradient(0, 0, 0, self.height())
            g.setColorAt(0, QColor("#141b32"))
            g.setColorAt(1, QColor("#0e1526"))
            p.fillPath(path, g)
            p.setPen(QPen(QColor("#2a3552"), 1))
            p.drawPath(path)
        p.end()


'''

t = t[:mp] + block + t[e:]
mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
print("OK: region reconstruida (HexIcon+Medal+PlansDialog+open_plans+Bubble)")
