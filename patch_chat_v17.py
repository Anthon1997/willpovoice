from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")
log = []

# ============ 1) Reemplazar chips inline por metodo ============
s = t.find("    chips = QHBoxLayout()")
e = t.find("self._chat_chips_wrap)", s)
if s != -1 and e != -1:
    e += len("self._chat_chips_wrap)")
    t = t[:s] + "    self._show_chat_chips()" + t[e:]
    log.append("chips -> metodo")

# ============ 2) Metodos _show/_hide_chat_chips ============
anchor_att = "MainWindow._on_chat_chip = _on_chat_chip"
if "def _show_chat_chips" not in t and anchor_att in t:
    i = t.find(anchor_att)
    fns = '''def _show_chat_chips(self):
    try:
        old = getattr(self, "_chat_chips_wrap", None)
        if old is not None:
            old.setParent(None)
            old.deleteLater()
    except Exception:
        pass
    chips = QHBoxLayout()
    chips.setSpacing(10)
    chips.setContentsMargins(52, 4, 8, 0)
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
    x = QPushButton()
    x.setFixedSize(26, 26)
    x.setIcon(QIcon(make_icon("x", "#8b949e", 12)))
    x.setCursor(Qt.CursorShape.PointingHandCursor)
    x.setToolTip("Cerrar sugerencias")
    x.setStyleSheet(
        "QPushButton { background: transparent; border: none;"
        " border-radius: 13px; }"
        " QPushButton:hover { background: rgba(139,148,158,40); }")
    x.clicked.connect(self._hide_chat_chips)
    chips.addWidget(x)
    wrap = QWidget()
    wrap.setLayout(chips)
    self._chat_chips_wrap = wrap
    self._chat_layout.insertWidget(
        self._chat_layout.count() - 1, wrap)
    self._chat_scroll.verticalScrollBar().setValue(
        self._chat_scroll.verticalScrollBar().maximum())


def _hide_chat_chips(self):
    try:
        w = getattr(self, "_chat_chips_wrap", None)
        if w is not None:
            w.setParent(None)
            w.deleteLater()
        self._chat_chips_wrap = None
    except Exception:
        pass


MainWindow._show_chat_chips = _show_chat_chips
MainWindow._hide_chat_chips = _hide_chat_chips
'''
    t = t[:i] + fns + t[i:]
    log.append("metodos chips")

# ============ 3) Chip click: ya no elimina, reaparece tras respuesta ============
old_remove = '''    try:
        self._chat_chips_wrap.setParent(None)
        self._chat_chips_wrap.deleteLater()
    except Exception:
        pass
    self._add_chat_bubble(resp, is_user=False)'''
new_remove = '''    self._add_chat_bubble(resp, is_user=False)
    self._show_chat_chips()'''
if old_remove in t:
    t = t.replace(old_remove, new_remove, 1)
    log.append("chips tras chip")

# ============ 4) Reaparecen tras cada respuesta IA ============
old_end = '''        try:
            ad.speak(response)
        except Exception as exc:
            print(f"TTS fallo: {exc}")'''
new_end = old_end + "\n    self._show_chat_chips()"
if old_end in t and "self._show_chat_chips()\n\n\ndef _copy_chat_text" not in t:
    t = t.replace(old_end, new_end, 1)
    log.append("chips tras respuesta")

mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
assert "MainWindow._show_chat_chips = _show_chat_chips" in t
print("OK", log)
