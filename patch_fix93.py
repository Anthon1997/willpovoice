from pathlib import Path
import ast

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

# 1. Boton sin texto (el icono lo define _apply_style)
if 'self.plus_btn = QPushButton("+")' in t:
    t = t.replace('self.plus_btn = QPushButton("+")', "self.plus_btn = QPushButton()", 1)
    print("1. plus_btn sin texto.")

# 2. Iconos dibujados en lugar de texto
if 'self.plus_btn.setText("✓")' in t:
    t = t.replace(
        'self.plus_btn.setText("✓")',
        "self.plus_btn.setIcon(self._check_icon())\n"
        "            self.plus_btn.setIconSize(QSize(16, 16))",
        1,
    )
    print("2. Check dibujado al seleccionar.")

if 'self.plus_btn.setText("+")' in t:
    t = t.replace(
        'self.plus_btn.setText("+")',
        "self.plus_btn.setIcon(self._plus_icon())\n"
        "            self.plus_btn.setIconSize(QSize(16, 16))",
        1,
    )
    print("3. Mas dibujado por defecto.")

# 3. Metodos que dibujan los iconos
if "def _plus_icon" not in t:
    t = t.replace(
        "    def _apply_style(self):",
        '''    def _plus_icon(self) -> QIcon:
        pix = QPixmap(16, 16)
        pix.fill(Qt.GlobalColor.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(
            QPen(
                QColor("#ffffff"),
                2.6,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
            )
        )
        p.drawLine(3, 8, 13, 8)
        p.drawLine(8, 3, 8, 13)
        p.end()
        return QIcon(pix)

    def _check_icon(self) -> QIcon:
        pix = QPixmap(16, 16)
        pix.fill(Qt.GlobalColor.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(
            QPen(
                QColor("#ffffff"),
                2.6,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin,
            )
        )
        p.drawPolyline(QPolygon([QPoint(3, 8), QPoint(6, 12), QPoint(13, 4)]))
        p.end()
        return QIcon(pix)

    def _apply_style(self):''',
        1,
    )
    print("4. Metodos _plus_icon y _check_icon agregados.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(p.read_text(encoding="utf-8"))
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
