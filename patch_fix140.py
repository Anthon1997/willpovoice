from pathlib import Path
import re, ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# ---- 1. RECOPILACION ----
for m in ("page1 = QWidget()", "def _load_history",
          "history_list.itemClicked", "def _on_history_click"):
    print(f"--- {m!r} indice:", t.find(m))

# ---- 2. HistoryCard moderna ----
if "class HistoryCard" not in t:
    hcard = '''class HistoryCard(QFrame):
    load_clicked = Signal()
    delete_clicked = Signal()

    def __init__(self, window, entry, parent=None):
        super().__init__(parent)
        self.setFixedHeight(74)
        label = entry.get("label", "Texto manual")
        low = label.lower()
        if low.endswith(".pdf"):
            kind, color = "doc", RED
        elif low.endswith((".doc", ".docx", ".rtf")):
            kind, color = "doc", BLUE
        elif low.endswith((".txt", ".md", ".log", ".csv")):
            kind, color = "doc", TEAL
        elif label == "Texto manual":
            kind, color = "text", TEAL
        else:
            kind, color = "doc", MUTED
        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 0, 10, 0)
        lay.setSpacing(12)
        box = QFrame()
        box.setFixedSize(40, 40)
        box.setStyleSheet(
            f"QFrame {{ background: {CARD2}; border-radius: 10px; }}")
        bl = QVBoxLayout(box)
        bl.setContentsMargins(0, 0, 0, 0)
        ic = IconLabel(kind, 17, color)
        ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bl.addWidget(ic)
        lay.addWidget(box)
        tw = QWidget()
        tw.setStyleSheet("background: transparent;")
        tw.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        tl = QVBoxLayout(tw)
        tl.setContentsMargins(0, 0, 0, 0)
        tl.setSpacing(2)
        n = QLabel(label)
        n.setStyleSheet(
            f"color: {TEXT}; font-size: 13px; font-weight: 600;"
            " background: transparent;"
        )
        preview = QLabel(
            (entry.get("content", "") or "").replace("\\n", " ")[:80])
        preview.setStyleSheet(
            f"color: {MUTED}; font-size: 11px; background: transparent;"
        )
        tl.addWidget(n)
        tl.addWidget(preview)
        lay.addWidget(tw, 1)
        load_btn = SquareButton("paste", "Cargar en el editor")
        load_btn.setFixedSize(34, 34)
        load_btn.clicked.connect(self.load_clicked.emit)
        del_btn = SquareButton("trash", "Eliminar entrada")
        del_btn.setFixedSize(34, 34)
        del_btn.setStyleSheet(
            f"SquareButton {{ background: {CARD}; border: 1px solid"
            f" {BORDER}; border-radius: 10px; }}"
            " SquareButton:hover { background: rgba(239,68,68,60); }"
        )
        del_btn.icon.setPixmap(make_icon("trash", RED, 19))
        del_btn.clicked.connect(self.delete_clicked.emit)
        lay.addWidget(load_btn)
        lay.addWidget(del_btn)
        self.setStyleSheet(
            f"HistoryCard {{ background: {CARD}; border: none;"
            f" border-radius: 12px; }} HistoryCard:hover {{ background: {CARD2}; }}"
        )


'''
    t = t.replace("class MainWindow(QMainWindow):",
                  hcard + "class MainWindow(QMainWindow):", 1)
    print("2. HistoryCard agregada.")

# ---- 3. Pagina Historial moderna ----
old_page1 = """    page1 = QWidget()
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
    self.pages.addWidget(page1)"""
new_page1 = """    page1 = QWidget()
    h1 = QVBoxLayout(page1)
    h1.setContentsMargins(20, 16, 20, 16)
    h1.setSpacing(12)
    ht = QLabel("Historial")
    ht.setStyleSheet(f"color: {TEXT}; font-size: 20px; font-weight: 700;")
    self.hist_scroll = QScrollArea()
    self.hist_scroll.setWidgetResizable(True)
    self.hist_scroll.setFrameShape(QFrame.Shape.NoFrame)
    self.hist_scroll.setHorizontalScrollBarPolicy(
        Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    self.hist_scroll.setStyleSheet(
        "QScrollArea { background: transparent; border: none; }")
    self.hist_container = QWidget()
    self.hist_container.setStyleSheet("background: transparent;")
    self.history_layout = QVBoxLayout(self.hist_container)
    self.history_layout.setContentsMargins(0, 0, 6, 0)
    self.history_layout.setSpacing(8)
    self.hist_scroll.setWidget(self.hist_container)
    self.btn_clear_hist = QPushButton("Limpiar historial")
    self.btn_clear_hist.setCursor(Qt.CursorShape.PointingHandCursor)
    self.btn_clear_hist.setStyleSheet(
        "QPushButton { background: transparent; color: " + RED + ";"
        f" border: 1px solid {BORDER}; border-radius: 10px;"
        " padding: 8px 16px; }"
        " QPushButton:hover { background: rgba(239,68,68,40); }"
    )
    h1.addWidget(ht)
    h1.addWidget(self.hist_scroll, 1)
    h1.addWidget(self.btn_clear_hist, 0, Qt.AlignmentFlag.AlignLeft)
    self.pages.addWidget(page1)"""
if old_page1 in t:
    t = t.replace(old_page1, new_page1, 1)
    print("3. Pagina Historial moderna.")

# ---- 4. Quitar conexion vieja del QListWidget ----
old_conn = "    self.history_list.itemClicked.connect(self._on_history_click)\n"
if old_conn in t:
    t = t.replace(old_conn, "", 1)
    print("4. Conexion vieja eliminada.")

# ---- 5. Funciones de historial nuevas ----
new_hist = '''def _load_history(self):
    self._clear_layout(self.history_layout)
    self._history_full = []
    items = self.settings.get("history", [])
    for idx, it in enumerate(items):
        entry = it if isinstance(it, dict) else {
            "content": it, "label": "Texto manual"}
        self._history_full.append(entry)
        card = HistoryCard(self, entry)
        card.load_clicked.connect(lambda i=idx: self._load_entry(i))
        card.delete_clicked.connect(lambda i=idx: self._delete_entry(i))
        self.history_layout.addWidget(card)
    self.history_layout.addStretch()


def _load_entry(self, idx):
    if 0 <= idx < len(self._history_full):
        self.text_edit.setPlainText(
            self._history_full[idx].get("content", ""))
        self._switch_page(0)
        self.statusBar().showMessage("Contenido cargado en el editor.")


def _delete_entry(self, idx):
    items = self.settings.get("history", [])
    items = [it if isinstance(it, dict) else {
        "content": it, "label": "Texto manual"} for it in items]
    if 0 <= idx < len(items):
        items.pop(idx)
        self.settings["history"] = items
        self._load_history()
        self.statusBar().showMessage("Entrada eliminada del historial.")


'''
t = re.sub(
    r"def _load_history\(self\):[\s\S]*?(?=\ndef clear_history)",
    new_hist,
    t,
    count=1,
)
print("5. Funciones de historial nuevas.")

# ---- 6. Asignar nuevos metodos ----
if "MainWindow._load_entry" not in t:
    t += "\nMainWindow._load_entry = _load_entry\n"
    t += "MainWindow._delete_entry = _delete_entry\n"
    print("6. Metodos asignados.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
