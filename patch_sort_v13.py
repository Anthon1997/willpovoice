from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")
log = []

# ---------- 1) Helper de orden ----------
if "def _sort_key(self" not in t:
    anchor = "MainWindow._lang_filtered = _lang_filtered"
    i = t.find(anchor)
    if i != -1:
        eol = t.find("\n", i)
        block = '''

def _sort_key(self, name):
    low = (name or "").lower()
    if "multilingual" in low:
        return 0
    try:
        vl = self._voice_lang(name)
    except Exception:
        vl = "otro"
    return 2 if vl == "es" else 1

MainWindow._sort_key = _sort_key
'''
        t = t[:eol+1] + block + t[eol+1:]
        log.append("_sort_key")

# ---------- 2) Aplicar orden en _lang_filtered ----------
old_ret = "        out.append(name)\n    return out"
new_ret = "        out.append(name)\n    out.sort(key=self._sort_key)\n    return out"
if old_ret in t and "out.sort(key=self._sort_key)" not in t:
    t = t.replace(old_ret, new_ret, 1)
    log.append("sort aplicado")

mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
assert "MainWindow._sort_key = _sort_key" in t
print("OK", log)
