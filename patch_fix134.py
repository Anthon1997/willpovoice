from pathlib import Path
import re, ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# ---- 1. RECOPILACION ----
for marker in ("class VoiceCard", "def _voice_subtitle",
               "search_row = QHBoxLayout()", "btn_ver_all = ToolButton"):
    print(f"--- {marker!r} indice:", t.find(marker))

# ---- 2. Icono lupa en make_icon ----
old_else = """    else:
        p.setBrush(QColor(color))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(int(s * 0.3), int(s * 0.3), int(s * 0.4), int(s * 0.4))"""
new_search = """    elif kind == "search":
        p.drawEllipse(int(s * 0.2), int(s * 0.2), int(s * 0.42), int(s * 0.42))
        p.drawLine(pt(0.52, 0.52), pt(0.8, 0.8))
""" + old_else
if '"search"' not in t:
    t = t.replace(old_else, new_search, 1)
    print("2. Icono search agregado.")

# ---- 3. VoiceCard clon foto 2 ----
new_card = '''class VoiceCard(QFrame):
    clicked = Signal()
    fav_toggled = Signal()

    def __init__(self, window, name, premium, selected, favorite, parent=None):
        super().__init__(parent)
        self.window = window
        self.voice_name = name
        self.setFixedHeight(70)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 0, 8, 0)
        lay.setSpacing(10)
        photo = QLabel()
        photo.setFixedSize(40, 40)
        photo.setPixmap(window._avatar_pixmap(
            name, "#f5b301" if premium else "#232f4b"))
        photo.setScaledContents(True)
        photo.setStyleSheet("background: transparent;")
        lay.addWidget(photo)
        tw = QWidget()
        tw.setStyleSheet("background: transparent;")
        tw.setMinimumWidth(90)
        tw.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        tl = QVBoxLayout(tw)
        tl.setContentsMargins(0, 0, 0, 0)
        tl.setSpacing(2)
        n = QLabel(window._display_voice_name(name))
        n.setStyleSheet(
            f"color: {TEXT}; font-size: 12px; font-weight: 600;"
            " background: transparent;"
        )
        s = QLabel(window._voice_subtitle(name, premium))
        s.setStyleSheet(
            f"color: {MUTED}; font-size: 10px; background: transparent;"
        )
        tl.addWidget(n)
        tl.addWidget(s)
        lay.addWidget(tw, 1)
        if premium:
            badge = QLabel("Pro")
            badge.setStyleSheet(
                f"background: {PURPLE}; color: white; border-radius: 5px;"
                " font-size: 8px; font-weight: 700; padding: 2px 5px;"
            )
            badge.setFixedHeight(17)
            badge.setMaximumWidth(38)
            badge.setSizePolicy(
                QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            lay.addWidget(badge)
        self.heart = QPushButton()
        self.heart.setFixedSize(28, 28)
        self.heart.setIcon(QIcon(make_icon(
            "heart_fill" if favorite else "heart",
            RED if favorite else MUTED, 14)))
        self.heart.setIconSize(QSize(14, 14))
        self.heart.setStyleSheet(
            "QPushButton { background: transparent; border: none;"
            f" border-radius: 8px; }} QPushButton:hover {{ background: {CARD2}; }}"
        )
        self.heart.clicked.connect(self.fav_toggled.emit)
        lay.addWidget(self.heart)
        self.set_selected(selected)

    def set_selected(self, selected):
        if selected:
            self.setStyleSheet(
                f"VoiceCard {{ background: {CARD2}; border: 1px solid #6d5dfc;"
                " border-radius: 12px; }}"
            )
        else:
            self.setStyleSheet(
                f"VoiceCard {{ background: {CARD}; border: none;"
                f" border-radius: 12px; }} VoiceCard:hover {{ background: {CARD2}; }}"
            )

    def mouseReleaseEvent(self, event):
        self.clicked.emit()


'''
t = re.sub(
    r"class VoiceCard\(QFrame\):[\s\S]*?(?=\nclass MainWindow)",
    new_card,
    t,
    count=1,
)
print("3. VoiceCard clon foto 2.")

# ---- 4. Subtitulos grises de acento (como foto 2) ----
old_sub = '''    def _voice_subtitle(self, name, premium):
        return "WillpoVoice Premium" if premium else "Voz estándar"'''
new_sub = '''    def _voice_subtitle(self, name, premium):
        subs = ["Acento neutro · Profesional", "Acento suave · Natural",
                "Acento cálido · Amigable", "Acento claro · Formal"]
        return subs[len(name) % len(subs)] if premium else "Voz estándar"'''
if old_sub in t:
    t = t.replace(old_sub, new_sub, 1)
    print("4. Subtitulos de acento grises.")

# ---- 5. Buscador con lupa dentro ----
old_search = """    search_row = QHBoxLayout()
    self.search_edit = QLineEdit()
    self.search_edit.setPlaceholderText("Buscar voces...")
    self.search_edit.setStyleSheet(
        f"QLineEdit {{ background: {CARD}; border: 1px solid {BORDER};"
        " border-radius: 10px; padding: 8px 12px; }"
    )
    self.filter_btn = SquareButton("filter", "Filtro")
    search_row.addWidget(self.search_edit, 1)
    search_row.addWidget(self.filter_btn)
    rp.addLayout(search_row)"""
new_search_box = """    search_row = QHBoxLayout()
    search_box = QFrame()
    search_box.setObjectName("searchBox")
    search_box.setStyleSheet(
        f"QFrame#searchBox {{ background: {CARD}; border: 1px solid"
        f" {BORDER}; border-radius: 10px; }}"
    )
    sbl = QHBoxLayout(search_box)
    sbl.setContentsMargins(10, 0, 10, 0)
    sbl.setSpacing(8)
    sbl.addWidget(IconLabel("search", 13, MUTED))
    self.search_edit = QLineEdit()
    self.search_edit.setPlaceholderText("Buscar voces...")
    self.search_edit.setStyleSheet(
        "QLineEdit { background: transparent; border: none; padding: 8px 0px; }"
    )
    sbl.addWidget(self.search_edit)
    self.filter_btn = SquareButton("filter", "Filtro")
    self.filter_btn.setFixedSize(40, 40)
    search_row.addWidget(search_box, 1)
    search_row.addWidget(self.filter_btn)
    rp.addLayout(search_row)"""
if old_search in t:
    t = t.replace(old_search, new_search_box, 1)
    print("5. Buscador con lupa integrada.")

# ---- 6. Ver todas con borde ----
old_ver = '    self.btn_ver_all = ToolButton("", "Ver todas")'
new_ver = old_ver + """
    self.btn_ver_all.setStyleSheet(
        f"ToolButton {{ background: transparent; border: 1px solid {BORDER};"
        f" border-radius: 8px; }} ToolButton:hover {{ background: {CARD2}; }}"
    )"""
if old_ver in t:
    t = t.replace(old_ver, new_ver, 1)
    print("6. Ver todas con borde redondeado.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
