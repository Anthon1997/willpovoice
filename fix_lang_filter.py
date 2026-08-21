from pathlib import Path

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# Cambiar setCurrentIndex(0) → setCurrentIndex(3) en la zona del lang_combo
old = 'self.lang_combo.setCurrentIndex(0)\n    self.lang_combo.setStyleSheet(combo_qss)'
new = 'self.lang_combo.setCurrentIndex(3)\n    self.lang_combo.setStyleSheet(combo_qss)'

if old in t:
    t = t.replace(old, new, 1)
    p.write_text(t, encoding="utf-8", newline="\n")
    print("FIX aplicado: lang_combo por defecto = Todos")
else:
    print("ADVERTENCIA: patrón no encontrado, revisar manualmente")
    print("Línea objetivo: self.lang_combo.setCurrentIndex(0)")
