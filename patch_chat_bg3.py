from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

old_hook = '''        try:
            from PySide6.QtCore import QEvent
            if obj is getattr(self, "_chat_page", None) and \\
                    event.type() == QEvent.Type.Resize:
                self._layout_chat_bg()
        except Exception:
            pass
'''

new_hook = '''    try:
        from PySide6.QtCore import QEvent
        if obj is getattr(self, "_chat_page", None) and \\
                event.type() == QEvent.Type.Resize:
            self._layout_chat_bg()
    except Exception:
        pass
'''

if old_hook in t:
    t = t.replace(old_hook, new_hook, 1)
    p.write_text(t, encoding="utf-8", newline="\n")
    ast.parse(t)
    print("OK: indentacion corregida")
else:
    print("AVISO: hook no encontrado tal cual")
