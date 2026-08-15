from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

old = """def make_icon(kind, color, size=20):
    pix = QPixmap(size, size)"""
new = """def make_icon(kind, color, size=20):
    try:
        _base = Path(getattr(sys, "_MEIPASS",
                             Path(__file__).resolve().parents[1]))
        _svg = _base / "assets" / "icons" / "svg" / f"{kind}.svg"
        if _svg.exists():
            from PySide6.QtSvg import QSvgRenderer
            from PySide6.QtCore import QByteArray
            _data = _svg.read_text(encoding="utf-8")
            _data = _data.replace("currentColor", color)
            if kind == "heart_fill":
                _data = _data.replace('fill="none"',
                                      f'fill="{color}"')
            _r = QSvgRenderer(QByteArray(_data.encode("utf-8")))
            if _r.isValid():
                pix = QPixmap(size, size)
                pix.fill(Qt.GlobalColor.transparent)
                _p = QPainter(pix)
                _r.render(_p)
                _p.end()
                return pix
    except Exception:
        pass
    pix = QPixmap(size, size)"""
if old in t:
    t = t.replace(old, new, 1)
    p.write_text(t, encoding="utf-8")
    print("make_icon ahora renderiza SVG vectorial (con fallback).")
else:
    print("AVISO: ancla make_icon no encontrada.")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
