from pathlib import Path
import ast

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

old_block = '''        feats = [
            ("wave", "Voces naturales de alta calidad"),
            ("bolt", "Conversiones rapidas e ilimitadas"),
            ("shield", "Soporte prioritario y actualizaciones"),
            ("star", "Nuevas voces todas las semanas"),
        ]
        for kind, txt in feats:
            row = QHBoxLayout()
            row.setSpacing(10)
            row.setContentsMargins(0, 0, 0, 0)
            ic = QLabel()
            ic.setFixedSize(18, 18)
            ic.setPixmap(_lic_pix(kind, "#c9d1d9", 16))
            ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
            row.addWidget(ic, 0, Qt.AlignmentFlag.AlignTop)
            lb = QLabel(txt)
            lb.setStyleSheet(
                f"color: {MUTED}; font-size: 10.5px; padding-top: 1px;")
            lb.setWordWrap(True)
            lb.setMaximumWidth(190)
            row.addWidget(lb)
            row.addStretch()
            pv.addLayout(row)'''

new_block = '''        feats = [
            ("wave", "Voces naturales<br>de alta calidad"),
            ("bolt", "Conversiones rapidas<br>e ilimitadas"),
            ("shield", "Soporte prioritario<br>y actualizaciones"),
            ("star", "Nuevas voces<br>todas las semanas"),
        ]
        for kind, txt in feats:
            row = QHBoxLayout()
            row.setSpacing(12)
            row.setContentsMargins(0, 0, 0, 0)
            ic = QLabel()
            ic.setFixedSize(18, 18)
            ic.setPixmap(_lic_pix(kind, "#d7dde7", 16))
            ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
            row.addWidget(ic)
            lb = QLabel(txt)
            lb.setStyleSheet("color: #c9d1d9; font-size: 11px;")
            row.addWidget(lb)
            row.addStretch()
            pv.addLayout(row)'''

if old_block in t:
    t = t.replace(old_block, new_block, 1)
    print("Filas Premium alineadas al mockup.")
else:
    print("AVISO: bloque de filas no encontrado.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
