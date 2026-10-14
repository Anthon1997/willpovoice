from pathlib import Path
import re
src = Path("ui/modern_window.py").read_text(encoding="utf-8")
print("LIGHT_MODE bloque diferido:", "LIGHT_MODE = _light_theme_enabled()" in src)
print("show envuelto:", "MainWindow.show = _show_shadow" in src)
print("findChild playerBar:", 'findChild(QFrame, "playerBar")' in src)
print("QFrame importado:", re.search(r"import.*QFrame|QFrame", src) is not None)
i = src.find("def _show_shadow")
print("\n--- bloque _show_shadow ---")
print(src[i-200:i+700] if i >= 0 else "NO ENCONTRADO")
