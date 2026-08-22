from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")
log = []

# ---------- 1) Quitar sorts mal ubicados de v13 ----------
bad = "    out.sort(key=self._sort_key)\n"
n_bad = t.count(bad)
if n_bad:
    t = t.replace(bad, "")
    log.append(f"sorts previos removidos: {n_bad}")

# ---------- 2) Sort DENTRO de _lang_filtered ----------
i = t.find("def _lang_filtered")
if i == -1:
    raise SystemExit("ERROR: no existe _lang_filtered")
j = t.find("return out", i)
line_start = t.rfind("\n", i, j) + 1
t = t[:line_start] + "    out.sort(key=self._sort_key)\n" + t[line_start:]
log.append("sort en _lang_filtered")

# ---------- 3) Sort en bucles de cards ----------
old_loop = 'for name in getattr(self, "_voices", []):'
new_loop = 'for name in sorted(getattr(self, "_voices", []), key=self._sort_key):'
cnt = t.count(old_loop)
if cnt:
    t = t.replace(old_loop, new_loop)
    log.append(f"bucles de cards ordenados: {cnt}")

mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
assert "MainWindow._sort_key = _sort_key" in t
print("OK", log)
