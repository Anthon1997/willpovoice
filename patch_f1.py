from pathlib import Path
import re, ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")
log = []

# ============ A) PreviewWorker persistente ============
s = t.find("class PreviewWorker")
e = t.find("\ndef _check_preview_end")
if s != -1 and e != -1 and "preview_done" not in t[s:e]:
    new = open("pw_new.py", encoding="utf-8").read()
    t = t[:s] + new + t[e:]
    log.append("A preview")

ce = t.find("def closeEvent")
if ce != -1 and "_preview_worker" not in t[ce:ce + 400]:
    nl = t.find("\n", ce)
    t = (t[:nl + 1] +
         "    w = getattr(self, \"_preview_worker\", None)\n"
         "    if w is not None:\n"
         "        w.shutdown()\n"
         "        w.wait(2000)\n" + t[nl + 1:])
    log.append("A2 closeEvent")

# ============ B1) Orden: Multilingue primero ============
t2 = re.sub(r'self\.lang_combo\.addItems\(\[[^\]]*\]\)',
            'self.lang_combo.addItems(["Multilingüe Premium", '
            '"Español (España)", "Inglés (EEUU)", "Todos"])', t, count=1)
if t2 != t:
    t = t2; log.append("B1 orden")

# ============ B2) Iconos por lineas (indentacion capturada) ============
lines = t.split("\n")
for i, ln in enumerate(lines):
    if "self.lang_combo.setItemIcon(0" in ln:
        ind = ln[:len(ln) - len(ln.lstrip())]
        j = i
        while j < len(lines) and "setItemIcon" in lines[j]:
            j += 1
        lines[i:j] = [
            ind + 'self.lang_combo.setItemIcon(0, QIcon(make_icon("crown", "#f5b544", 16)))',
            ind + 'self.lang_combo.setItemIcon(1, QIcon(self._flag_pixmap("es")))',
            ind + 'self.lang_combo.setItemIcon(2, QIcon(self._flag_pixmap("us")))',
            ind + 'self.lang_combo.setItemIcon(3, QIcon(self._flag_pixmap("world")))',
            ind + 'self.lang_combo.currentIndexChanged.connect(',
            ind + '    lambda _i: self._on_lang_changed())',
            ind + 'self.lang_combo.setCurrentIndex(0)',
        ]
        log.append("B2 corona")
        break
t = "\n".join(lines)

p.write_text(t, encoding="utf-8", newline="\n")
print("FASE 1:", log)
