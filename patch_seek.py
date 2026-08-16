from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")
log = []

# 1) Reemplazar la linea comentada por conexiones pressed/released
lines = t.split("\n")
for i, ln in enumerate(lines):
    if "sliderMoved.connect(self._on_slider_moved)" in ln:
        ind = ln[:len(ln) - len(ln.lstrip())]
        lines[i] = (ind + "self.progress_slider.sliderPressed.connect(self._on_slider_pressed)\n" +
                    ind + "self.progress_slider.sliderReleased.connect(self._on_slider_released)")
        log.append("1 conexiones seek")
        break
t = "\n".join(lines)

# 2) Congelar actualizacion del slider mientras el usuario arrastra
old = """    if not getattr(self, "_media_ready", False):
        return
    secs = pos / 1000.0"""
new = """    if not getattr(self, "_media_ready", False):
        return
    if getattr(self, "_seeking", False):
        return
    secs = pos / 1000.0"""
if old in t:
    t = t.replace(old, new, 1)
    log.append("2 freeze durante arrastre")

# 3) Metodos pressed/released (seek al soltar)
if "def _on_slider_pressed" not in t:
    anchor = "def _on_slider_moved(self, pos):"
    add = '''def _on_slider_pressed(self):
    self._seeking = True


def _on_slider_released(self):
    self._seeking = False
    self._on_slider_moved(self.progress_slider.value())


'''
    if anchor in t:
        t = t.replace(anchor, add + anchor, 1)
        log.append("3 metodos seek")

for m in ["_on_slider_pressed", "_on_slider_released"]:
    tag = f"MainWindow.{m} = {m}"
    if tag not in t:
        t += f"\n{tag}\n"
        log.append("4 " + m)

p.write_text(t, encoding="utf-8", newline="\n")
print("SEEK:", log)
try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as ex:
    print("ERROR:", ex.lineno, ex.msg)
