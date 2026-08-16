from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# 1) Agregar opcion Multilingue Premium
old = 'self.lang_combo.addItems(["Español (España)", "Inglés (EEUU)", "Todos"])'
new = 'self.lang_combo.addItems(["Español (España)", "Inglés (EEUU)", "Multilingüe Premium", "Todos"])'
if old in t:
    t = t.replace(old, new, 1); print("1) opcion agregada")

# 2) Iconos + conexion a rebuild
old = """        self.lang_combo.setItemIcon(0, QIcon(self._flag_pixmap("es")))
        self.lang_combo.setItemIcon(1, QIcon(self._flag_pixmap("us")))
        self.lang_combo.setItemIcon(2, QIcon(self._flag_pixmap("world")))"""
new = """        self.lang_combo.setItemIcon(0, QIcon(self._flag_pixmap("es")))
        self.lang_combo.setItemIcon(1, QIcon(self._flag_pixmap("us")))
        self.lang_combo.setItemIcon(2, QIcon(make_icon("globe", PURPLE, 16)))
        self.lang_combo.setItemIcon(3, QIcon(self._flag_pixmap("world")))
        self.lang_combo.currentIndexChanged.connect(
            lambda _i: self._rebuild_cards())"""
if old in t:
    t = t.replace(old, new, 1); print("2) conexion agregada")

# 3) Metodo _voice_lang + filtro en _rebuild_cards
old = "def _rebuild_cards(self):"
new = """def _voice_lang(self, name):
    low = name.lower()
    if "multilingual" in low:
        return "multi"
    if "spanish" in low or "espa" in low or "es-" in low or "(es)" in low:
        return "es"
    if "english" in low or "ingl" in low or "en-" in low or "(en)" in low:
        return "en"
    return "otro"


def _rebuild_cards(self):"""
if old in t:
    t = t.replace(old, new, 1); print("3) _voice_lang insertado")

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
    t = t.replace(old, new, 1); print("4) filtro de idioma aplicado")

if "MainWindow._voice_lang = _voice_lang" not in t:
    t += "\nMainWindow._voice_lang = _voice_lang\n"

p.write_text(t, encoding="utf-8")
try:
    ast.parse(t); print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
