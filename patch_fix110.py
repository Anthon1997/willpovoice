from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")
changed = False

# 1. Inicializar atributos en __init__
if "self._rtab = " not in t:
    if "self.export_worker = None" in t:
        t = t.replace(
            "self.export_worker = None",
            "self.export_worker = None\n"
            '        self._rtab = "todas"\n'
            '        self._selected_voice = ""\n'
            "        self._voices = []",
            1,
        )
        changed = True
        print("1. Inicializados en __init__ (tras export_worker).")
    elif "self._build_ui()" in t:
        t = t.replace(
            "self._build_ui()",
            'self._rtab = "todas"\n'
            '        self._selected_voice = ""\n'
            "        self._voices = []\n"
            "        self._build_ui()",
            1,
        )
        changed = True
        print("1. Inicializados antes de _build_ui.")
else:
    print("1. Ya estaban inicializados.")

# 2. Filtros defensivos con getattr
old = 'if self._rtab == "premium" and not premium:'
new = 'if getattr(self, "_rtab", "todas") == "premium" and not premium:'
if old in t:
    t = t.replace(old, new, 1)
    changed = True
    print("2a. Filtro premium defensivo.")

old2 = 'if self._rtab == "favoritas" and name not in self._favorites():'
new2 = ('if getattr(self, "_rtab", "todas") == "favoritas" '
        'and name not in self._favorites():')
if old2 in t:
    t = t.replace(old2, new2, 1)
    changed = True
    print("2b. Filtro favoritas defensivo.")

# 3. _selected_voice defensivo en _make_card
if "name == self._selected_voice" in t:
    t = t.replace(
        "name == self._selected_voice",
        'name == getattr(self, "_selected_voice", "")',
    )
    changed = True
    print("3. _selected_voice defensivo.")

if changed:
    p.write_text(t, encoding="utf-8")

try:
    ast.parse(p.read_text(encoding="utf-8"))
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
