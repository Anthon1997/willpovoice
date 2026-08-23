from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")

old = '''    try:
        for _i in range(self.lang_combo.count()):
            if self.lang_combo.itemText(_i).startswith("Multiling"):
                self.lang_combo.setCurrentIndex(_i)
                break
        self._on_lang_changed()
    except Exception:
        pass'''

new = '''    def _apply_default_lang(_timer=None):
        try:
            for _i in range(self.lang_combo.count()):
                if self.lang_combo.itemText(_i).startswith("Multiling"):
                    self.lang_combo.setCurrentIndex(_i)
                    break
            self._on_lang_changed()
        except Exception:
            pass
    QTimer.singleShot(700, _apply_default_lang)'''

if old in t:
    t = t.replace(old, new, 1)
    mw.write_text(t, encoding="utf-8", newline="\n")
    ast.parse(t)
    print("OK: default multilingue diferido (700ms)")
else:
    print("AVISO: bloque anterior no encontrado")
