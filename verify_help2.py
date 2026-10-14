from pathlib import Path
import ast
src = Path("ui/modern_window.py").read_text(encoding="utf-8")
print("estilizado presente:", "mb.setIcon(QMessageBox.Icon.Information)" in src)
i = src.find("def show_help(self):")
print(src[i:i+420])
