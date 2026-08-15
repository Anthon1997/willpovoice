from pathlib import Path
import ast

p = Path("ui/modern_window.py")
t = p.read_text(encoding="utf-8")

# 1. _avatar_pixmap acepta color de anillo
t = t.replace(
    "def _avatar_pixmap(self, name):",
    "def _avatar_pixmap(self, name, ring=None):",
    1,
)
print("1. _avatar_pixmap con parametro ring.")

# 2. Anillo en la ruta de foto real
old_draw = """                p.drawPixmap(0, 0, sc, x, y, size, size)
                p.end()"""
new_draw = """                p.drawPixmap(0, 0, sc, x, y, size, size)
                if ring:
                    p.setClipping(False)
                    p.setPen(QPen(QColor(ring), 2))
                    p.drawEllipse(1, 1, size - 2, size - 2)
                p.end()"""
if old_draw in t:
    t = t.replace(old_draw, new_draw, 1)
    print("2. Anillo en foto real.")

# 3. Anillo en la ruta de iniciales
old_ini = """        p.drawText(QRect(0, 0, size, size), Qt.AlignmentFlag.AlignCenter, name[:1].upper())
        p.end()"""
new_ini = """        p.drawText(QRect(0, 0, size, size), Qt.AlignmentFlag.AlignCenter, name[:1].upper())
        if ring:
            p.setPen(QPen(QColor(ring), 2))
            p.drawEllipse(1, 1, size - 2, size - 2)
        p.end()"""
if old_ini in t:
    t = t.replace(old_ini, new_ini, 1)
    print("3. Anillo en iniciales.")

# 4. VoiceCard pasa el anillo dorado/gris segun premium
old_pix = "photo.setPixmap(window._avatar_pixmap(name))"
new_pix = ('photo.setPixmap(window._avatar_pixmap(\n'
           '            name, "#f5b301" if premium else "#232f4b"))')
if old_pix in t:
    t = t.replace(old_pix, new_pix, 1)
    print("4. Anillo dorado en Premium, gris en estandar.")

# 5. Subtitulo Premium en dorado: "WillpoVoice Premium"
old_sub = '''    def _voice_subtitle(self, name, premium):
        subs = ["Acento neutro · Profesional", "Acento suave · Natural",
                "Acento cálido · Amigable", "Acento claro · Formal"]
        return subs[len(name) % len(subs)] if premium else "Voz estándar"'''
new_sub = '''    def _voice_subtitle(self, name, premium):
        return "WillpoVoice Premium" if premium else "Voz estándar"'''
if old_sub in t:
    t = t.replace(old_sub, new_sub, 1)
    print("5. Subtitulo WillpoVoice Premium dorado.")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
