from pathlib import Path
import ast

mw = Path("ui/modern_window.py")
t = mw.read_text(encoding="utf-8")
n = 0

repl = [
    # Layout principal
    ("v.setContentsMargins(28, 24, 28, 22)\n        v.setSpacing(12)",
     "v.setContentsMargins(22, 14, 22, 14)\n        v.setSpacing(8)"),
    ('make_icon("crown", "#f5b544", 42)', 'make_icon("crown", "#f5b544", 32)'),
    ('"color: #ffffff; font-size: 24px; font-weight: 800;")',
     '"color: #ffffff; font-size: 20px; font-weight: 800;")'),
    ('t2.setStyleSheet("color: #9aa4c0; font-size: 12px;")',
     't2.setStyleSheet("color: #9aa4c0; font-size: 11px;")'),
    ("        v.addSpacing(8)", "        v.addSpacing(4)"),
    ("        v.addSpacing(4)\n        foot", "        v.addSpacing(2)\n        foot"),
    # Cards
    ("cv.setContentsMargins(18, 16, 18, 16)\n        cv.setSpacing(10)",
     "cv.setContentsMargins(14, 12, 14, 12)\n        cv.setSpacing(6)"),
    ("top.addWidget(_HexIcon(pix, color, 52))",
     "top.addWidget(_HexIcon(pix, color, 44))"),
    ('"color: #ffffff; font-size: 16px; font-weight: 800;")',
     '"color: #ffffff; font-size: 14px; font-weight: 800;")'),
    ('" border-radius: 14px; padding: 5px 14px;"',
     '" border-radius: 12px; padding: 4px 12px;"'),
    ('" font-size: 13px; font-weight: 800;"',
     '" font-size: 12px; font-weight: 800;"'),
    ('fl.setStyleSheet("color: #c9d1d9; font-size: 11.5px;")',
     'fl.setStyleSheet("color: #c9d1d9; font-size: 10.5px;")'),
    ("_chat_svg(self._CHECK, color, 14)", "_chat_svg(self._CHECK, color, 12)"),
    ("b.setFixedHeight(42 if solid else 40)",
     "b.setFixedHeight(36 if solid else 32)"),
    ('" border-radius: 10px; padding: 3px 10px;"',
     '" border-radius: 9px; padding: 2px 8px;"'),
    ('" font-size: 10px; font-weight: 700;"',
     '" font-size: 9px; font-weight: 700;"'),
    # Footer
    ("fv.setContentsMargins(16, 12, 16, 12)\n        fv.setSpacing(14)",
     "fv.setContentsMargins(14, 8, 14, 8)\n        fv.setSpacing(10)"),
    ("_chat_svg(path, color, 20)", "_chat_svg(path, color, 16)"),
    ('"color: #e6edf3; font-size: 11.5px; font-weight: 700;")',
     '"color: #e6edf3; font-size: 10.5px; font-weight: 700;")'),
    ('b.setStyleSheet("color: #7d8590; font-size: 10px;")',
     'b.setStyleSheet("color: #7d8590; font-size: 9px;")'),
]

for old, new in repl:
    if old in t:
        t = t.replace(old, new, 1)
        n += 1

mw.write_text(t, encoding="utf-8", newline="\n")
ast.parse(t)
print(f"OK: {n}/{len(repl)} ajustes compactos aplicados")
