from pathlib import Path
import ast

# ============ 1) Nuevo SYSTEM_PROMPT en brain.py ============
bp = Path("core/brain.py")
b = bp.read_text(encoding="utf-8-sig")
i = b.find('SYSTEM_PROMPT = """')
j = b.find('"""', i + 20)
if i != -1 and j != -1:
    new_prompt = '''SYSTEM_PROMPT = """Eres Willpo, el asistente de inteligencia artificial de WillpoVoice, una aplicacion de texto a voz con voces neuronales premium.
Hablas siempre en espanol neutro latinoamericano, con tono amigable, calido y empatico.
Tus respuestas seran leidas en voz alta por un motor TTS, asi que:
- Maximo 3 o 4 frases, cortas y claras.
- Nada de markdown, emojis, listas, asteriscos ni caracteres especiales.
Si te preguntan quien eres o que modelo eres: responde que eres Willpo, el asistente de WillpoVoice, impulsado por inteligencia artificial de ultima generacion. Nunca digas que eres ChatGPT, GPT, Claude, Gemini ni Llama.
Puedes explicar temas complejos pero siempre en lenguaje simple; si piden codigo o textos muy largos, resume la idea clave y ofrece ampliarla por partes para no cansar al oyente."""'''
    b = b[:i] + new_prompt + b[j + 3:]
    bp.write_text(b, encoding="utf-8", newline="\n")
    print("SYSTEM_PROMPT actualizado: identidad Willpo")

# ============ 2) Botones Copiar / Agregar en burbujas IA ============
mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")
log = []

s2 = t.find("def _add_chat_bubble(self, text, is_user, temp=False):")
e2 = t.find("def _on_chat_response(self, response, temp_bubble):")
if s2 == -1 or e2 == -1:
    raise SystemExit("ERROR: _add_chat_bubble no encontrado")

new_bubble_fn = '''def _add_chat_bubble(self, text, is_user, temp=False):
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
        col = QVBoxLayout()
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(4)
        col.addWidget(bub)
        if not temp:
            acts = QHBoxLayout()
            acts.setSpacing(8)
            acts.setContentsMargins(6, 0, 0, 0)
            ghost = ("QPushButton { background: transparent;"
                     " color: #8b949e; border: none; font-size: 10px;"
                     " font-weight: 600; padding: 2px 6px;"
                     " border-radius: 6px; }"
                     " QPushButton:hover { color: #e6edf3;"
                     " background: rgba(139,148,158,30); }")
            b_copy = QPushButton("Copiar")
            b_copy.setIcon(QIcon(make_icon("copy", "#8b949e", 12)))
            b_copy.setStyleSheet(ghost)
            b_copy.setCursor(Qt.CursorShape.PointingHandCursor)
            b_copy.clicked.connect(
                lambda _=False, txt=text: self._copy_chat_text(txt))
            acts.addWidget(b_copy)
            b_add = QPushButton("Agregar a conversi\\u00f3n")
            b_add.setIcon(QIcon(make_icon("paste", "#8b949e", 12)))
            b_add.setStyleSheet(ghost)
            b_add.setCursor(Qt.CursorShape.PointingHandCursor)
            b_add.clicked.connect(
                lambda _=False, txt=text: self._add_to_conversion(txt))
            acts.addWidget(b_add)
            acts.addStretch(1)
            col.addLayout(acts)
        row.addWidget(col)
        row.addStretch(1)
    wrap = QWidget()
    wrap.setLayout(row)
    wrap.setProperty("temp", temp)
    self._chat_layout.insertWidget(self._chat_layout.count() - 1, wrap)
    self._chat_scroll.verticalScrollBar().setValue(
        self._chat_scroll.verticalScrollBar().maximum())
    return wrap


'''
t = t[:s2] + new_bubble_fn + t[e2:]
log.append("botones en burbujas")

# ============ 3) Metodos de accion ============
anchor_att = "MainWindow._set_chat_locked = _set_chat_locked"
if "def _copy_chat_text" not in t and anchor_att in t:
    i = t.find(anchor_att)
    fns = '''def _copy_chat_text(self, txt):
    try:
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(txt)
        self.statusBar().showMessage(
            "Respuesta copiada al portapapeles", 3000)
    except Exception:
        pass


def _add_to_conversion(self, txt):
    target = None
    for name in ("text_edit", "text_input", "input_text",
                 "text_area", "editor", "txt_input"):
        w = getattr(self, name, None)
        if w is not None and (hasattr(w, "setPlainText")
                              or hasattr(w, "setText")):
            target = w
            break
    if target is None:
        from PySide6.QtWidgets import QTextEdit, QPlainTextEdit
        for w in self.findChildren((QTextEdit, QPlainTextEdit)):
            if w is not getattr(self, "_chat_input", None):
                target = w
                break
    if target is not None:
        try:
            if hasattr(target, "setPlainText"):
                cur = target.toPlainText()
                target.setPlainText(
                    (cur.rstrip() + "\\n\\n" + txt) if cur.strip() else txt)
            else:
                cur = target.text()
                target.setText((cur + " " + txt) if cur.strip() else txt)
            self._switch_page(0)
            self.statusBar().showMessage(
                "Texto agregado a la conversi\\u00f3n", 3000)
        except Exception:
            pass


MainWindow._copy_chat_text = _copy_chat_text
MainWindow._add_to_conversion = _add_to_conversion
'''
    t = t[:i] + fns + t[i:]
    log.append("metodos accion")

mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
assert "MainWindow._copy_chat_text = _copy_chat_text" in t
print("OK", log)
