from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# 1) Corona + conexion a _on_lang_changed + indice por defecto 2
old = """        self.lang_combo.setItemIcon(2, QIcon(make_icon("globe", PURPLE, 16)))
        self.lang_combo.setItemIcon(3, QIcon(self._flag_pixmap("world")))
        self.lang_combo.currentIndexChanged.connect(
            lambda _i: self._rebuild_cards())"""
new = """        self.lang_combo.setItemIcon(2, QIcon(make_icon("crown", "#f5b544", 16)))
        self.lang_combo.setItemIcon(3, QIcon(self._flag_pixmap("world")))
        self.lang_combo.currentIndexChanged.connect(
            lambda _i: self._on_lang_changed())
        self.lang_combo.setCurrentIndex(2)"""
if old in t:
    t = t.replace(old, new, 1); print("1) corona + default Multilingue")

# 2) Nuevos metodos de filtrado y refill del combo
old = "def _rebuild_cards(self):"
new = '''def _lang_filtered(self, names):
    lang = self.lang_combo.currentText()
    out = []
    for name in names:
        vl = self._voice_lang(name)
        if lang.startswith("Espa") and vl != "es":
            continue
        if lang.startswith("Ingl") and vl != "en":
            continue
        if lang.startswith("Multiling") and not self._is_premium(name):
            continue
        out.append(name)
    return out


def _refill_combo(self):
    cur = self.voice_combo.currentData(Qt.ItemDataRole.UserRole)
    names = self._lang_filtered(getattr(self, "_voices", []))
    self.voice_combo.blockSignals(True)
    self.voice_combo.clear()
    for v in names:
        self.voice_combo.addItem(self._display_voice_name(v))
        idx = self.voice_combo.count() - 1
        self.voice_combo.setItemData(idx, v, Qt.ItemDataRole.UserRole)
    self.voice_combo.blockSignals(False)
    if cur in names:
        self.voice_combo.setCurrentIndex(names.index(cur))
    elif names:
        self.voice_combo.setCurrentIndex(0)
    self._icon_queue = list(range(self.voice_combo.count()))
    if hasattr(self, "_icon_timer"):
        self._icon_timer.start(60)


def _on_lang_changed(self):
    self._refill_combo()
    self._rebuild_cards()


def _rebuild_cards(self):'''
if old in t:
    t = t.replace(old, new, 1); print("2) metodos de filtrado insertados")

# 3) _load_voices usa _refill_combo y selecciona dentro del filtro
old = """        self._voices = voices
        self.voice_combo.blockSignals(True)
        self.voice_combo.clear()
        for v in voices:
            self.voice_combo.addItem(self._display_voice_name(v))
            idx = self.voice_combo.count() - 1
            self.voice_combo.setItemData(idx, v, Qt.ItemDataRole.UserRole)
        last = self.settings.get("last_voice", "")
        if last in voices:
            self._select_voice(last)
        elif voices:
            pref = next((v for v in voices if "SeraphinaMultilingual" in v),
                        voices[0])
            self._select_voice(pref)
        self.voice_combo.blockSignals(False)
        self.stat_voices.value_label.setText(f"{len(voices)}+")"""
new = """        self._voices = voices
        self._refill_combo()
        names = self._lang_filtered(voices)
        last = self.settings.get("last_voice", "")
        if last in names:
            self._select_voice(last)
        elif names:
            pref = next((v for v in names if "SeraphinaMultilingual" in v),
                        names[0])
            self._select_voice(pref)
        self.stat_voices.value_label.setText(f"{len(voices)}+")"""
if old in t:
    t = t.replace(old, new, 1); print("3) _load_voices filtra por idioma")

for m in ["_lang_filtered", "_refill_combo", "_on_lang_changed"]:
    tag = f"MainWindow.{m} = {m}"
    if tag not in t:
        t += f"\n{tag}\n"

p.write_text(t, encoding="utf-8")
try:
    ast.parse(t); print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
