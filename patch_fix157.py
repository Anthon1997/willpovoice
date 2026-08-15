from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# ---- 1. Panel recomendado paginado ----
old_rec = """def _rebuild_cards(self):
    self._clear_layout(self.voice_cards_layout)
    q = self.search_edit.text().strip().lower()
    for name in getattr(self, "_voices", []):
        premium = self._is_premium(name)
        if getattr(self, "_rtab", "todas") == "premium" and not premium:
            continue
        if getattr(self, "_rtab", "todas") == "favoritas" and name not in self._favorites():
            continue
        if q and q not in name.lower():
            continue
        self._make_card(name, self.voice_cards_layout)
    self.voice_cards_layout.addStretch()"""
new_rec = '''def _rebuild_cards(self):
    self._clear_layout(self.voice_cards_layout)
    q = self.search_edit.text().strip().lower()
    self._rec_names = []
    for name in getattr(self, "_voices", []):
        premium = self._is_premium(name)
        if getattr(self, "_rtab", "todas") == "premium" and not premium:
            continue
        if getattr(self, "_rtab", "todas") == "favoritas" and name not in self._favorites():
            continue
        if q and q not in name.lower():
            continue
        self._rec_names.append(name)
    self._rec_shown = 0
    self._rec_more_btn = None
    self._append_rec_cards()


def _append_rec_cards(self):
    btn = getattr(self, "_rec_more_btn", None)
    if btn is not None:
        self.voice_cards_layout.removeWidget(btn)
        btn.deleteLater()
        self._rec_more_btn = None
    chunk = self._rec_names[self._rec_shown:self._rec_shown + 30]
    for name in chunk:
        self._make_card(name, self.voice_cards_layout)
    self._rec_shown += len(chunk)
    if self._rec_shown < len(self._rec_names):
        more = QPushButton(
            f"Mostrar mas voces ({len(self._rec_names) - self._rec_shown})")
        more.setCursor(Qt.CursorShape.PointingHandCursor)
        more.setStyleSheet(
            "QPushButton { background: transparent; color: " + MUTED + ";"
            " border: 1px dashed " + BORDER + "; border-radius: 10px;"
            f" padding: 8px; }} QPushButton:hover {{ color: {TEXT}; }}"
        )
        more.clicked.connect(self._append_rec_cards)
        self._rec_more_btn = more
        self.voice_cards_layout.addWidget(more)'''
if old_rec in t:
    t = t.replace(old_rec, new_rec, 1)
    print("1. Panel recomendado paginado (30 + Mostrar mas).")

# ---- 2. Pagina Voces paginada ----
old_all = """def _rebuild_all_page(self):
    self._clear_layout(self.all_layout)
    for name in getattr(self, "_voices", []):
        self._make_card(name, self.all_layout)
    self.all_layout.addStretch()"""
new_all = '''def _rebuild_all_page(self):
    self._clear_layout(self.all_layout)
    self._all_names = list(getattr(self, "_voices", []))
    self._all_shown = 0
    self._all_more_btn = None
    self._append_all_cards()


def _append_all_cards(self):
    btn = getattr(self, "_all_more_btn", None)
    if btn is not None:
        self.all_layout.removeWidget(btn)
        btn.deleteLater()
        self._all_more_btn = None
    chunk = self._all_names[self._all_shown:self._all_shown + 60]
    for name in chunk:
        self._make_card(name, self.all_layout)
    self._all_shown += len(chunk)
    if self._all_shown < len(self._all_names):
        more = QPushButton(
            f"Mostrar mas voces ({len(self._all_names) - self._all_shown})")
        more.setCursor(Qt.CursorShape.PointingHandCursor)
        more.setStyleSheet(
            "QPushButton { background: transparent; color: " + MUTED + ";"
            " border: 1px dashed " + BORDER + "; border-radius: 10px;"
            f" padding: 8px; }} QPushButton:hover {{ color: {TEXT}; }}"
        )
        more.clicked.connect(self._append_all_cards)
        self._all_more_btn = more
        self.all_layout.addWidget(more)'''
if old_all in t:
    t = t.replace(old_all, new_all, 1)
    print("2. Pagina Voces paginada (60 + Mostrar mas).")

# ---- 3. Asignaciones ----
if "MainWindow._append_rec_cards" not in t:
    t += "\nMainWindow._append_rec_cards = _append_rec_cards\n"
    t += "MainWindow._append_all_cards = _append_all_cards\n"
    print("3. Metodos asignados.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
