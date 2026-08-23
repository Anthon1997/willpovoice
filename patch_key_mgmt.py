from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")
log = []

# ============ 1) Boton Eliminar API Key en el header de la tarjeta ============
anchor_hdr = "    hdr.addStretch(1)\n    bv.addLayout(hdr)"
if "btn_del" not in t and anchor_hdr in t:
    i = t.find(anchor_hdr)
    btn = '''    btn_del = QPushButton("  Eliminar API Key")
    btn_del.setIcon(QIcon(make_icon("trash", "#ff7b72", 13)))
    btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
    btn_del.setStyleSheet(
        "QPushButton { background: transparent; color: #ff7b72;"
        " border: 1px solid rgba(255,123,114,80); border-radius: 14px;"
        " padding: 6px 12px; font-size: 10.5px; font-weight: 600; }"
        " QPushButton:hover { background: rgba(255,123,114,25); }")
    btn_del.clicked.connect(self._delete_groq_key)
    hdr.addWidget(btn_del)
'''
    t = t[:i] + btn + t[i:]
    log.append("boton eliminar")

# ============ 2) Configurar API Key = toggle abrir/cerrar ============
old_cfg = '''def _configure_groq_key(self):
    self._switch_page(5)
    self._chat_banner.setVisible(True)
    try:
        self._groq_key_input.setFocus()
    except Exception:
        pass'''
new_cfg = '''def _configure_groq_key(self):
    self._switch_page(5)
    vis = self._chat_banner.isVisible()
    self._chat_banner.setVisible(not vis)
    if not vis:
        try:
            self._groq_key_input.setFocus()
        except Exception:
            pass'''
if old_cfg in t:
    t = t.replace(old_cfg, new_cfg, 1)
    log.append("toggle configurar")

# ============ 3) Metodo _delete_groq_key ============
anchor_att = "MainWindow._save_groq_key = _save_groq_key"
if "def _delete_groq_key" not in t and anchor_att in t:
    i = t.find(anchor_att)
    fn = '''def _delete_groq_key(self):
    from PySide6.QtCore import QSettings
    s = QSettings("WillpoVoice", "WillpoVoice")
    s.remove("groq_api_key")
    try:
        self._groq_key_input.clear()
    except Exception:
        pass
    self._set_chat_locked(True)
    self._chat_banner.setVisible(True)
    self._add_chat_bubble(
        "API Key eliminada. Configura una nueva cuando quieras.",
        is_user=False)


MainWindow._delete_groq_key = _delete_groq_key
'''
    t = t[:i] + fn + t[i:]
    log.append("_delete_groq_key")

mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
assert "MainWindow._delete_groq_key = _delete_groq_key" in t
print("OK", log)
