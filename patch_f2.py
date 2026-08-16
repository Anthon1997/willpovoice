from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")
log = []

# ============ C) Metodos de filtrado antes de _rebuild_cards ============
if "def _voice_lang" not in t:
    anchor = "def _rebuild_cards(self):"
    methods = '''def _voice_lang(self, name):
    low = name.lower()
    if "multilingual" in low:
        return "multi"
    if "spanish" in low or "espa" in low or "es-" in low or "(es)" in low:
        return "es"
    if "english" in low or "ingl" in low or "en-" in low or "(en)" in low:
        return "en"
    return "otro"


def _lang_filtered(self, names):
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


'''
    if anchor in t:
        t = t.replace(anchor, methods + anchor, 1)
        log.append("C metodos")

# ============ D) Filtro dentro de _rebuild_cards ============
old = """        if q and q not in name.lower():
            continue
        self._rec_names.append(name)"""
new = """        if q and q not in name.lower():
            continue
        vl = self._voice_lang(name)
        lang = self.lang_combo.currentText()
        if lang.startswith("Espa") and vl != "es":
            continue
        if lang.startswith("Ingl") and vl != "en":
            continue
        if lang.startswith("Multiling") and not premium:
            continue
        self._rec_names.append(name)"""
if old in t:
    t = t.replace(old, new, 1)
    log.append("D filtro tarjetas")

# ============ E) _load_voices con refill ============
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
    t = t.replace(old, new, 1)
    log.append("E load_voices")

# ============ F) Asignaciones ============
for m in ["_get_preview_worker", "_voice_lang", "_lang_filtered",
          "_refill_combo", "_on_lang_changed"]:
    tag = f"MainWindow.{m} = {m}"
    if tag not in t:
        t += f"\n{tag}\n"
        log.append("F " + m)

p.write_text(t, encoding="utf-8", newline="\n")
print("FASE 2:", log)
try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as ex:
    print("ERROR:", ex.lineno, ex.msg)
