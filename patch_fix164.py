from pathlib import Path
import ast

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

# ---- 1. _lic_pix redibujado (iconos pulidos) ----
s = t.find("def _lic_pix")
e = t.find("\nclass LicenseDialog")
new_pix = '''def _lic_pix(kind, color, s=18):
    from PySide6.QtCore import QPointF, QRectF
    from PySide6.QtGui import QPolygonF, QBrush
    import math
    pix = QPixmap(s, s)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    c = QColor(color)
    p.setPen(QPen(c, 1.5))
    m = s / 18.0
    if kind == "monitor":
        p.drawRoundedRect(QRectF(2*m, 3*m, 14*m, 10*m), 2, 2)
        p.drawLine(QPointF(9*m, 13*m), QPointF(9*m, 15*m))
        p.drawLine(QPointF(5*m, 15.5*m), QPointF(13*m, 15.5*m))
    elif kind == "copy":
        p.drawRoundedRect(QRectF(6*m, 6*m, 10*m, 10*m), 2, 2)
        p.drawRoundedRect(QRectF(3*m, 3*m, 10*m, 10*m), 2, 2)
    elif kind == "crown":
        pts = [QPointF(3*m, 12.5*m), QPointF(3*m, 6.5*m), QPointF(6.5*m, 9.5*m),
               QPointF(9*m, 4.5*m), QPointF(11.5*m, 9.5*m), QPointF(15*m, 6.5*m),
               QPointF(15*m, 12.5*m), QPointF(3*m, 12.5*m)]
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
        p.setPen(QPen(c, 1.5))
        p.drawLine(QPointF(9*m, 8*m), QPointF(9*m, 13*m))
    elif kind == "shield":
        path = QPainterPath()
        path.moveTo(9*m, 2*m)
        path.lineTo(14.5*m, 4.2*m)
        path.lineTo(14.5*m, 8.5*m)
        path.quadTo(14.5*m, 13.5*m, 9*m, 16*m)
        path.quadTo(3.5*m, 13.5*m, 3.5*m, 8.5*m)
        path.lineTo(3.5*m, 4.2*m)
        path.closeSubpath()
        p.drawPath(path)
        p.drawLine(QPointF(6.3*m, 9*m), QPointF(8.3*m, 11*m))
        p.drawLine(QPointF(8.3*m, 11*m), QPointF(11.8*m, 6.8*m))
    elif kind == "wa":
        p.drawEllipse(QRectF(2.5*m, 2*m, 13*m, 13*m))
        p.setBrush(QBrush(c))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPolygon(QPolygonF([
            QPointF(4.5*m, 13.5*m), QPointF(3*m, 16.5*m), QPointF(8*m, 14.8*m)]))
        p.setPen(QPen(c, 1.5))
        p.drawArc(QRectF(6*m, 6*m, 6*m, 6*m), 200*16, 140*16)
    elif kind == "flask":
        p.drawLine(QPointF(6*m, 2*m), QPointF(12*m, 2*m))
        p.drawLine(QPointF(7*m, 2*m), QPointF(7*m, 7*m))
        p.drawLine(QPointF(11*m, 2*m), QPointF(11*m, 7*m))
        p.drawLine(QPointF(7*m, 7*m), QPointF(4*m, 13.5*m))
        p.drawLine(QPointF(11*m, 7*m), QPointF(14*m, 13.5*m))
        p.drawLine(QPointF(4*m, 13.5*m), QPointF(14*m, 13.5*m))
        p.drawLine(QPointF(5.6*m, 10.5*m), QPointF(12.4*m, 10.5*m))
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
                          QPointF(8*m, 16*m), QPointF(13*m, 8*m), QPointF(9*m, 8*m),
                          QPointF(10*m, 2*m)])
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
if s != -1 and e != -1 and e > s:
    t = t[:s] + new_pix + t[e:]
    print("1. Iconos redibujados y pulidos.")

# ---- 2. Filas de beneficios alineadas ----
old_rows = """        for kind, txt in feats:
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
            pv.addLayout(row)"""
new_rows = """        for kind, txt in feats:
            row = QHBoxLayout()
            row.setSpacing(10)
            row.setContentsMargins(0, 0, 0, 0)
            ic = QLabel()
            ic.setFixedSize(18, 18)
            ic.setPixmap(_lic_pix(kind, "#c9d1d9", 16))
            ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
            row.addWidget(ic, 0, Qt.AlignmentFlag.AlignTop)
            lb = QLabel(txt)
            lb.setStyleSheet(
                f"color: {MUTED}; font-size: 10.5px; padding-top: 1px;")
            lb.setWordWrap(True)
            lb.setMaximumWidth(190)
            row.addWidget(lb)
            row.addStretch()
            pv.addLayout(row)"""
if old_rows in t:
    t = t.replace(old_rows, new_rows, 1)
    print("2. Filas alineadas como el mockup.")

# ---- 3. Linea neon entre paneles ----
old_add = "        body.addWidget(left)"
new_add = """        body.addWidget(left)

        neon = QFrame()
        neon.setFixedWidth(2)
        neon.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:0,y2:1,"
            " stop:0 rgba(124,92,255,30), stop:0.5 #7c5cff,"
            " stop:1 rgba(124,92,255,30));")
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
        ne = QGraphicsDropShadowEffect(neon)
        ne.setBlurRadius(14)
        ne.setOffset(0, 0)
        ne.setColor(QColor("#7c5cff"))
        neon.setGraphicsEffect(ne)
        body.addWidget(neon)"""
if old_add in t:
    t = t.replace(old_add, new_add, 1)
    print("3. Linea neon violeta entre paneles.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
