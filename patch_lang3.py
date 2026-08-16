from pathlib import Path
import re, ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

print("crown.svg existe:", Path("assets/icons/svg/crown.svg").exists())

# 1) Reordenar: Multilingue Premium PRIMERO
t = re.sub(
    r'self\.lang_combo\.addItems\(\[[^\]]*\]\)',
    'self.lang_combo.addItems(["Multilingüe Premium", "Español (España)", '
    '"Inglés (EEUU)", "Todos"])',
    t, count=1)
print("1) orden aplicado")

# 2) Reemplazar bloque de iconos + conexion + indice por defecto
s = t.find("self.lang_combo.setItemIcon(0")
m = t.find("setCurrentIndex", s)
e = t.find("\n", m)
new_block = (
    'self.lang_combo.setItemIcon(0, QIcon(make_icon("crown", "#f5b544", 16)))\n'
    '        self.lang_combo.setItemIcon(1, QIcon(self._flag_pixmap("es")))\n'
    '        self.lang_combo.setItemIcon(2, QIcon(self._flag_pixmap("us")))\n'
    '        self.lang_combo.setItemIcon(3, QIcon(self._flag_pixmap("world")))\n'
    '        self.lang_combo.currentIndexChanged.connect(\n'
    '            lambda _i: self._on_lang_changed())\n'
    '        self.lang_combo.setCurrentIndex(0)'
)
if s != -1 and e > s:
    t = t[:s] + new_block + t[e:]
    print("2) corona + default indice 0")

p.write_text(t, encoding="utf-8")
try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as ex:
    print("ERROR:", ex.lineno, ex.msg)

# Verificacion visual del bloque final
t2 = p.read_text(encoding="utf-8")
i = t2.find("self.lang_combo = QComboBox()")
print(t2[i:i + 700])
