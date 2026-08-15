from pathlib import Path
import re, ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# ---- 1. RECOPILACION: imprimir estado actual ----
for marker in ("def set_collapsed", "def _toggle_sidebar"):
    i = t.find(marker)
    j = t.find("\ndef ", i + 10)
    print(f"===== {marker} (actual) =====")
    print(t[i:j if j != -1 else i + 600])

# ---- 2. REESCRITURA: colapso organico ----
new_collapsed = '''    def set_collapsed(self, collapsed):
        self.label.setVisible(not collapsed)
        lay = self.layout()
        if collapsed:
            lay.setContentsMargins(0, 0, 0, 0)
            lay.setSpacing(0)
            lay.setAlignment(self.icon, Qt.AlignmentFlag.AlignCenter)
            self.icon.setFixedSize(24, 24)
        else:
            lay.setContentsMargins(14, 0, 12, 0)
            lay.setSpacing(12)
            lay.setAlignment(self.icon, Qt.AlignmentFlag.AlignLeft)
            self.icon.setFixedSize(20, 20)

'''
t = re.sub(
    r"    def set_collapsed\(self, collapsed\):[\s\S]*?(?=\n    def )",
    new_collapsed,
    t,
    count=1,
)
print("set_collapsed reescrito.")

new_toggle = '''def _toggle_sidebar(self):
    collapsed = self.sidebar.width() > 100
    self.sidebar.setFixedWidth(72 if collapsed else 232)
    sb_lay = self.sidebar.layout()
    if collapsed:
        sb_lay.setContentsMargins(10, 14, 10, 14)
        sb_lay.setAlignment(
            self.hamburger, Qt.AlignmentFlag.AlignHCenter)
    else:
        sb_lay.setContentsMargins(14, 14, 14, 14)
        sb_lay.setAlignment(
            self.hamburger, Qt.AlignmentFlag.AlignLeft)
    for btn, _pg in self._nav:
        btn.set_collapsed(collapsed)
    self._logo_name.setVisible(not collapsed)
    self._logo_ver.setVisible(not collapsed)
    self._prem_card.setVisible(not collapsed)

'''
t = re.sub(
    r"def _toggle_sidebar\(self\):[\s\S]*?(?=\ndef _set_rtab)",
    new_toggle,
    t,
    count=1,
)
print("_toggle_sidebar reescrito.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
