from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

old = "self.stop_button.clicked.connect(self.stop_speech)"
new = "self.stop_button.clicked.connect(self._player_play_clicked)"
if old in t:
    t = t.replace(old, new, 1)
    p.write_text(t, encoding="utf-8")
    print("Detener ahora usa la logica del boton play (pausa/reanuda).")
else:
    print("AVISO: conexion no encontrada. Lineas con stop_button:")
    for ln in t.splitlines():
        if "stop_button" in ln and "connect" in ln:
            print("  ", ln.strip())

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
