from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")

old = '''            if hasattr(target, "setPlainText"):
                cur = target.toPlainText()
                target.setPlainText(
                    (cur.rstrip() + "\\n\\n" + txt) if cur.strip() else txt)
            else:
                cur = target.text()
                target.setText((cur + " " + txt) if cur.strip() else txt)'''

new = '''            if hasattr(target, "setPlainText"):
                target.setPlainText(txt)
            else:
                target.setText(txt)'''

if old in t:
    t = t.replace(old, new, 1)
    mw.write_text(t, encoding="utf-8", newline="\n")
    ast.parse(t)
    print("OK: Agregar a conversion ahora REEMPLAZA el texto")
else:
    print("AVISO: bloque no encontrado")
