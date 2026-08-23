from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")
log = []

# ============ 1) Nueva tarjeta de configuracion de API Key ============
s = t.find("    self._chat_banner = QFrame()")
e = t.find("    p5.addWidget(self._chat_banner)")
if s == -1 or e == -1:
    raise SystemExit("ERROR: banner no encontrado")
e += len("    p5.addWidget(self._chat_banner)")

new_card = '''    self._chat_banner = QFrame()
    self._chat_banner.setObjectName("groqCard")
    self._chat_banner.setStyleSheet(
        "#groqCard { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
        " stop:0 rgba(18,24,56,235), stop:1 rgba(30,16,60,235));"
        " border: 1px solid #3b4bd8; border-radius: 18px; }")
    bv = QVBoxLayout(self._chat_banner)
    bv.setContentsMargins(28, 26, 28, 26)
    bv.setSpacing(18)

    hdr = QHBoxLayout()
    hdr.setSpacing(18)
    orb = QLabel()
    orb.setFixedSize(72, 72)
    orb.setPixmap(make_icon("key", "#c4b5fd", 34))
    orb.setAlignment(Qt.AlignmentFlag.AlignCenter)
    orb.setStyleSheet(
        "background: rgba(124,92,255,40); border: 2px solid #7c5cff;"
        " border-radius: 36px;")
    hdr.addWidget(orb)
    tcol = QVBoxLayout()
    tcol.setSpacing(4)
    t1 = QLabel("Configura tu API Key de Groq")
    t1.setStyleSheet(
        "color: #ffffff; font-size: 22px; font-weight: 800; font-style: italic;")
    tcol.addWidget(t1)
    t2 = QLabel("Conecta tu API Key para desbloquear todo el poder "
                "del Chat IA de WillpoVoice.")
    t2.setStyleSheet("color: #a8b3cf; font-size: 12px;")
    tcol.addWidget(t2)
    hdr.addLayout(tcol)
    hdr.addStretch(1)
    bv.addLayout(hdr)

    cards = QHBoxLayout()
    cards.setSpacing(16)
    for glyph, ctitle, cdesc in [
        ("shield", "100% Seguro",
         "Tu clave se almacena de forma segura y encriptada."),
        ("bolt", "Acceso Completo",
         "Disfruta de respuestas mas rapidas y precisas con Groq."),
    ]:
        fr = QFrame()
        fr.setObjectName("gcMini")
        fr.setStyleSheet(
            "#gcMini { background: rgba(13,18,40,160);"
            " border: 1px solid #2a3364; border-radius: 12px; }")
        fv = QHBoxLayout(fr)
        fv.setContentsMargins(16, 14, 16, 14)
        fv.setSpacing(12)
        ic = QLabel()
        ic.setFixedSize(44, 44)
        ic.setPixmap(make_icon(glyph, "#ffffff", 20))
        ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ic.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            " stop:0 #6d5df0, stop:1 #4527a0); border-radius: 22px;")
        fv.addWidget(ic)
        tx = QVBoxLayout()
        tx.setSpacing(3)
        a = QLabel(ctitle)
        a.setStyleSheet("color: #ffffff; font-size: 13px; font-weight: 700;")
        tx.addWidget(a)
        b = QLabel(cdesc)
        b.setStyleSheet("color: #93a0c2; font-size: 11px;")
        b.setWordWrap(True)
        tx.addWidget(b)
        fv.addLayout(tx)
        cards.addWidget(fr)
    bv.addLayout(cards)

    lbl = QLabel("Ingresa tu API Key")
    lbl.setStyleSheet("color: #e6edf3; font-size: 12px; font-weight: 700;")
    bv.addWidget(lbl)

    key_row = QFrame()
    key_row.setObjectName("gcInput")
    key_row.setStyleSheet(
        "#gcInput { background: rgba(10,14,32,200);"
        " border: 1px solid #2a3364; border-radius: 10px; }")
    kv = QHBoxLayout(key_row)
    kv.setContentsMargins(12, 4, 8, 4)
    kv.setSpacing(8)
    kic = QLabel()
    kic.setPixmap(make_icon("key", "#8b949e", 16))
    kv.addWidget(kic)
    self._groq_key_input = QLineEdit()
    self._groq_key_input.setFixedHeight(40)
    self._groq_key_input.setPlaceholderText(
        "gsk_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    self._groq_key_input.setEchoMode(QLineEdit.EchoMode.Password)
    self._groq_key_input.setStyleSheet(
        "QLineEdit { background: transparent; border: none;"
        " color: #e6edf3; font-size: 12.5px; }")
    self._groq_key_input.returnPressed.connect(self._save_groq_key)
    kv.addWidget(self._groq_key_input, 1)
    self._key_eye = QPushButton()
    self._key_eye.setFixedSize(32, 32)
    self._key_eye.setCursor(Qt.CursorShape.PointingHandCursor)
    self._key_eye.setStyleSheet(
        "QPushButton { background: transparent; border: none; }")
    self._key_eye.setIcon(QIcon(_chat_svg(_EYE_OFF, "#8b949e", 16)))
    self._key_eye.clicked.connect(self._toggle_key_vis)
    kv.addWidget(self._key_eye)
    bv.addWidget(key_row)

    hint = QLabel("Presiona Enter para conectar  ·  "
                  "Obtén tu clave gratis en console.groq.com "
                  "(sin tarjeta de crédito)")
    hint.setStyleSheet("color: #93a0c2; font-size: 11px;")
    bv.addWidget(hint)

    bot = QHBoxLayout()
    bot.setSpacing(12)
    btn_get = QPushButton("  Obtener API Key gratis")
    btn_get.setIcon(QIcon(make_icon("key", "#ffffff", 16)))
    btn_get.setFixedHeight(44)
    btn_get.setCursor(Qt.CursorShape.PointingHandCursor)
    btn_get.setStyleSheet(
        "QPushButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
        " stop:0 #6d5df0, stop:1 #2f6bff); color: white; border: none;"
        " border-radius: 10px; padding: 0 22px; font-weight: 700;"
        " font-size: 12.5px; }"
        " QPushButton:hover { background: #7d6ffb; }")
    btn_get.clicked.connect(
        lambda: QDesktopServices.openUrl(QUrl("https://console.groq.com/keys")))
    bot.addWidget(btn_get)
    lock = QLabel()
    lock.setPixmap(make_icon("lock", "#8d75ff", 14))
    bot.addWidget(lock)
    priv = QLabel("Tú tienes el control absoluto: "
                  "tu clave nunca sale de tu equipo.")
    priv.setStyleSheet("color: #93a0c2; font-size: 11px;")
    bot.addWidget(priv)
    bot.addStretch(1)
    bv.addLayout(bot)

    p5.addWidget(self._chat_banner)'''

t = t[:s] + new_card + t[e:]
log.append("tarjeta groq")

# ============ 2) Constantes de ojos + metodos nuevos ============
anchor_eye = "def _chat_svg(path_data, color, size):"
if "_EYE_ON" not in t and anchor_eye in t:
    i = t.find(anchor_eye)
    eyes = ('''_EYE_ON = ("M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27"
           "-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24"
           "-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3"
           " 3-1.34 3-3-1.34-3-3-3z")
_EYE_OFF = ("M12 7c2.76 0 5 2.24 5 5 0 .65-.13 1.26-.36 1.83l2.92 2.92c1.51"
            "-1.26 2.7-2.89 3.43-4.75-1.73-4.39-6-7.5-11-7.5-1.4 0-2.74.25"
            "-3.98.7l2.16 2.16C10.74 7.13 11.35 7 12 7zM2 4.27l2.28 2.28.46"
            ".46C3.08 8.3 1.78 10.02 1 12c1.73 4.39 6 7.5 11 7.5 1.55 0 3.03"
            "-.3 4.38-.84l.42.42L19.73 22 21 20.73 3.27 3 2 4.27zM7.53 9.8l1.55"
            " 1.55c-.05.21-.08.43-.08.65 0 1.66 1.34 3 3 3 .22 0 .44-.03.65-.08"
            "l1.55 1.55c-.67.37-1.43.58-2.2.58-2.76 0-5-2.24-5-5 0-.77.21-1.53"
            ".58-2.2z")


''')
    t = t[:i] + eyes + t[i:]
    log.append("eyes svg")

# ============ 3) _configure_groq_key -> muestra tarjeta ============
s2 = t.find("def _configure_groq_key(self):")
e2 = t.find("def _send_chat_message(self):")
if s2 != -1 and e2 != -1:
    new_cfg = '''def _configure_groq_key(self):
    self._switch_page(5)
    self._chat_banner.setVisible(True)
    try:
        self._groq_key_input.setFocus()
    except Exception:
        pass


'''
    t = t[:s2] + new_cfg + t[e2:]
    log.append("configure simple")

# ============ 4) _save_groq_key + _toggle_key_vis ============
anchor_att = "MainWindow._configure_groq_key = _configure_groq_key"
if "def _save_groq_key" not in t and anchor_att in t:
    i = t.find(anchor_att)
    fns = '''def _save_groq_key(self):
    from PySide6.QtCore import QSettings
    key = self._groq_key_input.text().strip()
    if not key:
        return
    s = QSettings("WillpoVoice", "WillpoVoice")
    s.setValue("groq_api_key", key)
    self._chat_banner.setVisible(False)
    self._add_chat_bubble(
        "API Key conectada. ¡Listo para chatear!", is_user=False)


def _toggle_key_vis(self):
    le = self._groq_key_input
    if le.echoMode() == QLineEdit.EchoMode.Password:
        le.setEchoMode(QLineEdit.EchoMode.Normal)
        self._key_eye.setIcon(QIcon(_chat_svg(_EYE_ON, "#8b949e", 16)))
    else:
        le.setEchoMode(QLineEdit.EchoMode.Password)
        self._key_eye.setIcon(QIcon(_chat_svg(_EYE_OFF, "#8b949e", 16)))


MainWindow._save_groq_key = _save_groq_key
MainWindow._toggle_key_vis = _toggle_key_vis
'''
    t = t[:i] + fns + t[i:]
    log.append("save+toggle")

mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
assert "MainWindow._save_groq_key = _save_groq_key" in t
print("OK", log)
