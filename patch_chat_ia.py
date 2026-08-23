from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")
log = []

# 1) Agregar botón "Chat IA" en el sidebar (índice 5, antes de Ajustes)
old_nav = '''    for glyph, text, page in (
        ("home", "Inicio", 0), ("history", "Historial", 1),
        ("mic", "Voces", 2), ("heart", "Favoritos", 3),
        ("folder", "Proyectos", 4), ("gear", "Ajustes", 5),
    ):'''

new_nav = '''    for glyph, text, page in (
        ("home", "Inicio", 0), ("history", "Historial", 1),
        ("mic", "Voces", 2), ("heart", "Favoritos", 3),
        ("folder", "Proyectos", 4), ("sparkles", "Chat IA", 5),
        ("gear", "Ajustes", 6),
    ):'''

if old_nav in t:
    t = t.replace(old_nav, new_nav)
    log.append("botón Chat IA en sidebar")
else:
    print("ERROR: no encontré bloque nav")

# 2) Actualizar índices de páginas en _switch_page (gear ahora es 6)
# Buscar donde se crea page5 (Ajustes) y renombrar a page6
t = t.replace("page5 = QWidget()", "page6 = QWidget()")
t = t.replace("self.pages.addWidget(page5)", "self.pages.addWidget(page6)")
log.append("Ajustes movido a página 6")

# 3) Crear página 5 (Chat IA) antes de page6
anchor_page6 = "    page6 = QWidget()"
if anchor_page6 in t and "page5 = QWidget()" not in t:
    idx = t.find(anchor_page6)
    chat_page = '''    # ---------- PAGINA 5: CHAT IA ----------
    page5 = QWidget()
    p5 = QVBoxLayout(page5)
    p5.setContentsMargins(24, 24, 24, 24)
    p5.setSpacing(16)

    # Header
    h5 = QHBoxLayout()
    h5.setSpacing(10)
    ico5 = QLabel()
    ico5.setPixmap(make_icon("sparkles", "#bc8cff", 22))
    h5.addWidget(ico5)
    t5 = QLabel("Chat IA")
    t5.setStyleSheet(f"color: {TEXT}; font-size: 20px; font-weight: 800;")
    h5.addWidget(t5)
    h5.addStretch(1)

    # Botón configurar API key
    btn_config = QPushButton("⚙️ Configurar API Key")
    btn_config.setCursor(Qt.CursorShape.PointingHandCursor)
    btn_config.setStyleSheet(
        f"QPushButton {{ background: {BORDER}; color: {TEXT}; border: none;"
        " border-radius: 8px; padding: 6px 12px; font-size: 11px; font-weight: 600; }}"
        " QPushButton:hover { background: #3d4550; }")
    btn_config.clicked.connect(self._configure_groq_key)
    h5.addWidget(btn_config)
    p5.addLayout(h5)

    # Banner si no hay key
    self._chat_banner = QFrame()
    self._chat_banner.setStyleSheet(
        "QFrame { background: #1c1f2e; border: 1px solid #4a3f7a; border-radius: 10px; }")
    bv = QVBoxLayout(self._chat_banner)
    bv.setContentsMargins(16, 12, 16, 12)
    bv.setSpacing(8)
    bt1 = QLabel("🔑 Configura tu API Key de Groq para usar el Chat IA")
    bt1.setStyleSheet(f"color: {TEXT}; font-size: 13px; font-weight: 600;")
    bv.addWidget(bt1)
    bt2 = QLabel("Obtén tu clave gratis en console.groq.com (sin tarjeta de crédito)")
    bt2.setStyleSheet(f"color: {MUTED}; font-size: 11px;")
    bv.addWidget(bt2)
    btn_get_key = QPushButton("🌐 Obtener API Key gratis")
    btn_get_key.setCursor(Qt.CursorShape.PointingHandCursor)
    btn_get_key.setStyleSheet(
        f"QPushButton {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
        f" stop:0 {BLUE}, stop:1 {PURPLE}); color: white; border: none;"
        " border-radius: 8px; padding: 8px 16px; font-weight: 600; }}")
    btn_get_key.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://console.groq.com/keys")))
    bv.addWidget(btn_get_key, 0, Qt.AlignmentFlag.AlignLeft)
    p5.addWidget(self._chat_banner)

    # Área de chat (scroll)
    self._chat_scroll = QScrollArea()
    self._chat_scroll.setWidgetResizable(True)
    self._chat_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
    chat_widget = QWidget()
    self._chat_layout = QVBoxLayout(chat_widget)
    self._chat_layout.setContentsMargins(0, 0, 0, 0)
    self._chat_layout.setSpacing(12)
    self._chat_layout.addStretch(1)
    self._chat_scroll.setWidget(chat_widget)
    p5.addWidget(self._chat_scroll, 1)

    # Input
    input_row = QHBoxLayout()
    input_row.setSpacing(10)
    self._chat_input = QLineEdit()
    self._chat_input.setFixedHeight(44)
    self._chat_input.setPlaceholderText("Escribe tu pregunta...")
    self._chat_input.setStyleSheet(
        f"QLineEdit {{ background: {BORDER}; color: {TEXT}; border: 1px solid {BORDER};"
        " border-radius: 10px; padding: 0 14px; font-size: 13px; }}"
        f" QLineEdit:focus {{ border: 1px solid {BLUE}; }}")
    self._chat_input.returnPressed.connect(self._send_chat_message)
    input_row.addWidget(self._chat_input, 1)

    btn_send = QPushButton("Enviar")
    btn_send.setFixedSize(90, 44)
    btn_send.setCursor(Qt.CursorShape.PointingHandCursor)
    btn_send.setStyleSheet(
        f"QPushButton {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
        f" stop:0 {BLUE}, stop:1 {PURPLE}); color: white; border: none;"
        " border-radius: 10px; font-weight: 700; }}"
        " QPushButton:hover { background: #8d75ff; }")
    btn_send.clicked.connect(self._send_chat_message)
    input_row.addWidget(btn_send)
    p5.addLayout(input_row)

    self.pages.addWidget(page5)

'''
    t = t[:idx] + chat_page + t[idx:]
    log.append("página Chat IA creada")

# 4) Agregar métodos _configure_groq_key y _send_chat_message
# Buscar el final de la clase MainWindow (último método)
anchor_end = "MainWindow._open_plans = _open_plans"
if anchor_end in t:
    idx = t.find(anchor_end)
    methods = '''

def _configure_groq_key(self):
    from PySide6.QtWidgets import QInputDialog
    from PySide6.QtCore import QSettings
    settings = QSettings("WillpoVoice", "WillpoVoice")
    current = settings.value("groq_api_key", "")
    key, ok = QInputDialog.getText(
        self, "Configurar API Key de Groq",
        "Pega tu API Key (obtenla gratis en console.groq.com/keys):",
        text=current)
    if ok and key.strip():
        settings.setValue("groq_api_key", key.strip())
        self._chat_banner.setVisible(False)
        self._add_chat_bubble("✅ API Key configurada. ¡Listo para chatear!", is_user=False)
    elif ok and not key.strip():
        settings.setValue("groq_api_key", "")
        self._chat_banner.setVisible(True)


def _send_chat_message(self):
    from PySide6.QtCore import QSettings, QThread, pyqtSignal
    import core.brain as brain

    text = self._chat_input.text().strip()
    if not text:
        return

    settings = QSettings("WillpoVoice", "WillpoVoice")
    api_key = settings.value("groq_api_key", "")
    if not api_key:
        self._chat_banner.setVisible(True)
        return

    # Actualizar key en brain temporalmente
    brain.GROQ_API_KEY = api_key

    # Agregar burbuja del usuario
    self._add_chat_bubble(text, is_user=True)
    self._chat_input.clear()

    # Mostrar "pensando..."
    thinking = self._add_chat_bubble("🤔 Pensando...", is_user=False, temp=True)

    # Ejecutar en hilo separado
    class ChatWorker(QThread):
        finished = pyqtSignal(str)
        def run(self):
            resp = brain.pensar(text)
            self.finished.emit(resp)

    self._chat_worker = ChatWorker()
    self._chat_worker.finished.connect(lambda r: self._on_chat_response(r, thinking))
    self._chat_worker.start()


def _add_chat_bubble(self, text, is_user, temp=False):
    from PySide6.QtWidgets import QLabel, QHBoxLayout
    bubble = QLabel(text)
    bubble.setWordWrap(True)
    bubble.setStyleSheet(
        f"QLabel {{ background: {'#7c5cff' if is_user else '#1c1f2e'};"
        f" color: {'white' if is_user else TEXT}; border-radius: 10px;"
        f" padding: 10px 14px; font-size: 12px;"
        f" {'margin-left: 60px;' if is_user else 'margin-right: 60px;'} }}")
    bubble.setMaximumWidth(500)
    row = QHBoxLayout()
    row.setContentsMargins(0, 0, 0, 0)
    if is_user:
        row.addStretch(1)
        row.addWidget(bubble)
    else:
        row.addWidget(bubble)
        row.addStretch(1)
    wrap = QWidget()
    wrap.setLayout(row)
    wrap.setProperty("temp", temp)
    self._chat_layout.insertWidget(self._chat_layout.count() - 1, wrap)
    self._chat_scroll.verticalScrollBar().setValue(
        self._chat_scroll.verticalScrollBar().maximum())
    return wrap


def _on_chat_response(self, response, temp_bubble):
    # Eliminar burbuja "pensando..."
    if temp_bubble and temp_bubble.property("temp"):
        temp_bubble.setParent(None)
        temp_bubble.deleteLater()

    # Agregar respuesta real
    self._add_chat_bubble(response, is_user=False)

    # Hablar la respuesta con la voz seleccionada
    try:
        self.adapter.speak(response)
    except Exception as e:
        print(f"TTS falló: {e}")


MainWindow._configure_groq_key = _configure_groq_key
MainWindow._send_chat_message = _send_chat_message
MainWindow._add_chat_bubble = _add_chat_bubble
MainWindow._on_chat_response = _on_chat_response

'''
    t = t[:idx] + methods + t[idx:]
    log.append("métodos de chat agregados")

# 5) Al iniciar, ocultar banner si ya hay key
anchor_init = "self._switch_page(0)"
if anchor_init in t and "chat_banner" not in t[:t.find(anchor_init)+1000]:
    idx = t.find(anchor_init)
    eol = t.find("\n", idx)
    check_key = '''
    # Ocultar banner de chat si ya hay API key
    try:
        from PySide6.QtCore import QSettings
        s = QSettings("WillpoVoice", "WillpoVoice")
        if s.value("groq_api_key", ""):
            self._chat_banner.setVisible(False)
    except Exception:
        pass
'''
    t = t[:eol+1] + check_key + t[eol+1:]
    log.append("check de API key al iniciar")

mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
print("✅ SINTAXIS OK")
print("parches:", log)
