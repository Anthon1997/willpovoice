from pathlib import Path
import re, ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# 1. Nueva estructura Idioma / Voz seleccionada (foto 2)
new_sel = '''    sel = QHBoxLayout()
    sel.setSpacing(14)
    combo_qss = (
        f"QComboBox {{ background: #0d1424; color: {TEXT}; border: 1px solid"
        f" {BORDER}; border-radius: 10px; padding: 10px 12px; font-size: 13px;"
        " min-height: 22px; }"
        " QComboBox:hover { border: 1px solid #34406b; }"
        " QComboBox::drop-down { border: none; width: 30px; }"
        f" QComboBox QAbstractItemView {{ background: #10162a; color: {TEXT};"
        f" border: 1px solid {BORDER}; selection-background-color: {CARD2};"
        " padding: 6px; }"
    )
    col1 = QVBoxLayout()
    col1.setSpacing(6)
    l1 = QLabel("Idioma")
    l1.setStyleSheet(
        f"color: {MUTED}; font-size: 11px; background: transparent;"
    )
    self.lang_combo = QComboBox()
    self.lang_combo.addItems(["Español (España)", "Inglés (EEUU)", "Todos"])
    self.lang_combo.setItemIcon(0, QIcon(self._flag_pixmap("es")))
    self.lang_combo.setItemIcon(1, QIcon(self._flag_pixmap("us")))
    self.lang_combo.setItemIcon(2, QIcon(self._flag_pixmap("world")))
    self.lang_combo.setStyleSheet(combo_qss)
    col1.addWidget(l1)
    col1.addWidget(self.lang_combo)
    sel.addLayout(col1, 1)
    col2 = QVBoxLayout()
    col2.setSpacing(6)
    l2 = QLabel("Voz seleccionada")
    l2.setStyleSheet(
        f"color: {MUTED}; font-size: 11px; background: transparent;"
    )
    self.voice_combo = QComboBox()
    self.voice_combo.setStyleSheet(
        combo_qss + " QComboBox { padding: 10px 84px 10px 12px; }"
    )
    self.pro_badge = QLabel("Pro", self.voice_combo)
    self.pro_badge.setStyleSheet(
        f"background: {PURPLE}; color: white; border-radius: 6px;"
        " font-size: 9px; font-weight: 700; padding: 3px 6px;"
    )
    self.pro_badge.setAttribute(
        Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    self.voice_combo.installEventFilter(self)
    col2.addWidget(l2)
    col2.addWidget(self.voice_combo)
    sel.addLayout(col2, 1)
    cl.addLayout(sel)'''

t = re.sub(
    r"    sel = QHBoxLayout\(\)[\s\S]*?    cl\.addLayout\(sel\)",
    lambda _m: new_sel,
    t,
    count=1,
)
print("1. Fila Idioma/Voz reestructurada (foto 2).")

# 2. Badge Pro visible solo en voces premium
old_sv = """def _select_voice(self, name):
    self._selected_voice = name"""
new_sv = """def _select_voice(self, name):
    self._selected_voice = name
    if hasattr(self, "pro_badge"):
        self.pro_badge.setVisible(self._is_premium(name))"""
if old_sv in t:
    t = t.replace(old_sv, new_sv, 1)
    print("2. Badge Pro sincronizado con la voz.")

# 3. eventFilter para posicionar el badge dentro del combo
if "def eventFilter" not in t:
    t += '''

def eventFilter(self, obj, event):
    from PySide6.QtCore import QEvent
    if obj is getattr(self, "voice_combo", None) and event.type() in (
            QEvent.Type.Resize, QEvent.Type.Polish, QEvent.Type.Show):
        h = self.voice_combo.height()
        badge = getattr(self, "pro_badge", None)
        if badge is not None:
            badge.move(max(0, self.voice_combo.width() - 78),
                       (h - 22) // 2)
    return QMainWindow.eventFilter(self, obj, event)


MainWindow.eventFilter = eventFilter
'''
    print("3. eventFilter agregado.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
