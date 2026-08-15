from pathlib import Path
import re, ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# ---- 1. RECOPILACION ----
for m in ("class VoiceCard", "def _make_card", "MAX_HISTORY",
          "def stop_speech"):
    print(f"--- {m!r} indice:", t.find(m))

# ---- 2. Signal de preview en MainWindow ----
old_max = """class MainWindow(QMainWindow):
    MAX_HISTORY = 10"""
new_max = """class MainWindow(QMainWindow):
    MAX_HISTORY = 10
    preview_changed = Signal(str, bool)"""
if old_max in t:
    t = t.replace(old_max, new_max, 1)
    print("2. Signal preview_changed.")

# ---- 3. PreviewPhoto + VoiceCard con preview organico ----
new_card = '''class PreviewPhoto(QLabel):
    play_clicked = Signal()
    hover_changed = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def enterEvent(self, event):
        self.hover_changed.emit(True)

    def leaveEvent(self, event):
        self.hover_changed.emit(False)

    def mouseReleaseEvent(self, event):
        self.play_clicked.emit()


class VoiceCard(QFrame):
    clicked = Signal()
    fav_toggled = Signal()
    preview_toggled = Signal()

    def __init__(self, window, name, premium, selected, favorite, parent=None):
        super().__init__(parent)
        self.window = window
        self.voice_name = name
        self._hover = False
        self._playing = False
        self.setFixedHeight(74)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 0, 8, 0)
        lay.setSpacing(10)
        self._avatar_pix = window._avatar_pixmap(
            name, "#f5b301" if premium else "#232f4b")
        self.photo = PreviewPhoto()
        self.photo.setFixedSize(40, 40)
        self.photo.setScaledContents(True)
        self.photo.setPixmap(self._avatar_pix)
        self.photo.setStyleSheet("background: transparent;")
        self.photo.hover_changed.connect(self._set_hover)
        self.photo.play_clicked.connect(self.preview_toggled.emit)
        if hasattr(window, "preview_changed"):
            window.preview_changed.connect(self._on_preview_changed)
        lay.addWidget(self.photo)
        tw = QWidget()
        tw.setStyleSheet("background: transparent;")
        tw.setMinimumWidth(90)
        tw.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        tl = QVBoxLayout(tw)
        tl.setContentsMargins(0, 0, 0, 0)
        tl.setSpacing(1)
        n = QLabel(window._display_voice_name(name))
        n.setStyleSheet(
            f"color: {TEXT}; font-size: 13px; font-weight: 600;"
            " background: transparent;"
        )
        s = QLabel(window._voice_subtitle(name, premium))
        s.setStyleSheet(
            f"color: {MUTED}; font-size: 11px; background: transparent;"
        )
        tl.addWidget(n)
        if premium:
            g = QLabel("WillpoVoice Premium")
            g.setStyleSheet(
                "color: #f5b301; font-size: 10px; font-weight: 600;"
                " background: transparent;"
            )
            tl.addWidget(g)
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

    def _set_hover(self, hover):
        self._hover = hover
        self._update_photo()

    def _on_preview_changed(self, name, playing):
        self._playing = (name == self.voice_name) and playing
        if self._hover:
            self._update_photo()

    def _update_photo(self):
        if self._hover:
            self.photo.setPixmap(self._make_overlay())
        else:
            self.photo.setPixmap(self._avatar_pix)

    def _make_overlay(self):
        size = 40
        pix = QPixmap(size, size)
        pix.fill(Qt.GlobalColor.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QColor(0, 0, 0, 160))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(0, 0, size, size)
        p.setPen(QPen(QColor("#f5b301"), 2))
        p.drawEllipse(1, 1, size - 2, size - 2)
        p.setBrush(QColor("#ffffff"))
        p.setPen(Qt.PenStyle.NoPen)
        if self._playing:
            p.drawRoundedRect(14, 13, 5, 14, 2, 2)
            p.drawRoundedRect(22, 13, 5, 14, 2, 2)
        else:
            p.drawPolygon(QPolygon(
                [QPoint(16, 12), QPoint(16, 28), QPoint(29, 20)]))
        p.end()
        return pix

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
print("3. PreviewPhoto + VoiceCard con preview.")

# ---- 4. Conectar preview en _make_card ----
old_mk = """    card.fav_toggled.connect(lambda n=name: self._toggle_fav(n))
    layout.addWidget(card)"""
new_mk = """    card.fav_toggled.connect(lambda n=name: self._toggle_fav(n))
    card.preview_toggled.connect(lambda n=name: self._toggle_preview(n))
    layout.addWidget(card)"""
if old_mk in t:
    t = t.replace(old_mk, new_mk, 1)
    print("4. preview_toggled conectado.")

# ---- 5. Logica de preview en MainWindow ----
if "def _toggle_preview" not in t:
    t += '''

def _toggle_preview(self, name):
    if getattr(self, "_preview_name", "") == name and getattr(
            self, "_preview_playing", False):
        self._stop_preview()
        return
    self._stop_preview()
    try:
        import win32com.client
        if not hasattr(self, "_preview_sapi"):
            self._preview_sapi = win32com.client.Dispatch("SAPI.SpVoice")
        self.exporter.adapter.set_voice(name)
        self._preview_sapi.Voice = self.exporter.adapter.sapi.Voice
        self._preview_sapi.Speak("Hola, este es mi voz.", 1)
        self._preview_name = name
        self._preview_playing = True
        self.preview_changed.emit(name, True)
        self.statusBar().showMessage(f"Previsualizando: {name}")
    except Exception as exc:
        self._preview_playing = False
        QMessageBox.warning(self, "WillpoVoice",
                            f"No se pudo reproducir la muestra: {exc}")


def _stop_preview(self):
    old = getattr(self, "_preview_name", "")
    if getattr(self, "_preview_sapi", None) is not None:
        try:
            self._preview_sapi.Speak("", 2)
        except Exception:
            pass
    self._preview_playing = False
    self._preview_name = ""
    if old:
        self.preview_changed.emit(old, False)


def _check_preview_end(self):
    if getattr(self, "_preview_playing", False):
        try:
            st = self._preview_sapi.Status.RunningState
        except Exception:
            st = 1
        if st != 2:
            self._stop_preview()


MainWindow._toggle_preview = _toggle_preview
MainWindow._stop_preview = _stop_preview
MainWindow._check_preview_end = _check_preview_end
'''
    print("5. Logica de preview agregada.")

# ---- 6. Init: estado + timer de preview ----
old_init = '        self._voices = []'
new_init = """        self._voices = []
        self._preview_name = ""
        self._preview_playing = False
        self._preview_timer = QTimer(self)
        self._preview_timer.timeout.connect(self._check_preview_end)
        self._preview_timer.start(600)"""
if old_init in t and "_preview_timer" not in t.split(old_init)[0]:
    t = t.replace(old_init, new_init, 1)
    print("6. Init preview.")

# ---- 7. Detener preview con el boton Detener ----
old_stop = """def stop_speech(self):
    try:
        self.engine.stop()"""
new_stop = """def stop_speech(self):
    try:
        self._stop_preview()
        self.engine.stop()"""
if old_stop in t:
    t = t.replace(old_stop, new_stop, 1)
    print("7. Detener tambien detiene preview.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
