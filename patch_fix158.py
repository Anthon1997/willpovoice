from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# ---- 1. Combo sin iconos en el bucle (por tandas despues) ----
old_loop = """            self.voice_combo.setItemData(idx, v, Qt.ItemDataRole.UserRole)
            self.voice_combo.setItemIcon(idx, QIcon(self._avatar_pixmap(v)))"""
new_loop = """            self.voice_combo.setItemData(idx, v, Qt.ItemDataRole.UserRole)"""
if old_loop in t:
    t = t.replace(old_loop, new_loop, 1)
    print("1. Iconos fuera del bucle de carga.")

# ---- 2. Arranque: solo panel recomendado + tandas de iconos ----
old_tail = """        self.voice_combo.blockSignals(False)
        self.stat_voices.value_label.setText(f"{len(voices)}+")
        self._rebuild_cards()
        self._rebuild_all_page()
        self._rebuild_fav_page()"""
new_tail = """        self.voice_combo.blockSignals(False)
        self.stat_voices.value_label.setText(f"{len(voices)}+")
        self._all_built = False
        self._fav_built = False
        self._icon_queue = list(range(self.voice_combo.count()))
        if not hasattr(self, "_icon_timer"):
            self._icon_timer = QTimer(self)
            self._icon_timer.timeout.connect(self._chunk_icons)
        self._icon_timer.start(60)
        self._rebuild_cards()"""
if old_tail in t:
    t = t.replace(old_tail, new_tail, 1)
    print("2. Arranque ligero (sin paginas Voces/Favoritos).")

# ---- 3. _switch_page con construccion perezosa ----
old_sp = """def _switch_page(self, index):
    self.pages.setCurrentIndex(index)
    for i, (btn, _pg) in enumerate(self._nav):
        btn.set_active(i == index)
    self.right_panel.setVisible(index == 0)"""
new_sp = """def _switch_page(self, index):
    self.pages.setCurrentIndex(index)
    for i, (btn, _pg) in enumerate(self._nav):
        btn.set_active(i == index)
    self.right_panel.setVisible(index == 0)
    if index == 2 and not getattr(self, "_all_built", False):
        self._all_built = True
        self._rebuild_all_page()
    if index == 3 and not getattr(self, "_fav_built", False):
        self._fav_built = True
        self._rebuild_fav_page()"""
if old_sp in t:
    t = t.replace(old_sp, new_sp, 1)
    print("3. Paginas lazy al primer visita.")

# ---- 4. Marcar construidas en los rebuilds ----
t = t.replace(
    "def _rebuild_all_page(self):\n    self._clear_layout(self.all_layout)",
    "def _rebuild_all_page(self):\n    self._all_built = True\n    self._clear_layout(self.all_layout)",
    1,
)
t = t.replace(
    "def _rebuild_fav_page(self):\n    self._clear_layout(self.fav_layout)",
    "def _rebuild_fav_page(self):\n    self._fav_built = True\n    self._clear_layout(self.fav_layout)",
    1,
)
print("4. Rebuilds marcan paginas construidas.")

# ---- 5. _chunk_icons ----
if "def _chunk_icons" not in t:
    t += '''

def _chunk_icons(self):
    if not getattr(self, "_icon_queue", None):
        self._icon_timer.stop()
        return
    batch = self._icon_queue[:40]
    self._icon_queue = self._icon_queue[40:]
    for idx in batch:
        v = self.voice_combo.itemData(idx, Qt.ItemDataRole.UserRole)
        if v:
            self.voice_combo.setItemIcon(idx, QIcon(self._avatar_pixmap(v)))
    if not self._icon_queue:
        self._icon_timer.stop()


MainWindow._chunk_icons = _chunk_icons
'''
    print("5. Iconos del combo en tandas de 40.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
