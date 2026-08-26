from pathlib import Path
import ast
import builtins

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")
log = []

# 1) _chat_svg al final del modulo (si falta)
svg_fn = '''def _chat_svg(path_data, color, size):
    """Renderiza un path SVG Material como QPixmap."""
    from PySide6.QtSvg import QSvgRenderer
    from PySide6.QtCore import QByteArray
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
           'fill="' + color + '"><path d="' + path_data + '"/></svg>')
    r = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    r.render(p)
    p.end()
    return pm
'''
if not any(l.startswith("def _chat_svg(") for l in t.splitlines()):
    t = t.rstrip("\n") + "\n\n" + svg_fn + "\n"
    log.append("_chat_svg agregado")

mw.write_text(t, encoding="utf-8", newline="\n")
tree = ast.parse(t)

# 2) Escaner de nombres huerfanos a nivel modulo
defined = set(dir(builtins))
for node in tree.body:
    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
        defined.add(node.name)
    elif isinstance(node, ast.Assign):
        for tg in node.targets:
            if isinstance(tg, ast.Name):
                defined.add(tg.id)
    elif isinstance(node, (ast.Import, ast.ImportFrom)):
        for al in node.names:
            defined.add(al.asname or al.name.split(".")[0])

missing_names = set()
for node in tree.body:
    if isinstance(node, ast.FunctionDef):
        local = set()
        for a in node.args.args + node.args.kwonlyargs:
            local.add(a.arg)
        for sub in ast.walk(node):
            if isinstance(sub, ast.Assign):
                for tg in sub.targets:
                    if isinstance(tg, ast.Name):
                        local.add(tg.id)
            elif isinstance(sub, (ast.FunctionDef, ast.ClassDef, ast.Lambda)):
                if isinstance(sub, ast.Lambda):
                    for a in sub.args.args:
                        local.add(a.arg)
                else:
                    local.add(sub.name)
            elif isinstance(sub, (ast.Import, ast.ImportFrom)):
                for al in sub.names:
                    local.add(al.asname or al.name.split(".")[0])
            elif isinstance(sub, ast.ExceptHandler) and sub.name:
                local.add(sub.name)
            elif isinstance(sub, ast.For):
                if isinstance(sub.target, ast.Name):
                    local.add(sub.target.id)
        for sub in ast.walk(node):
            if isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Load):
                if sub.id not in defined and sub.id not in local:
                    missing_names.add(sub.id)

print("log:", log)
print("huerfanos:", sorted(missing_names))
