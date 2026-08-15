from pathlib import Path
import ast

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

old = "\n@staticmethod\n    def _split_chunks(text, limit=600):"
new = "\n    @staticmethod\n    def _split_chunks(text, limit=600):"
if old in t:
    t = t.replace(old, new, 1)
    print("Decorator @staticmethod re-indentado dentro de ExportWorker.")
else:
    print("AVISO: patron no encontrado.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("main_window SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
