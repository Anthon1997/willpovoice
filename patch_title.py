from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")
log = []

# 1) Buscar todas las ocurrencias hardcodeadas de la version
for n, ln in enumerate(t.splitlines(), 1):
    if "1.2.8" in ln or "1.2.7" in ln:
        print(f"{n}: {ln.strip()[:110]}")

# 2) Reemplazar setWindowTitle hardcodeado por APP_VERSION
import re
t2, n1 = re.subn(
    r'setWindowTitle\(\s*["\']WillpoVoice v1\.2\.\d["\']\s*\)',
    'setWindowTitle(f"WillpoVoice v{APP_VERSION}")',
    t)
if n1:
    t = t2
    log.append(f"titulo dinamico x{n1}")

# 3) Asegurar import de APP_VERSION en modern_window
if "APP_VERSION" not in t:
    i = t.find("from core")
    if i != -1:
        t = t[:i] + "from app.version import APP_VERSION\n" + t[i:]
        log.append("import version")
elif "from app.version import" not in t and "APP_VERSION" in t:
    i = t.find("import ")
    # buscar zona de imports al inicio
    t = t.replace("from core import", "from app.version import APP_VERSION\nfrom core import", 1)
    log.append("import version injertado")

p.write_text(t, encoding="utf-8", newline="\n")
print("FIX:", log)
try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as ex:
    print("ERROR:", ex.lineno, ex.msg)
