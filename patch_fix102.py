from pathlib import Path
import re, ast

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

# 0. QSizePolicy disponible
if "QSizePolicy," not in t:
    t = t.replace(
        "QScrollArea, QSlider, QSpinBox, QStackedWidget,",
        "QScrollArea, QSizePolicy, QSlider, QSpinBox, QStackedWidget,",
        1,
    )
    print("0. QSizePolicy importado.")

# 1. NavButton alineado (sin lineas sueltas)
new_nav = '''class NavButton(QFrame):
    clicked = Signal()

    def __init__(self, glyph, text, parent=None):
        super().__init__(parent)
        self.setFixedHeight(44)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 0, 14, 0)
        lay.setSpacing(12)
        self.icon = IconLabel(glyph, 15, MUTED)
        self.icon.setFixedSize(20, 20)
        self.label = QLabel(text)
        self.label.setStyleSheet(
            f"color: {MUTED}; font-size: 13px; background: transparent;"
            " border: none;"
        )
        lay.addWidget(self.icon)
        lay.addWidget(self.label)
        lay.addStretch()
        self.set_active(False)

    def mouseReleaseEvent(self, event):
        self.clicked.emit()

    def set_active(self, active):
        if active:
            self.setStyleSheet(
                "NavButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                " stop:0 rgba(45,212,191,26), stop:1 rgba(139,92,246,26));"
                f" border: 1px solid {BORDER}; border-radius: 10px; }}"
            )
            self.icon.setStyleSheet(f"color: {TEAL}; background: transparent;")
            self.label.setStyleSheet(
                f"color: {TEXT}; font-size: 13px; font-weight: 600;"
                " background: transparent; border: none;"
            )
        else:
            self.setStyleSheet(
                "NavButton { background: transparent; border: 1px solid"
                " transparent; border-radius: 10px; }"
                f"NavButton:hover {{ background: {CARD}; }}"
            )
            self.icon.setStyleSheet(f"color: {MUTED}; background: transparent;")
            self.label.setStyleSheet(
                f"color: {MUTED}; font-size: 13px; background: transparent;"
                " border: none;"
            )


'''
t = re.sub(
    r"class NavButton\(QFrame\):[\s\S]*?(?=\nclass SquareButton)",
    new_nav,
    t,
    count=1,
)
print("1. NavButton alineado.")

# 2. VoiceCard con textos que encogen (nunca se sale)
new_card = '''class VoiceCard(QFrame):
    clicked = Signal()
    fav_toggled = Signal()

    def __init__(self, window, name, premium, selected, favorite, parent=None):
        super().__init__(parent)
        self.window = window
        self.voice_name = name
        self.setFixedHeight(84)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 0, 10, 0)
        lay.setSpacing(10)
        photo = QLabel()
        photo.setFixedSize(46, 46)
        photo.setPixmap(window._avatar_pixmap(name))
        photo.setScaledContents(True)
        photo.setStyleSheet("background: transparent;")
        lay.addWidget(photo)
        texts_widget = QWidget()
        texts_widget.setStyleSheet("background: transparent;")
        texts_widget.setMinimumWidth(0)
        texts_widget.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred
        )
        tw = QVBoxLayout(texts_widget)
        tw.setContentsMargins(0, 0, 0, 0)
        tw.setSpacing(3)
        n = QLabel(window._display_voice_name(name))
        n.setStyleSheet(
            f"color: {TEXT}; font-size: 12px; font-weight: 600;"
            " background: transparent;"
        )
        s = QLabel(window._voice_subtitle(name, premium))
        s.setStyleSheet(
            f"color: {MUTED}; font-size: 10px; background: transparent;"
        )
        tw.addWidget(n)
        tw.addWidget(s)
        lay.addWidget(texts_widget, 1)
        if premium:
            badge = QLabel("Pro")
            badge.setStyleSheet(
                f"background: {PURPLE}; color: white; border-radius: 6px;"
                " font-size: 9px; font-weight: 700; padding: 3px 6px;"
            )
            lay.addWidget(badge)
        self.heart = QPushButton()
        self.heart.setFixedSize(34, 34)
        self.heart.setIcon(QIcon(make_icon(
            "heart_fill" if favorite else "heart",
            RED if favorite else MUTED, 16)))
        self.heart.setIconSize(QSize(16, 16))
        self.heart.setStyleSheet(
            "QPushButton { background: transparent; border: none;"
            " border-radius: 10px; }"
            f"QPushButton:hover {{ background: {CARD2}; }}"
        )
        self.heart.clicked.connect(self.fav_toggled.emit)
        lay.addWidget(self.heart)
        self.set_selected(selected)

    def set_selected(self, selected):
        if selected:
            self.setStyleSheet(
                f"VoiceCard {{ background: {CARD2}; border: 1px solid"
                f" {PURPLE}; border-radius: 14px; }}"
            )
        else:
            self.setStyleSheet(
                f"VoiceCard {{ background: {CARD}; border: 1px solid"
                f" {BORDER}; border-radius: 14px; }}"
                f"VoiceCard:hover {{ background: {CARD2}; }}"
            )

    def mouseReleaseEvent(self, event):
        self.clicked.emit()


'''
t = re.sub(
    r"class VoiceCard\(QFrame\):[\s\S]*?(?=\nclass StatsCard)",
    new_card,
    t,
    count=1,
)
print("2. VoiceCard responsive.")

# 3. Sidebar reconstruido (alineado, sin lineas)
new_sidebar = '''        # ---------- SIDEBAR ----------
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(232)
        self.sidebar.setStyleSheet(
            f"QFrame {{ background: {SIDE_BG}; border: none; }}"
        )
        sb = QVBoxLayout(self.sidebar)
        sb.setContentsMargins(14, 14, 14, 14)
        sb.setSpacing(4)
        self.hamburger = SquareButton("\\uE700", "Menu")
        sb.addWidget(self.hamburger, 0, Qt.AlignmentFlag.AlignLeft)
        sb.addSpacing(10)
        logo = QLabel()
        lp = self._resource_path(Path("assets") / "icons" / "logo.png")
        if not lp.exists():
            lp = self._resource_path(Path("assets") / "icons" / "icon.ico")
        if lp.exists():
            logo.setPixmap(QPixmap(str(lp)).scaledToHeight(
                40, Qt.TransformationMode.SmoothTransformation))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet("background: transparent;")
        self._logo_name = QLabel("WillpoVoice")
        self._logo_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._logo_name.setStyleSheet(
            f"color: {TEXT}; font-size: 15px; font-weight: 700;"
            " background: transparent;"
        )
        self._logo_ver = QLabel("v1.2.1")
        self._logo_ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._logo_ver.setStyleSheet(
            f"color: {MUTED}; font-size: 10px; background: transparent;"
        )
        sb.addWidget(logo)
        sb.addWidget(self._logo_name)
        sb.addWidget(self._logo_ver)
        sb.addSpacing(16)
        self._nav = []
        for glyph, text, page in (
            ("\\uE80F", "Inicio", 0), ("\\uE81C", "Historial", 1),
            ("\\uE720", "Voces", 2), ("\\uEB51", "Favoritos", 3),
            ("\\uE8B7", "Proyectos", 4), ("\\uE713", "Ajustes", 5),
        ):
            btn = NavButton(glyph, text)
            btn.clicked.connect(lambda _=False, p=page: self._switch_page(p))
            sb.addWidget(btn)
            self._nav.append((btn, page))
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {BORDER};")
        sb.addWidget(sep)
        sb.addSpacing(4)
        for glyph, text, fn in (
            ("\\uE897", "Ayuda", self.show_help),
            ("\\uE95B", "Soporte", self.open_support),
        ):
            btn = NavButton(glyph, text)
            btn.clicked.connect(lambda _=False, f=fn: f())
            sb.addWidget(btn)
        sb.addStretch()
        prem = QFrame()
        prem.setStyleSheet(
            "QFrame { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            " stop:0 #241a3d, stop:1 #3b2a63); border-radius: 14px; }"
        )
        pl = QVBoxLayout(prem)
        pl.setContentsMargins(14, 14, 14, 14)
        pt = QLabel("👑  WillpoVoice Premium")
        pt.setStyleSheet(
            f"color: {TEXT}; font-size: 12px; font-weight: 700;"
            " background: transparent;"
        )
        pd = QLabel("Desbloquea todas las voces y funciones premium.")
        pd.setWordWrap(True)
        pd.setStyleSheet(
            f"color: {MUTED}; font-size: 10px; background: transparent;"
        )
        pb = QPushButton("✨ Ver planes")
        pb.setCursor(Qt.CursorShape.PointingHandCursor)
        pb.setStyleSheet(
            "QPushButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f" stop:0 {BLUE}, stop:1 {PURPLE}); color: white; border: none;"
            " border-radius: 8px; padding: 7px 12px; font-weight: 600; }"
        )
        pb.clicked.connect(self.open_support)
        pl.addWidget(pt)
        pl.addWidget(pd)
        pl.addWidget(pb, 0, Qt.AlignmentFlag.AlignLeft)
        self._prem_card = prem
        sb.addWidget(prem)
        root.addWidget(self.sidebar)
'''
t = re.sub(
    r"        # ---------- SIDEBAR ----------[\s\S]*?root\.addWidget\(self\.sidebar\)",
    new_sidebar.rstrip("\n"),
    t,
    count=1,
)
print("3. Sidebar reconstruido.")

# 4. Panel derecho responsive
new_right = '''        # ---------- PANEL DERECHO ----------
        self.right_panel = QFrame()
        self.right_panel.setStyleSheet(
            f"QFrame {{ background: {BG}; border-left: 1px solid {BORDER}; }}"
        )
        self.right_panel.setMinimumWidth(300)
        self.right_panel.setMaximumWidth(360)
        rp = QVBoxLayout(self.right_panel)
        rp.setContentsMargins(14, 14, 14, 14)
        rp.setSpacing(10)
        rh = QHBoxLayout()
        rt = QLabel("Voces recomendadas")
        rt.setStyleSheet(
            f"color: {TEXT}; font-size: 14px; font-weight: 700;"
        )
        self.btn_ver_all = ToolButton("", "Ver todas")
        rh.addWidget(rt)
        rh.addStretch()
        rh.addWidget(self.btn_ver_all)
        rp.addLayout(rh)
        search_row = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Buscar voces...")
        self.search_edit.setStyleSheet(
            f"QLineEdit {{ background: {CARD}; border: 1px solid {BORDER};"
            " border-radius: 10px; padding: 8px 12px; }"
        )
        self.filter_btn = SquareButton("\\uE71C", "Filtro")
        search_row.addWidget(self.search_edit, 1)
        search_row.addWidget(self.filter_btn)
        rp.addLayout(search_row)
        tabs = QHBoxLayout()
        tabs.setSpacing(4)
        self.rtab_all = TabButton("Todas")
        self.rtab_pro = TabButton("👑 Premium")
        self.rtab_fav = TabButton("❤ Favoritas")
        self.rtab_all.set_active(True)
        tabs.addWidget(self.rtab_all)
        tabs.addWidget(self.rtab_pro)
        tabs.addWidget(self.rtab_fav)
        tabs.addStretch()
        rp.addLayout(tabs)
        self.cards_scroll = QScrollArea()
        self.cards_scroll.setWidgetResizable(True)
        self.cards_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.cards_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.cards_scroll.setStyleSheet(
            "QScrollArea { background: transparent; border: none; }"
        )
        self.cards_container = QWidget()
        self.cards_container.setStyleSheet("background: transparent;")
        self.voice_cards_layout = QVBoxLayout(self.cards_container)
        self.voice_cards_layout.setContentsMargins(0, 0, 4, 0)
        self.voice_cards_layout.setSpacing(8)
        self.cards_scroll.setWidget(self.cards_container)
        rp.addWidget(self.cards_scroll, 1)
        root.addWidget(self.right_panel)

'''
t = re.sub(
    r"        # ---------- PANEL DERECHO ----------[\s\S]*?(?=        self\.player_timer = QTimer\(self\))",
    new_right,
    t,
    count=1,
)
print("4. Panel derecho responsive.")

# 5. Banderas en combo de idioma
old_lang = '''        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["Español (España)", "Inglés (EEUU)", "Todos"])'''
new_lang = old_lang + '''
        self.lang_combo.setItemIcon(0, QIcon(self._flag_pixmap("es")))
        self.lang_combo.setItemIcon(1, QIcon(self._flag_pixmap("us")))
        self.lang_combo.setItemIcon(2, QIcon(self._flag_pixmap("world")))'''
if old_lang in t:
    t = t.replace(old_lang, new_lang, 1)
    print("5. Banderas en combo de idioma.")

# 6. Metodo de banderas
if "def _flag_pixmap" not in t:
    t = t.replace(
        "    def _connect_signals(self):",
        '''    def _flag_pixmap(self, kind):
        w, h = 22, 16
        pix = QPixmap(w, h)
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        if kind == "es":
            p.fillRect(0, 0, w, h, QColor("#aa151b"))
            p.fillRect(0, 4, w, 8, QColor("#f1bf00"))
        elif kind == "us":
            for i in range(7):
                c = "#b22234" if i % 2 == 0 else "#ffffff"
                p.fillRect(0, i * h // 7, w, h // 7 + 1, QColor(c))
            p.fillRect(0, 0, 10, 8, QColor("#3c3b6e"))
        else:
            p.fillRect(0, 0, w, h, QColor("#1d4ed8"))
            p.setPen(QPen(QColor("#ffffff"), 1.5))
            p.drawLine(0, h // 2, w, h // 2)
            p.drawLine(w // 2, 0, w // 2, h)
            p.drawEllipse(4, 3, w - 8, h - 6)
        p.end()
        return pix

    def _add_neon(self, widget, color):
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
        eff = QGraphicsDropShadowEffect(widget)
        eff.setBlurRadius(18)
        eff.setOffset(0, 0)
        eff.setColor(QColor(color))
        widget.setGraphicsEffect(eff)

    def _connect_signals(self):''',
        1,
    )
    print("6. _flag_pixmap y _add_neon agregados.")

# 7. Neon en botones principales
if "self._add_neon(self.speak_button" not in t:
    t = t.replace(
        "p0.addLayout(acts)",
        "p0.addLayout(acts)\n"
        "        self._add_neon(self.speak_button, BLUE)\n"
        "        self._add_neon(self.stop_button, MAGENTA)\n"
        "        self._add_neon(self.export_button, TEAL)",
        1,
    )
    print("7. Efecto neon aplicado.")

# 8. Iconos con trazo mas profesional
t = t.replace(
    "pen = QPen(QColor(color), max(1.3, size * 0.09))",
    "pen = QPen(QColor(color), max(1.6, size * 0.11))",
    1,
)
print("8. Trazo de iconos reforzado.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
