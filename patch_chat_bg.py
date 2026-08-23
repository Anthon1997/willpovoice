from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

old = '''        if not getattr(self, "_chat_bg_pix", None):
            pm = QPixmap(1400, 900)
            pm.fill(Qt.GlobalColor.transparent)
            pr = QPainter(pm)
            pr.setOpacity(0.28)
            sp = base / "assets" / "banner.svg"
            if sp.exists():
                QSvgRenderer(str(sp)).render(pr)
            pr.end()
            self._chat_bg_pix = pm'''

new = '''        if not getattr(self, "_chat_bg_pix", None):
            pm = QPixmap(1400, 900)
            pm.fill(Qt.GlobalColor.transparent)
            pr = QPainter(pm)
            pr.setOpacity(0.30)
            sp_png = base / "assets" / "icons" / "chat_bg.png"
            sp_svg = base / "assets" / "banner.svg"
            if sp_png.exists():
                src = QPixmap(str(sp_png))
                scaled = src.scaled(
                    1400, 900,
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation)
                pr.drawPixmap((1400 - scaled.width()) // 2,
                              (900 - scaled.height()) // 2, scaled)
            elif sp_svg.exists():
                QSvgRenderer(str(sp_svg)).render(pr)
            pr.end()
            self._chat_bg_pix = pm'''

if old in t:
    t = t.replace(old, new, 1)
    p.write_text(t, encoding="utf-8", newline="\n")
    ast.parse(t)
    print("OK: fondo chat_bg.png prioritario")
else:
    print("AVISO: bloque no encontrado")
