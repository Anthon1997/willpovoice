from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")

old = '''        _old_l.addWidget(_frame)
    except Exception as _exc:
        print("chatFrame:", _exc)'''

new = '''        _old_l.addWidget(_frame)
        _sep = QFrame(_frame)
        _sep.setFixedHeight(1)
        _sep.setStyleSheet(
            "background: rgba(139,117,255,45); border: none;")
        _fl.insertWidget(1, _sep)
    except Exception as _exc:
        print("chatFrame:", _exc)'''

if old in t and "_fl.insertWidget(1, _sep)" not in t:
    t = t.replace(old, new, 1)
    mw.write_text(t, encoding="utf-8", newline="\n")
    ast.parse(t)
    print("OK: separador cabecera/cuerpo agregado")
else:
    print("nada que hacer")
