from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")
log = []

# 1) El fix real: addWidget -> addLayout
old = "        row.addWidget(col)\n        row.addStretch(1)"
new = "        row.addLayout(col)\n        row.addStretch(1)"
if old in t:
    t = t.replace(old, new, 1)
    log.append("addLayout")

# 2) Guard anti-warning de arranque (voice_combo aun no existe)
anchor = "def _refill_combo(self):"
if anchor in t and "hasattr(self, \"voice_combo\")" not in t.split(anchor)[1][:200]:
    i = t.find(anchor)
    j = t.find("\n", i) + 1
    t = t[:j] + '    if not hasattr(self, "voice_combo"):\n        return\n' + t[j:]
    log.append("guard refill_combo")

p.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
print("OK", log)
