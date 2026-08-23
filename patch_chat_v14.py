from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")
log = []

# ============ 1) Saludo + chips de arranque ============
anchor = "    self._set_chat_locked(not _has_key)"
if "_chat_chips_wrap" not in t and anchor in t:
    i = t.find(anchor) + len(anchor)
    block = '''
    self._add_chat_bubble(
        "\\u00a1Hola! \\u00bfEn qu\\u00e9 puedo ayudarte hoy?", is_user=False)
    chips = QHBoxLayout()
    chips.setSpacing(10)
    chips.setContentsMargins(52, 4, 0, 0)
    chip_style = (
        "QPushButton { background: transparent; color: #cfe3ff;"
        " border: 1px solid #2f4c79; border-radius: 16px;"
        " padding: 8px 14px; font-size: 11px; font-weight: 600; }"
        " QPushButton:hover { background: rgba(88,166,255,25); }")
    for glyph, label in [("doc", "Crear un guion / historia"),
                         ("search", "Analizar guion y mejorar"),
                         ("bolt", "Crear anuncios publicitarios")]:
        ch = QPushButton("  " + label)
        ch.setIcon(QIcon(make_icon(glyph, "#7cb7ff", 13)))
        ch.setCursor(Qt.CursorShape.PointingHandCursor)
        ch.setStyleSheet(chip_style)
        ch.clicked.connect(
            lambda _=False, lb=label: self._on_chat_chip(lb))
        chips.addWidget(ch)
    chips.addStretch(1)
    self._chat_chips_wrap = QWidget()
    self._chat_chips_wrap.setLayout(chips)
    self._chat_layout.insertWidget(
        self._chat_layout.count() - 1, self._chat_chips_wrap)'''
    t = t[:i] + block + t[i:]
    log.append("saludo + chips")

# ============ 2) Metodo _on_chat_chip ============
anchor_att = "MainWindow._copy_chat_text = _copy_chat_text"
if "def _on_chat_chip" not in t and anchor_att in t:
    i = t.find(anchor_att)
    fn = '''def _on_chat_chip(self, label):
    respuestas = {
        "Crear un guion / historia":
            "\\u00a1Perfecto! \\u00bfDe qu\\u00e9 tratar\\u00e1 tu historia o guion? "
            "Dame los detalles exactos y lo crear\\u00e9 \\u2728",
        "Analizar guion y mejorar":
            "\\u00a1Perfecto! Comp\\u00e1rteme tu guion para mejorarlo.",
        "Crear anuncios publicitarios":
            "\\u00a1Perfecto! Vamos a crear tu anuncio publicitario. "
            "Necesitar\\u00e9 lo siguiente:\\n"
            "- Nombre de tu negocio:\\n"
            "- De qu\\u00e9 trata tu negocio:\\n"
            "- Qu\\u00e9 producto vas a ofrecer:\\n"
            "- Precio",
    }
    self._add_chat_bubble(label, is_user=True)
    try:
        self._chat_chips_wrap.setParent(None)
        self._chat_chips_wrap.deleteLater()
    except Exception:
        pass
    self._add_chat_bubble(respuestas.get(label, ""), is_user=False)


MainWindow._on_chat_chip = _on_chat_chip
'''
    t = t[:i] + fn + t[i:]
    log.append("_on_chat_chip")

mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
assert "MainWindow._on_chat_chip = _on_chat_chip" in t
print("OK", log)
