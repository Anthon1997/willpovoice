from pathlib import Path
import re, ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# --- Fix: guardar el glyph del NavButton y redraw al activar ---
if "self._glyph = glyph" not in t:
    t = t.replace(
        "self.icon.setFixedSize(20, 20)",
        "self.icon.setFixedSize(20, 20)\n        self._glyph = glyph",
        1,
    )
    t = re.sub(
        r"    def set_active\(self, active\):[\s\S]*?(?=\nclass SquareButton)",
        '''    def set_active(self, active):
        if active:
            self.setStyleSheet(
                "NavButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                " stop:0 rgba(45,212,191,26), stop:1 rgba(139,92,246,26));"
                f" border: 1px solid {BORDER}; border-radius: 10px; }}"
            )
            self.icon.setPixmap(make_icon(self._glyph, TEAL, 19))
            self.label.setStyleSheet(
                f"color: {TEXT}; font-size: 13px; font-weight: 600;"
                " background: transparent; border: none;"
            )
        else:
            self.setStyleSheet(
                "NavButton { background: transparent; border: 1px solid"
                f" transparent; border-radius: 10px; }} NavButton:hover {{ background: {CARD}; }}"
            )
            self.icon.setPixmap(make_icon(self._glyph, MUTED, 19))
            self.label.setStyleSheet(
                f"color: {MUTED}; font-size: 13px; background: transparent; border: none;"
            )


''',
        t,
        count=1,
    )
    print("Fix NavButton aplicado.")

parteB = '''

class ToolButton(QFrame):
    clicked = Signal()

    def __init__(self, glyph, text, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 6, 10, 6)
        lay.setSpacing(8)
        self.icon = IconLabel(glyph, 13, MUTED)
        self.label = QLabel(text)
        self.label.setStyleSheet(
            f"color: {MUTED}; font-size: 12px; background: transparent;"
        )
        lay.addWidget(self.icon)
        lay.addWidget(self.label)
        self.setStyleSheet(
            "ToolButton { background: transparent; border: 1px solid"
            f" transparent; border-radius: 8px; }} ToolButton:hover {{ background: {CARD2}; }}"
        )

    def mouseReleaseEvent(self, event):
        self.clicked.emit()


    # ===================== METODOS DE MainWindow =====================
def _build_ui(self):
    central = QWidget()
    self.setCentralWidget(central)
    root = QHBoxLayout(central)
    root.setContentsMargins(0, 0, 0, 0)
    root.setSpacing(0)

    # ---------- SIDEBAR ----------
    self.sidebar = QFrame()
    self.sidebar.setFixedWidth(232)
    self.sidebar.setStyleSheet(f"QFrame {{ background: {SIDE_BG}; border: none; }}")
    sb = QVBoxLayout(self.sidebar)
    sb.setContentsMargins(14, 14, 14, 14)
    sb.setSpacing(4)
    self.hamburger = SquareButton("menu", "Menu")
    self.hamburger.clicked.connect(self._toggle_sidebar)
    sb.addWidget(self.hamburger, 0, Qt.AlignmentFlag.AlignLeft)
    sb.addSpacing(8)
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
        f"color: {TEXT}; font-size: 15px; font-weight: 700; background: transparent;"
    )
    self._logo_ver = QLabel("v1.2.1")
    self._logo_ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
    self._logo_ver.setStyleSheet(
        f"color: {MUTED}; font-size: 10px; background: transparent;"
    )
    sb.addWidget(logo)
    sb.addWidget(self._logo_name)
    sb.addWidget(self._logo_ver)
    sb.addSpacing(14)
    self._nav = []
    for glyph, text, page in (
        ("home", "Inicio", 0), ("history", "Historial", 1),
        ("mic", "Voces", 2), ("heart", "Favoritos", 3),
        ("folder", "Proyectos", 4), ("gear", "Ajustes", 5),
    ):
        btn = NavButton(glyph, text)
        btn.clicked.connect(lambda _=False, pg=page: self._switch_page(pg))
        sb.addWidget(btn)
        self._nav.append((btn, page))
    sep = QFrame()
    sep.setFixedHeight(1)
    sep.setStyleSheet(f"background: {BORDER};")
    sb.addWidget(sep)
    sb.addSpacing(4)
    for glyph, text, fn in (("help", "Ayuda", self.show_help),
                            ("headset", "Soporte", self.open_support)):
        btn = NavButton(glyph, text)
        btn.clicked.connect(lambda _=False, f=fn: f())
        sb.addWidget(btn)
    sb.addStretch()
    self._prem_card = QFrame()
    self._prem_card.setStyleSheet(
        "QFrame { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
        " stop:0 #241a3d, stop:1 #3b2a63); border-radius: 14px; }"
    )
    pl = QVBoxLayout(self._prem_card)
    pl.setContentsMargins(14, 14, 14, 14)
    pt = QLabel("👑  WillpoVoice Premium")
    pt.setStyleSheet(f"color: {TEXT}; font-size: 12px; font-weight: 700; background: transparent;")
    pd = QLabel("Desbloquea todas las voces y funciones premium.")
    pd.setWordWrap(True)
    pd.setStyleSheet(f"color: {MUTED}; font-size: 10px; background: transparent;")
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
    sb.addWidget(self._prem_card)
    root.addWidget(self.sidebar)

    # ---------- PAGINAS ----------
    self.pages = QStackedWidget()
    root.addWidget(self.pages, 1)

    page0 = QWidget()
    p0 = QVBoxLayout(page0)
    p0.setContentsMargins(16, 14, 16, 14)
    p0.setSpacing(14)

    header = QFrame()
    header.setFixedHeight(190)
    header.setStyleSheet(f"QFrame {{ background: {CARD}; border-radius: 16px; }}")
    hg = QGridLayout(header)
    hg.setContentsMargins(0, 0, 0, 0)
    cover = QLabel()
    cp = self._resource_path(Path("assets") / "icons" / "portada.png")
    if not cp.exists():
        fd = self._resource_path(Path("assets") / "icons" / "portada_frames")
        if fd.exists():
            files = sorted(fd.glob("*.jpg")) or sorted(fd.glob("*.png"))
            if files:
                cp = files[len(files) // 2]
    if cp.exists():
        cover.setPixmap(QPixmap(str(cp)))
    cover.setScaledContents(True)
    cover.setStyleSheet("background: transparent; border-radius: 16px;")
    hg.addWidget(cover, 0, 0)
    titles = QWidget()
    titles.setStyleSheet("background: transparent;")
    tl2 = QVBoxLayout(titles)
    tl2.setContentsMargins(24, 16, 0, 16)
    t1 = QLabel("WillpoVoice")
    t1.setStyleSheet("color: white; font-size: 26px; font-weight: 700; background: transparent;")
    t2 = QLabel("Convierte texto en voz con voces naturales")
    t2.setStyleSheet("color: #cdd5ea; font-size: 12px; background: transparent;")
    tl2.addWidget(t1)
    tl2.addWidget(t2)
    tl2.addStretch()
    hg.addWidget(titles, 0, 0)
    p0.addWidget(header)

    stats = QHBoxLayout()
    stats.setSpacing(14)
    self.stat_voices = StatsCard("mic", TEAL, "Voces disponibles", "0")
    self.stat_langs = StatsCard("globe", BLUE, "Idiomas", "29")
    self.stat_conv = StatsCard("wave", TEAL, "Conversiones hoy",
                               str(self.settings.get("conv_today", 0)))
    for s in (self.stat_voices, self.stat_langs, self.stat_conv):
        stats.addWidget(s)
    p0.addLayout(stats)

    card = QFrame()
    card.setStyleSheet(f"QFrame {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 16px; }}")
    cl = QVBoxLayout(card)
    cl.setContentsMargins(18, 14, 18, 16)
    cl.setSpacing(12)
    top = QHBoxLayout()
    self.tab_text = TabButton("Texto manual")
    self.tab_file = TabButton("Importar archivo")
    self.tab_text.set_active(True)
    self.tab_file.clicked.connect(self._open_document_dialog)
    top.addWidget(self.tab_text)
    top.addWidget(self.tab_file)
    top.addStretch()
    self.btn_clear = ToolButton("trash", "Limpiar")
    self.btn_paste = ToolButton("paste", "Pegar")
    top.addWidget(self.btn_clear)
    top.addWidget(self.btn_paste)
    cl.addLayout(top)

    self.text_edit = QPlainTextEdit()
    self.text_edit.setPlaceholderText("Escribe aquí el texto que quieres convertir a voz...")
    self.text_edit.setFixedHeight(150)
    self.text_edit.setMinimumWidth(150)
    cl.addWidget(self.text_edit)
    self.counter_label = QLabel("0 / 5000")
    self.counter_label.setAlignment(Qt.AlignmentFlag.AlignRight)
    self.counter_label.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
    cl.addWidget(self.counter_label)

    sel = QHBoxLayout()
    sel.setSpacing(10)
    l1 = QLabel("Idioma")
    l1.setStyleSheet(f"color: {MUTED}; font-size: 12px;")
    self.lang_combo = QComboBox()
    self.lang_combo.addItems(["Español (España)", "Inglés (EEUU)", "Todos"])
    self.lang_combo.setItemIcon(0, QIcon(self._flag_pixmap("es")))
    self.lang_combo.setItemIcon(1, QIcon(self._flag_pixmap("us")))
    self.lang_combo.setItemIcon(2, QIcon(self._flag_pixmap("world")))
    self.lang_combo.setMinimumWidth(120)
    l2 = QLabel("Voz seleccionada")
    l2.setStyleSheet(f"color: {MUTED}; font-size: 12px;")
    self.voice_combo = QComboBox()
    self.voice_combo.setMinimumWidth(160)
    sel.addWidget(l1)
    sel.addWidget(self.lang_combo, 1)
    sel.addSpacing(8)
    sel.addWidget(l2)
    sel.addWidget(self.voice_combo, 1)
    cl.addLayout(sel)

    self.adv_button = QPushButton("＞  Opciones avanzadas")
    self.adv_button.setCursor(Qt.CursorShape.PointingHandCursor)
    self.adv_button.setStyleSheet(
        f"QPushButton {{ background: {CARD2}; color: {TEXT}; border: 1px solid"
        " {0}; border-radius: 10px; padding: 8px 14px; text-align: left; }}".format(BORDER)
    )
    cl.addWidget(self.adv_button)
    self.adv_widget = QWidget()
    al = QHBoxLayout(self.adv_widget)
    al.setContentsMargins(0, 4, 0, 4)
    al.addWidget(QLabel("Velocidad"))
    self.rate_slider = QSlider(Qt.Orientation.Horizontal)
    self.rate_slider.setRange(-10, 10)
    al.addWidget(self.rate_slider, 1)
    al.addSpacing(14)
    al.addWidget(QLabel("Volumen"))
    self.volume_slider = QSlider(Qt.Orientation.Horizontal)
    self.volume_slider.setRange(0, 100)
    self.volume_slider.setValue(100)
    al.addWidget(self.volume_slider, 1)
    self.adv_widget.setVisible(False)
    cl.addWidget(self.adv_widget)
    p0.addWidget(card)

    acts = QHBoxLayout()
    acts.setSpacing(12)
    self.speak_button = ActionButton("play", "Reproducir", BLUE, "#1d4ed8")
    self.stop_button = ActionButton("stop", "Detener", MAGENTA, PURPLE)
    self.export_button = ActionButton("download", "Exportar", TEAL, "#0d9488")
    self.copy_button = SquareButton("copy", "Copiar texto")
    self.open_button = SquareButton("folder", "Abrir archivo")
    self.theme_button = SquareButton("moon", "Tema")
    acts.addWidget(self.speak_button)
    acts.addWidget(self.stop_button)
    acts.addWidget(self.export_button)
    acts.addStretch()
    acts.addWidget(self.copy_button)
    acts.addWidget(self.open_button)
    acts.addWidget(self.theme_button)
    p0.addLayout(acts)
    self._add_neon(self.speak_button, BLUE)
    self._add_neon(self.stop_button, MAGENTA)
    self._add_neon(self.export_button, TEAL)

    player = QFrame()
    player.setFixedHeight(64)
    player.setStyleSheet(f"QFrame {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 14px; }}")
    yl = QHBoxLayout(player)
    yl.setContentsMargins(12, 0, 14, 0)
    yl.setSpacing(10)
    self.player_play = SquareButton("play", "Reproducir")
    self.player_play.setFixedSize(40, 40)
    self.time_cur = QLabel("0:00")
    self.time_cur.setStyleSheet(f"color: {MUTED};")
    self.progress_slider = QSlider(Qt.Orientation.Horizontal)
    self.progress_slider.setRange(0, 100)
    self.time_tot = QLabel("0:00")
    self.time_tot.setStyleSheet(f"color: {MUTED};")
    vol_icon = IconLabel("volume", 14, MUTED)
    self.vol_slider = QSlider(Qt.Orientation.Horizontal)
    self.vol_slider.setRange(0, 100)
    self.vol_slider.setValue(100)
    self.vol_slider.setFixedWidth(110)
    yl.addWidget(self.player_play)
    yl.addWidget(self.time_cur)
    yl.addWidget(self.progress_slider, 1)
    yl.addWidget(self.time_tot)
    yl.addWidget(vol_icon)
    yl.addWidget(self.vol_slider)
    p0.addWidget(player)
    self.pages.addWidget(page0)

    page1 = QWidget()
    h1 = QVBoxLayout(page1)
    h1.setContentsMargins(20, 16, 20, 16)
    ht = QLabel("Historial")
    ht.setStyleSheet(f"color: {TEXT}; font-size: 20px; font-weight: 700;")
    self.history_list = QListWidget()
    self.btn_clear_hist = QPushButton("Limpiar historial")
    self.btn_clear_hist.setStyleSheet(
        f"QPushButton {{ background: {CARD}; color: {TEXT}; border: 1px solid"
        f" {BORDER}; border-radius: 10px; padding: 8px 16px; }}"
    )
    h1.addWidget(ht)
    h1.addWidget(self.history_list, 1)
    h1.addWidget(self.btn_clear_hist, 0, Qt.AlignmentFlag.AlignLeft)
    self.pages.addWidget(page1)

    page2 = QWidget()
    v2 = QVBoxLayout(page2)
    v2.setContentsMargins(20, 16, 20, 16)
    vt = QLabel("Voces")
    vt.setStyleSheet(f"color: {TEXT}; font-size: 20px; font-weight: 700;")
    self.all_scroll = QScrollArea()
    self.all_scroll.setWidgetResizable(True)
    self.all_scroll.setFrameShape(QFrame.Shape.NoFrame)
    self.all_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    self.all_scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
    self.all_container = QWidget()
    self.all_container.setStyleSheet("background: transparent;")
    self.all_layout = QVBoxLayout(self.all_container)
    self.all_layout.setContentsMargins(0, 0, 6, 0)
    self.all_layout.setSpacing(8)
    self.all_scroll.setWidget(self.all_container)
    v2.addWidget(vt)
    v2.addWidget(self.all_scroll, 1)
    self.pages.addWidget(page2)

    page3 = QWidget()
    f3 = QVBoxLayout(page3)
    f3.setContentsMargins(20, 16, 20, 16)
    ft = QLabel("Favoritos")
    ft.setStyleSheet(f"color: {TEXT}; font-size: 20px; font-weight: 700;")
    self.fav_scroll = QScrollArea()
    self.fav_scroll.setWidgetResizable(True)
    self.fav_scroll.setFrameShape(QFrame.Shape.NoFrame)
    self.fav_scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
    self.fav_container = QWidget()
    self.fav_container.setStyleSheet("background: transparent;")
    self.fav_layout = QVBoxLayout(self.fav_container)
    self.fav_layout.setContentsMargins(0, 0, 6, 0)
    self.fav_layout.setSpacing(8)
    self.fav_scroll.setWidget(self.fav_container)
    f3.addWidget(ft)
    f3.addWidget(self.fav_scroll, 1)
    self.pages.addWidget(page3)

    page4 = QWidget()
    pr4 = QVBoxLayout(page4)
    pt4 = QLabel("Proyectos")
    pt4.setStyleSheet(f"color: {TEXT}; font-size: 20px; font-weight: 700;")
    ps4 = QLabel("Próximamente podrás guardar y organizar tus proyectos de voz.")
    ps4.setStyleSheet(f"color: {MUTED}; font-size: 13px;")
    pr4.addWidget(pt4)
    pr4.addWidget(ps4)
    pr4.addStretch()
    self.pages.addWidget(page4)

    page5 = QWidget()
    a5 = QVBoxLayout(page5)
    a5.setContentsMargins(20, 16, 20, 16)
    at5 = QLabel("Ajustes")
    at5.setStyleSheet(f"color: {TEXT}; font-size: 20px; font-weight: 700;")
    row5 = QHBoxLayout()
    row5.addWidget(QLabel("Límite de caracteres:"))
    self.limit_spin = QSpinBox()
    self.limit_spin.setRange(500, 20000)
    self.limit_spin.setSingleStep(500)
    self.limit_spin.setValue(int(self.settings.get("char_limit", 5000)))
    row5.addWidget(self.limit_spin)
    row5.addStretch()
    self.license_label = QLabel("")
    self.license_label.setStyleSheet(f"color: {MUTED};")
    a5.addWidget(at5)
    a5.addLayout(row5)
    a5.addWidget(self.license_label)
    a5.addStretch()
    self.pages.addWidget(page5)

    # ---------- PANEL DERECHO ----------
    self.right_panel = QFrame()
    self.right_panel.setStyleSheet(f"QFrame {{ background: {BG}; border-left: 1px solid {BORDER}; }}")
    self.right_panel.setMinimumWidth(240)
    self.right_panel.setMaximumWidth(340)
    rp = QVBoxLayout(self.right_panel)
    rp.setContentsMargins(14, 14, 14, 14)
    rp.setSpacing(10)
    rh = QHBoxLayout()
    rt = QLabel("Voces recomendadas")
    rt.setStyleSheet(f"color: {TEXT}; font-size: 14px; font-weight: 700;")
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
    self.filter_btn = SquareButton("filter", "Filtro")
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
    self.cards_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    self.cards_scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
    self.cards_container = QWidget()
    self.cards_container.setStyleSheet("background: transparent;")
    self.voice_cards_layout = QVBoxLayout(self.cards_container)
    self.voice_cards_layout.setContentsMargins(0, 0, 4, 0)
    self.voice_cards_layout.setSpacing(8)
    self.cards_scroll.setWidget(self.cards_container)
    rp.addWidget(self.cards_scroll, 1)
    root.addWidget(self.right_panel)

    self.player_timer = QTimer(self)
    self.player_timer.timeout.connect(self._tick_player)
    self._seconds = 0
    self._switch_page(0)


def _connect_signals(self):
    self.speak_button.clicked.connect(self.speak_text)
    self.player_play.clicked.connect(self.speak_text)
    self.stop_button.clicked.connect(self.stop_speech)
    self.export_button.clicked.connect(self._show_export_menu)
    self.copy_button.clicked.connect(self._copy_text)
    self.open_button.clicked.connect(self._open_document_dialog)
    self.theme_button.clicked.connect(self._toggle_theme_msg)
    self.btn_clear.clicked.connect(lambda: self.text_edit.clear())
    self.btn_paste.clicked.connect(lambda: self.text_edit.paste())
    self.btn_clear_hist.clicked.connect(self.clear_history)
    self.text_edit.textChanged.connect(self.update_counter)
    self.voice_combo.currentIndexChanged.connect(lambda _i: self._on_combo_voice())
    self.search_edit.textChanged.connect(lambda _t: self._rebuild_cards())
    self.rtab_all.clicked.connect(lambda: self._set_rtab("todas"))
    self.rtab_pro.clicked.connect(lambda: self._set_rtab("premium"))
    self.rtab_fav.clicked.connect(lambda: self._set_rtab("favoritas"))
    self.btn_ver_all.clicked.connect(lambda: self._switch_page(2))
    self.adv_button.clicked.connect(self._toggle_adv)
    self.history_list.itemClicked.connect(self._on_history_click)
    self.vol_slider.valueChanged.connect(lambda v: self.engine.set_volume(v))
    self.volume_slider.valueChanged.connect(lambda v: self.engine.set_volume(v))
    self.limit_spin.valueChanged.connect(
        lambda v: self.settings.__setitem__("char_limit", v))


def _switch_page(self, index):
    self.pages.setCurrentIndex(index)
    for i, (btn, _pg) in enumerate(self._nav):
        btn.set_active(i == index)
    self.right_panel.setVisible(index == 0)


def _toggle_sidebar(self):
    collapsed = self.sidebar.width() > 100
    self.sidebar.setFixedWidth(68 if collapsed else 232)
    for btn, _pg in self._nav:
        btn.set_collapsed(collapsed)
    self._logo_name.setVisible(not collapsed)
    self._logo_ver.setVisible(not collapsed)
    self._prem_card.setVisible(not collapsed)


def _set_rtab(self, tab):
    self._rtab = tab
    self.rtab_all.set_active(tab == "todas")
    self.rtab_pro.set_active(tab == "premium")
    self.rtab_fav.set_active(tab == "favoritas")
    self._rebuild_cards()


def _clear_layout(self, layout):
    while layout.count():
        item = layout.takeAt(0)
        w = item.widget() if item else None
        if w is not None:
            w.deleteLater()


def _favorites(self):
    return set(self.settings.get("favorites", []))


def _make_card(self, name, layout):
    premium = self._is_premium(name)
    favs = self._favorites()
    card = VoiceCard(self, name, premium,
                     name == self._selected_voice, name in favs)
    card.clicked.connect(lambda n=name: self._select_voice(n))
    card.fav_toggled.connect(lambda n=name: self._toggle_fav(n))
    layout.addWidget(card)


def _rebuild_cards(self):
    self._clear_layout(self.voice_cards_layout)
    q = self.search_edit.text().strip().lower()
    for name in getattr(self, "_voices", []):
        premium = self._is_premium(name)
        if self._rtab == "premium" and not premium:
            continue
        if self._rtab == "favoritas" and name not in self._favorites():
            continue
        if q and q not in name.lower():
            continue
        self._make_card(name, self.voice_cards_layout)
    self.voice_cards_layout.addStretch()


def _rebuild_all_page(self):
    self._clear_layout(self.all_layout)
    for name in getattr(self, "_voices", []):
        self._make_card(name, self.all_layout)
    self.all_layout.addStretch()


def _rebuild_fav_page(self):
    self._clear_layout(self.fav_layout)
    for name in getattr(self, "_voices", []):
        if name in self._favorites():
            self._make_card(name, self.fav_layout)
    self.fav_layout.addStretch()


def _load_voices(self):
    try:
        self.engine.refresh_voices()
        voices = self.engine.get_available_voices()
        voices.sort(key=lambda n: (not self._is_premium(n), n.lower()))
        self._voices = voices
        self.voice_combo.blockSignals(True)
        self.voice_combo.clear()
        for v in voices:
            self.voice_combo.addItem(self._display_voice_name(v))
            idx = self.voice_combo.count() - 1
            self.voice_combo.setItemData(idx, v, Qt.ItemDataRole.UserRole)
            self.voice_combo.setItemIcon(idx, QIcon(self._avatar_pixmap(v)))
        last = self.settings.get("last_voice", "")
        if last in voices:
            self._select_voice(last)
        elif voices:
            pref = next((v for v in voices if "SeraphinaMultilingual" in v),
                        voices[0])
            self._select_voice(pref)
        self.voice_combo.blockSignals(False)
        self.stat_voices.value_label.setText(f"{len(voices)}+")
        self._rebuild_cards()
        self._rebuild_all_page()
        self._rebuild_fav_page()
    except Exception as exc:
        self.logger.exception("Error cargando voces.")
        QMessageBox.critical(self, "Error",
                             f"No se pudieron cargar las voces: {exc}")


def _on_combo_voice(self):
    voice = self.voice_combo.currentData(Qt.ItemDataRole.UserRole)
    if voice:
        self._select_voice(voice)


def _select_voice(self, name):
    self._selected_voice = name
    for i in range(self.voice_combo.count()):
        if self.voice_combo.itemData(i, Qt.ItemDataRole.UserRole) == name:
            self.voice_combo.blockSignals(True)
            self.voice_combo.setCurrentIndex(i)
            self.voice_combo.blockSignals(False)
            break
    try:
        self.engine.select_voice(name)
    except Exception:
        pass
    self._rebuild_cards()
    self._rebuild_all_page()
    self._rebuild_fav_page()


def _toggle_fav(self, name):
    favs = self._favorites()
    if name in favs:
        favs.discard(name)
    else:
        favs.add(name)
    self.settings["favorites"] = sorted(favs)
    self._rebuild_cards()
    self._rebuild_all_page()
    self._rebuild_fav_page()


def update_counter(self):
    limit = int(self.settings.get("char_limit", 5000))
    total = len(self.text_edit.toPlainText())
    self.counter_label.setText(f"{total} / {limit}")


def _copy_text(self):
    QGuiApplication_clipboard = __import__(
        "PySide6.QtGui", fromlist=["QGuiApplication"]).QGuiApplication
    QGuiApplication_clipboard.clipboard().setText(self.text_edit.toPlainText())
    self.statusBar().showMessage("Texto copiado al portapapeles.")


def _open_document_dialog(self):
    path, _ = QFileDialog.getOpenFileName(
        self, "Abrir documento", "",
        "Archivos (*.txt *.md *.log *.csv *.pdf *.docx *.doc *.rtf *.html)")
    if not path:
        return
    try:
        content = file_reader.extract_text(Path(path))
        self.text_edit.setPlainText(content)
        self._add_to_history(content, file_path=path)
        self.statusBar().showMessage(f"Documento cargado: {Path(path).name}")
    except Exception as exc:
        QMessageBox.warning(self, "WillpoVoice",
                            f"No se pudo leer el archivo: {exc}")


def _toggle_adv(self):
    show = not self.adv_widget.isVisible()
    self.adv_widget.setVisible(show)
    self.adv_button.setText(
        "＞  Opciones avanzadas" if not show else "＜  Opciones avanzadas")


def _toggle_theme_msg(self):
    self.statusBar().showMessage("Tema claro: próximamente.")


def _fmt_time(self, s):
    m = int(s // 60)
    ss = int(s % 60)
    return f"{m}:{ss:02d}"


def _tick_player(self):
    self._seconds += 0.5
    self.time_cur.setText(self._fmt_time(self._seconds))
    self.progress_slider.setValue(int(self._seconds * 4) % 100)
    try:
        state = self.engine.adapter.sapi.Status.RunningState
    except Exception:
        state = 1
    if state != 2 and self._seconds > 2:
        self.player_timer.stop()
        self._seconds = 0
        self.time_cur.setText("0:00")
        self.progress_slider.setValue(0)


def speak_text(self):
    try:
        text = self.text_edit.toPlainText().strip()
        if not text:
            self.statusBar().showMessage("Escribe un texto antes de reproducir.")
            return
        voice = self.voice_combo.currentData(Qt.ItemDataRole.UserRole)
        if voice:
            self.engine.select_voice(voice)
        self.engine.set_rate(self.rate_slider.value())
        self.engine.set_volume(self.volume_slider.value())
        self.engine.speak_async(text)
        self._add_to_history(text)
        self.settings["conv_today"] = int(self.settings.get("conv_today", 0)) + 1
        self.stat_conv.value_label.setText(str(self.settings["conv_today"]))
        self._seconds = 0
        self.player_timer.start(500)
        self.statusBar().showMessage("Reproduciendo...")
    except Exception as exc:
        QMessageBox.warning(self, "Error", f"No se pudo reproducir: {exc}")


def stop_speech(self):
    try:
        self.engine.stop()
        self.player_timer.stop()
        self._seconds = 0
        self.time_cur.setText("0:00")
        self.progress_slider.setValue(0)
        self.statusBar().showMessage("Reproducción detenida.")
    except Exception as exc:
        QMessageBox.warning(self, "Error", f"No se pudo detener: {exc}")


def _show_export_menu(self):
    menu = QMenu(self)
    wav = menu.addAction("Audio WAV  (.wav, sin compresion)")
    mp3 = menu.addAction("Audio MP3  (.mp3, comprimido)")
    action = menu.exec(self.export_button.mapToGlobal(
        QPoint(0, self.export_button.height())))
    if action == wav:
        self.export_wav()
    elif action == mp3:
        self.export_mp3()


def export_wav(self):
    text = self.text_edit.toPlainText().strip()
    if not text:
        self.statusBar().showMessage("Escribe un texto antes de exportar.")
        return
    path, _ = QFileDialog.getSaveFileName(self, "Guardar audio WAV",
                                          "willpovoice_audio.wav",
                                          "Archivos WAV (*.wav)")
    if not path:
        return
    self._run_export(text, path, False)


def export_mp3(self):
    import tempfile
    text = self.text_edit.toPlainText().strip()
    if not text:
        self.statusBar().showMessage("Escribe un texto antes de exportar.")
        return
    path, _ = QFileDialog.getSaveFileName(self, "Guardar audio MP3",
                                          "willpovoice_audio.mp3",
                                          "Archivos MP3 (*.mp3)")
    if not path:
        return
    if not path.lower().endswith(".mp3"):
        path += ".mp3"
    self._mp3_final_path = path
    self._run_export(text, tempfile.mktemp(suffix=".wav"), True)


def _run_export(self, text, path, is_mp3):
    voice = self.voice_combo.currentData(Qt.ItemDataRole.UserRole)
    self.statusBar().showMessage("Exportando audio...")
    self.export_worker = ExportWorker(
        exporter=self.exporter, text=text, path=path, voice=voice,
        rate=self.rate_slider.value(), volume=self.volume_slider.value())
    self.export_worker.export_ok.connect(self.on_export_ok)
    self.export_worker.export_error.connect(self.on_export_error)
    self.export_worker.start()


def on_export_ok(self, path):
    final_path = path
    mp3_target = getattr(self, "_mp3_final_path", None)
    if mp3_target:
        self._mp3_final_path = None
        try:
            from core.mp3_encoder import wav_to_mp3
            wav_to_mp3(path, mp3_target)
            Path(path).unlink(missing_ok=True)
            final_path = mp3_target
        except Exception as exc:
            QMessageBox.warning(self, "Error",
                                f"No se pudo convertir a MP3: {exc}")
            return
    self.statusBar().showMessage(f"Audio guardado en: {final_path}")
    QMessageBox.information(self, "Exportación exitosa",
                            f"El audio se guardó en: {final_path}")


def on_export_error(self, message):
    QMessageBox.warning(self, "Error",
                        f"No se pudo exportar el audio: {message}")


def _load_history(self):
    self.history_list.clear()
    self._history_full = []
    for it in self.settings.get("history", []):
        entry = it if isinstance(it, dict) else {
            "content": it, "label": "Texto manual"}
        self._history_full.append(entry)
        self.history_list.addItem(entry.get("label", "Sin titulo"))


def _on_history_click(self, item):
    idx = self.history_list.row(item)
    if 0 <= idx < len(self._history_full):
        self.text_edit.setPlainText(
            self._history_full[idx].get("content", ""))
        self._switch_page(0)


def clear_history(self):
    self.settings["history"] = []
    self._load_history()
    self.statusBar().showMessage("Historial limpiado.")


def _add_to_history(self, text, file_path=None):
    text = (text or "").strip()
    if not text:
        return
    items = self.settings.get("history", [])
    label = "Texto manual"
    if file_path:
        label = Path(file_path).name
    entry = {"content": text, "label": label}
    items = [it if isinstance(it, dict) else {"content": it, "label": "Texto manual"}
             for it in items]
    items = [it for it in items if it.get("content") != text]
    items.insert(0, entry)
    self.settings["history"] = items[: self.MAX_HISTORY]
    self._load_history()


def open_support(self):
    QDesktopServices.openUrl(QUrl("https://wa.me/51923073560"))
    self.statusBar().showMessage("Abriendo WhatsApp de soporte...")


def show_help(self):
    QMessageBox.information(
        self, "Ayuda de WillpoVoice",
        "1. Elige una voz en el panel derecho.\\n"
        "2. Escribe o pega tu texto.\\n"
        "3. Pulsa Reproducir para escucharlo.\\n"
        "4. Usa Exportar para guardar WAV/MP3.\\n"
        "5. Marca voces con el corazón para favoritas.")


def _check_license(self):
    state, days_left = license_manager.check_status()
    if state == "licensed":
        self.license_label.setText("Version licenciada.")
        self.statusBar().showMessage("Version licenciada.")
        return True
    dialog = LicenseDialog(self, license_manager.get_machine_id(),
                           days_left if state == "trial" else -1)
    dialog.exec()
    if dialog.activated_key:
        data = license_manager.load_data()
        data["license_key"] = dialog.activated_key
        license_manager.save_data(data)
        self.license_label.setText("Version licenciada.")
        return True
    return dialog.trial_accepted


def showEvent(self, event):
    super().showEvent(event)
    if not getattr(self, "_license_checked", False):
        self._license_checked = True
        if not self._check_license():
            self.close()


def closeEvent(self, event):
    try:
        self.settings["last_voice"] = self._current_voice()
        save_settings(self.settings)
        self.engine.stop()
    except Exception:
        self.logger.exception("Error al cerrar.")
    event.accept()


def _current_voice(self):
    data = self.voice_combo.currentData(Qt.ItemDataRole.UserRole)
    return data or self.voice_combo.currentText()


MainWindow._build_ui = _build_ui
MainWindow._connect_signals = _connect_signals
MainWindow._switch_page = _switch_page
MainWindow._toggle_sidebar = _toggle_sidebar
MainWindow._set_rtab = _set_rtab
MainWindow._clear_layout = _clear_layout
MainWindow._favorites = _favorites
MainWindow._make_card = _make_card
MainWindow._rebuild_cards = _rebuild_cards
MainWindow._rebuild_all_page = _rebuild_all_page
MainWindow._rebuild_fav_page = _rebuild_fav_page
MainWindow._load_voices = _load_voices
MainWindow._on_combo_voice = _on_combo_voice
MainWindow._select_voice = _select_voice
MainWindow._toggle_fav = _toggle_fav
MainWindow.update_counter = update_counter
MainWindow._copy_text = _copy_text
MainWindow._open_document_dialog = _open_document_dialog
MainWindow._toggle_adv = _toggle_adv
MainWindow._toggle_theme_msg = _toggle_theme_msg
MainWindow._fmt_time = _fmt_time
MainWindow._tick_player = _tick_player
MainWindow.speak_text = speak_text
MainWindow.stop_speech = stop_speech
MainWindow._show_export_menu = _show_export_menu
MainWindow.export_wav = export_wav
MainWindow.export_mp3 = export_mp3
MainWindow._run_export = _run_export
MainWindow.on_export_ok = on_export_ok
MainWindow.on_export_error = on_export_error
MainWindow._load_history = _load_history
MainWindow._on_history_click = _on_history_click
MainWindow.clear_history = clear_history
MainWindow._add_to_history = _add_to_history
MainWindow.open_support = open_support
MainWindow.show_help = show_help
MainWindow._check_license = _check_license
MainWindow.showEvent = showEvent
MainWindow.closeEvent = closeEvent
MainWindow._current_voice = _current_voice
'''

# Las funciones de Parte B se definieron con sangria 0 y se asignan
# a la clase al final; corregimos la sangria del bloque _build_ui
# que debe ser metodo (se asigna via MainWindow._build_ui).
t = t + parteB
p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("Parte B escrita - SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
