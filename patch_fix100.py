from pathlib import Path
import ast

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

# 1. Import QPolygon + math
if "QPolygon" not in t:
    t = t.replace(
        "from PySide6.QtCore import Qt, QThread, QTimer, QUrl, Signal, QSize",
        "from PySide6.QtCore import Qt, QThread, QTimer, QUrl, Signal, QSize, QPolygon",
        1,
    )
    print("1. QPolygon importado.")

# 2. Fabrica de iconos dibujados (reemplaza Segoe MDL2 que no renderiza)
if "def make_icon" not in t:
    factory = '''
GLYPH_MAP = {
    "\\uE700": "menu", "\\uE80F": "home", "\\uE81C": "history",
    "\\uE720": "mic", "\\uEB51": "heart", "\\uEB52": "heart_fill",
    "\\uE8B7": "folder", "\\uE713": "gear", "\\uE897": "help",
    "\\uE95B": "headset", "\\uE768": "play", "\\uE71A": "stop",
    "\\uE896": "download", "\\uE8C8": "copy", "\\uE708": "moon",
    "\\uE74D": "trash", "\\uE77F": "paste", "\\uE774": "globe",
    "\\uE995": "wave", "\\uE71C": "filter", "\\uE767": "volume",
}


def make_icon(kind, color, size=20):
    import math
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(QColor(color), max(1.3, size * 0.09))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    s = size

    def pt(fx, fy):
        return QPoint(int(fx * s), int(fy * s))

    def poly(*coords):
        return QPolygon([pt(x, y) for x, y in coords])

    if kind == "menu":
        for y in (0.3, 0.5, 0.7):
            p.drawLine(pt(0.2, y), pt(0.8, y))
    elif kind == "home":
        p.drawPolyline(poly((0.5, 0.15), (0.15, 0.48), (0.15, 0.85),
                            (0.85, 0.85), (0.85, 0.48), (0.5, 0.15)))
    elif kind == "history":
        p.drawEllipse(int(s * 0.15), int(s * 0.15), int(s * 0.7), int(s * 0.7))
        p.drawLine(pt(0.5, 0.5), pt(0.5, 0.3))
        p.drawLine(pt(0.5, 0.5), pt(0.66, 0.58))
    elif kind == "mic":
        p.drawRoundedRect(int(s * 0.38), int(s * 0.12), int(s * 0.24), int(s * 0.42), 4, 4)
        p.drawArc(int(s * 0.24), int(s * 0.28), int(s * 0.52), int(s * 0.52), 180 * 16, 180 * 16)
        p.drawLine(pt(0.5, 0.8), pt(0.5, 0.9))
    elif kind in ("heart", "heart_fill"):
        path = QPainterPath()
        path.moveTo(s * 0.5, s * 0.85)
        path.cubicTo(s * 0.05, s * 0.5, s * 0.15, s * 0.1, s * 0.5, s * 0.3)
        path.cubicTo(s * 0.85, s * 0.1, s * 0.95, s * 0.5, s * 0.5, s * 0.85)
        if kind == "heart_fill":
            p.setBrush(QColor(color))
        p.drawPath(path)
    elif kind == "folder":
        p.drawPolyline(poly((0.12, 0.3), (0.12, 0.22), (0.42, 0.22), (0.5, 0.3)))
        p.drawRoundedRect(int(s * 0.12), int(s * 0.3), int(s * 0.76), int(s * 0.52), 3, 3)
    elif kind == "gear":
        p.drawEllipse(int(s * 0.32), int(s * 0.32), int(s * 0.36), int(s * 0.36))
        for i in range(8):
            a = math.radians(i * 45)
            p.drawLine(pt(0.5 + 0.32 * math.cos(a), 0.5 + 0.32 * math.sin(a)),
                       pt(0.5 + 0.45 * math.cos(a), 0.5 + 0.45 * math.sin(a)))
    elif kind == "help":
        p.drawEllipse(int(s * 0.15), int(s * 0.15), int(s * 0.7), int(s * 0.7))
        p.setFont(QFont("Segoe UI", max(8, int(s * 0.5)), QFont.Weight.Bold))
        p.drawText(QRect(0, 0, s, s), Qt.AlignmentFlag.AlignCenter, "?")
    elif kind == "headset":
        p.drawArc(int(s * 0.18), int(s * 0.15), int(s * 0.64), int(s * 0.64), 0, 180 * 16)
        p.drawRoundedRect(int(s * 0.14), int(s * 0.5), int(s * 0.14), int(s * 0.28), 3, 3)
        p.drawRoundedRect(int(s * 0.72), int(s * 0.5), int(s * 0.14), int(s * 0.28), 3, 3)
    elif kind == "play":
        p.setBrush(QColor(color))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPolygon(poly((0.32, 0.2), (0.32, 0.8), (0.8, 0.5)))
    elif kind == "stop":
        p.setBrush(QColor(color))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(int(s * 0.3), int(s * 0.3), int(s * 0.4), int(s * 0.4), 3, 3)
    elif kind == "download":
        p.drawLine(pt(0.5, 0.18), pt(0.5, 0.6))
        p.drawPolyline(poly((0.32, 0.44), (0.5, 0.62), (0.68, 0.44)))
        p.drawLine(pt(0.25, 0.8), pt(0.75, 0.8))
    elif kind == "copy":
        p.drawRoundedRect(int(s * 0.32), int(s * 0.32), int(s * 0.48), int(s * 0.52), 3, 3)
        p.drawRoundedRect(int(s * 0.2), int(s * 0.16), int(s * 0.48), int(s * 0.52), 3, 3)
    elif kind == "moon":
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(color))
        p.drawEllipse(int(s * 0.18), int(s * 0.18), int(s * 0.64), int(s * 0.64))
        p.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        p.drawEllipse(int(s * 0.38), int(s * 0.1), int(s * 0.55), int(s * 0.55))
    elif kind == "trash":
        p.drawLine(pt(0.25, 0.28), pt(0.75, 0.28))
        p.drawLine(pt(0.42, 0.18), pt(0.58, 0.18))
        p.drawRoundedRect(int(s * 0.3), int(s * 0.28), int(s * 0.4), int(s * 0.55), 3, 3)
    elif kind == "paste":
        p.drawRoundedRect(int(s * 0.24), int(s * 0.2), int(s * 0.52), int(s * 0.65), 3, 3)
        p.drawRect(int(s * 0.4), int(s * 0.12), int(s * 0.2), int(s * 0.14))
    elif kind == "globe":
        p.drawEllipse(int(s * 0.15), int(s * 0.15), int(s * 0.7), int(s * 0.7))
        p.drawLine(pt(0.15, 0.5), pt(0.85, 0.5))
        p.drawEllipse(int(s * 0.35), int(s * 0.15), int(s * 0.3), int(s * 0.7))
    elif kind == "wave":
        p.drawPolyline(poly((0.12, 0.5), (0.28, 0.5), (0.38, 0.22),
                            (0.5, 0.78), (0.62, 0.35), (0.72, 0.5), (0.88, 0.5)))
    elif kind == "filter":
        p.drawLine(pt(0.2, 0.3), pt(0.8, 0.3))
        p.drawLine(pt(0.3, 0.5), pt(0.7, 0.5))
        p.drawLine(pt(0.4, 0.7), pt(0.6, 0.7))
    elif kind == "volume":
        p.setBrush(QColor(color))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPolygon(poly((0.18, 0.4), (0.34, 0.4), (0.5, 0.24),
                           (0.5, 0.76), (0.34, 0.6), (0.18, 0.6)))
        p.setPen(pen)
        p.drawArc(int(s * 0.5), int(s * 0.3), int(s * 0.4), int(s * 0.4), -60 * 16, 120 * 16)
    else:
        p.setBrush(QColor(color))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(int(s * 0.3), int(s * 0.3), int(s * 0.4), int(s * 0.4))
    p.end()
    return pix


'''
    t = t.replace("class IconLabel(QLabel):", factory + "class IconLabel(QLabel):", 1)
    print("2. Fabrica de iconos agregada.")

# 3. IconLabel usa pixmaps dibujados (no fuente MDL2)
old_il = '''class IconLabel(QLabel):
    def __init__(self, glyph, size=16, color=MUTED, parent=None):
        super().__init__(parent)
        self.setFont(_mdls(size))
        self.setText(glyph)
        self.setStyleSheet(f"color: {color}; background: transparent;")'''
new_il = '''class IconLabel(QLabel):
    def __init__(self, glyph, size=16, color=MUTED, parent=None):
        super().__init__(parent)
        kind = GLYPH_MAP.get(glyph, "dot")
        self.setPixmap(make_icon(kind, color, size + 4))
        self.setStyleSheet("background: transparent;")'''
if old_il in t:
    t = t.replace(old_il, new_il, 1)
    print("3. IconLabel con pixmaps.")

# 4. NavButton modo colapsado
if "def set_collapsed" not in t:
    t = t.replace(
        "class SquareButton(QFrame):",
        '''    def set_collapsed(self, collapsed):
        self.label.setVisible(not collapsed)
        lay = self.layout()
        if collapsed:
            lay.setContentsMargins(0, 0, 0, 0)
            self.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            lay.setContentsMargins(16, 0, 12, 0)
            self.icon.setAlignment(Qt.AlignmentFlag.AlignLeft)


class SquareButton(QFrame):''',
        1,
    )
    print("4. NavButton.set_collapsed agregado.")

# 5. Hamburguesa: colapsa a riel (nunca se pierde)
old_ham = """        self.hamburger.clicked.connect(
            lambda: self.sidebar.setVisible(not self.sidebar.isVisible()))"""
if old_ham in t:
    t = t.replace(old_ham, "        self.hamburger.clicked.connect(self._toggle_sidebar)", 1)
    print("5. Hamburguesa conectada a _toggle_sidebar.")

# 6. Referencias de logo y premium guardadas
for old, new in (
    ("        name_l = QLabel(\"WillpoVoice\")", "        self._logo_name = QLabel(\"WillpoVoice\")"),
    ("        name_l.setStyleSheet(", "        self._logo_name.setStyleSheet("),
    ("        name_l.setAlignment(", "        self._logo_name.setAlignment("),
    ("        logo_box.addWidget(name_l)", "        logo_box.addWidget(self._logo_name)"),
    ("        ver_l = QLabel(\"v1.2.1\")", "        self._logo_ver = QLabel(\"v1.2.1\")"),
    ("        ver_l.setStyleSheet(", "        self._logo_ver.setStyleSheet("),
    ("        ver_l.setAlignment(", "        self._logo_ver.setAlignment("),
    ("        logo_box.addWidget(ver_l)", "        logo_box.addWidget(self._logo_ver)"),
    ("        prem = QFrame()", "        self._prem_card = QFrame()"),
    ("        prem.setStyleSheet(", "        self._prem_card.setStyleSheet("),
    ("        pl = QVBoxLayout(prem)", "        pl = QVBoxLayout(self._prem_card)"),
    ("        sb.addWidget(prem)", "        sb.addWidget(self._prem_card)"),
):
    t = t.replace(old, new, 1)
print("6. Referencias guardadas.")

# 7. Metodo _toggle_sidebar
if "def _toggle_sidebar" not in t:
    t = t.replace(
        "    def _switch_page(self, index):",
        '''    def _toggle_sidebar(self):
        collapsed = self.sidebar.width() > 100
        self.sidebar.setFixedWidth(68 if collapsed else 232)
        for btn, _page in self._nav:
            btn.set_collapsed(collapsed)
        self._logo_name.setVisible(not collapsed)
        self._logo_ver.setVisible(not collapsed)
        self._prem_card.setVisible(not collapsed)

    def _switch_page(self, index):''',
        1,
    )
    print("7. _toggle_sidebar agregado.")

# 8. Portada con frames de respaldo
old_cover = """        cp = self._resource_path(Path("assets") / "icons" / "portada.png")
        if cp.exists():"""
new_cover = """        cp = self._resource_path(Path("assets") / "icons" / "portada.png")
        if not cp.exists():
            frames_dir = self._resource_path(
                Path("assets") / "icons" / "portada_frames")
            if frames_dir.exists():
                files = sorted(frames_dir.glob("*.jpg")) or sorted(
                    frames_dir.glob("*.png"))
                if files:
                    cp = files[len(files) // 2]
        if cp.exists():"""
if old_cover in t:
    t = t.replace(old_cover, new_cover, 1)
    print("8. Portada con respaldo de frames.")

# 9. Combo de voz con avatar + nombre corto
old_add = """            self.voice_combo.clear()
            for v in voices:
                self.voice_combo.addItem(v)"""
new_add = """            self.voice_combo.clear()
            for v in voices:
                self.voice_combo.addItem(self._display_voice_name(v))
                idx = self.voice_combo.count() - 1
                self.voice_combo.setItemData(
                    idx, v, Qt.ItemDataRole.UserRole)
                self.voice_combo.setItemIcon(
                    idx, QIcon(self._avatar_pixmap(v)))"""
if old_add in t:
    t = t.replace(old_add, new_add, 1)
    print("9. Combo con avatares y nombres cortos.")

# 10. _current_voice + seleccion por dato
old_sel = """    def _select_voice(self, name):
        self._selected_voice = name
        self.voice_combo.blockSignals(True)
        self.voice_combo.setCurrentText(name)
        self.voice_combo.blockSignals(False)"""
new_sel = """    def _current_voice(self):
        data = self.voice_combo.currentData(Qt.ItemDataRole.UserRole)
        return data or self.voice_combo.currentText()

    def _select_voice(self, name):
        self._selected_voice = name
        for i in range(self.voice_combo.count()):
            if self.voice_combo.itemData(
                    i, Qt.ItemDataRole.UserRole) == name:
                self.voice_combo.blockSignals(True)
                self.voice_combo.setCurrentIndex(i)
                self.voice_combo.blockSignals(False)
                break"""
if old_sel in t:
    t = t.replace(old_sel, new_sel, 1)
    print("10. Seleccion por dato interno.")

old_cb = """    def _on_combo_voice(self, name):
        if name:
            self._select_voice(name)"""
new_cb = """    def _on_combo_voice(self, name):
        voice = self._current_voice()
        if voice:
            self._select_voice(voice)"""
if old_cb in t:
    t = t.replace(old_cb, new_cb, 1)

t = t.replace("self.voice_combo.currentText().strip()", "self._current_voice()")
t = t.replace(
    'self.settings["last_voice"] = self.voice_combo.currentText()',
    'self.settings["last_voice"] = self._current_voice()',
)
old_last = """            if last in voices:
                self.voice_combo.setCurrentText(last)"""
new_last = """            if last in voices:
                self._select_voice(last)"""
if old_last in t:
    t = t.replace(old_last, new_last, 1)
old_pref = """                self.voice_combo.setCurrentText(pref)"""
new_pref = """                self._select_voice(pref)"""
if old_pref in t:
    t = t.replace(old_pref, new_pref, 1)
print("11. Lecturas de voz actualizadas.")

# 12. Corazon dibujado en tarjetas
old_heart = """        self.heart = QPushButton()
        self.heart.setFixedSize(38, 38)
        self.heart.setFont(_mdls(15))
        self.heart.setText("\\uEB52" if favorite else "\\uEB51")"""
new_heart = """        self.heart = QPushButton()
        self.heart.setFixedSize(38, 38)
        self.heart.setIcon(QIcon(make_icon(
            "heart_fill" if favorite else "heart",
            RED if favorite else MUTED, 18)))
        self.heart.setIconSize(QSize(18, 18))"""
if old_heart in t:
    t = t.replace(old_heart, new_heart, 1)
    print("12. Corazon dibujado en tarjetas.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
