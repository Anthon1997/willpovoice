from pathlib import Path
import re

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# cualquier string hardcodeado "v1.2.8" -> dinamico
t2, n = re.subn(r'(["\'])v1\.2\.8\1', 'f"v{APP_VERSION}"', t)
if n:
    t = t2
    print(f"version dinamica x{n}")

if "from app.version import APP_VERSION" not in t:
    t = t.replace("from core import", "from app.version import APP_VERSION\nfrom core import", 1)
    print("import APP_VERSION")

p.write_text(t, encoding="utf-8", newline="\n")
import ast
ast.parse(t)
print("SINTAXIS OK")
