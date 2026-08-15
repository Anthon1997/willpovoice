from pathlib import Path
import re, ast

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

# 1. Boton estilo hamburguesa con icono de voces dibujado
old_block = re.search(
    r"self\.voices_button = QPushButton\([\s\S]*?"
    r"QPushButton:hover \{ background: #1a2236; \}\n        \)",
    t,
)
if old_block:
    new_block = '''self.voices_button = QPushButton()
        self.voices_button.setFixedSize(44, 44)
        self.voices_button.setToolTip("Voces")
        self.voices_button.setIcon(QIcon(self._voices_icon_pixmap()))
        self.voices_button.setIconSize(QSize(24, 24))
        self.header_widget.layout().addWidget(
            self.voices_button, 0, Qt.AlignmentFlag.AlignVCenter
        )
        self.voices_button.setStyleSheet(
            "QPushButton { background: rgba(19, 26, 43, 0.85); "
            "border: 1px solid #232f4b; border-radius: 12px; }"
            "QPushButton:hover { border: 1px solid #ffd75e; }"
        )'''
    t = t[: old_block.start()] + new_block + t[old_block.end() :]
    print("1. Boton hamburguesa con icono de voces.")
else:
    print("1. AVISO: bloque del boton no encontrado.")

# 2. Metodo que dibuja el icono (persona + ondas de voz)
if "_voices_icon_pixmap" not in t:
    t = t.replace(
        "    def _build_ui(self) -> None:",
        '''    def _voices_icon_pixmap(self) -> QPixmap:
        pix = QPixmap(24, 24)
        pix.fill(Qt.GlobalColor.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = QColor("#ffd75e")
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(color)
        p.drawEllipse(5, 4, 7, 7)
        body = QPainterPath()
        body.addRoundedRect(2, 13, 13, 8, 4, 4)
        p.drawPath(body)
        p.setBrush(Qt.GlobalColor.transparent)
        p.setPen(QPen(color, 1.8))
        p.drawArc(QRect(14, 7, 8, 8), -50 * 16, 100 * 16)
        p.drawArc(QRect(15, 4, 9, 9), -50 * 16, 100 * 16)
        p.end()
        return pix

    def _build_ui(self) -> None:''',
        1,
    )
    print("2. Icono de voces dibujado (persona + ondas).")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(p.read_text(encoding="utf-8"))
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
