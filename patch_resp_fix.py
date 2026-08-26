from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")

# Delimitar la región corrupta: desde "def _on_chat_response"
# hasta el siguiente "def _layout_chat_bg"
s = t.find("def _on_chat_response(self, response, temp_bubble):")
e = t.find("def _layout_chat_bg(self):")
if s == -1 or e == -1:
    raise SystemExit("ERROR: region _on_chat_response no encontrada")

clean_fn = '''def _on_chat_response(self, response, temp_bubble):
    if temp_bubble is not None:
        try:
            temp_bubble.setParent(None)
            temp_bubble.deleteLater()
        except Exception:
            pass
    self._add_chat_bubble(response, is_user=False)
    if hasattr(self, "_chat_history"):
        self._chat_history.append(
            {"role": "assistant", "content": response})
    self._show_chat_chips()


'''

t = t[:s] + clean_fn + t[e:]
mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
print("OK: _on_chat_response reescrita y limpia")

# Verificar que no quedaron try/except colgados en esa zona
region = t[s:s+len(clean_fn)+100]
if "except Exception as exc:" in region and "try:" not in region:
    print("WARN: except huerfano todavia detectado")
else:
    print("OK: sin bloques try/except huerfanos")
