from pathlib import Path
p = Path("METODOLOGIA_TRABAJO_IA.txt")
t = p.read_text(encoding="utf-8")
sec = """[6. MODO CLARO - METODOLOGIA DE IMPLEMENTACION]
Mecanismo (v1.3.0): al importar modern_window se lee
QSettings theme; si == "Claro" -> LIGHT_MODE=True y:
  a) Se swappean las constantes de paleta (BG, SIDE_BG,
     CARD, CARD2, BORDER, TEXT, MUTED) a valores claros.
  b) Monkeypatch de QWidget.setStyleSheet: traduce cada
     hex oscuro del mapa _LIGHT_HEX a su par claro ANTES
     de aplicar el stylesheet (cubre ~152 literales sin
     reescribirlos a mano).
  c) El cambio de tema requiere REINICIO (dialogo
     "Reiniciar ahora" -> _restart_app con QProcess).
Para extender/pulir el modo claro:
  1. Agregar pares hex al dict _LIGHT_HEX (orden importa:
     el map de #ffffff va PRIMERO para no doble-traducir).
  2. Capturar pantalla en claro y corregir contrastes.
  3. Lo que NO cubre el monkeypatch (fase 2 manual):
     pixmaps/dibujos QPainter (make_icon usa constantes y
     ya se adapta), fondos con imagen (chat_bg.png,
     portada) y SVGs _chat_svg con hex hardcodeado.
  4. NUNCA tocar los 152 literales del tema oscuro: el
     oscuro sigue siendo el tema por defecto y debe
     quedar intacto.
Regla: todo color nuevo que se agregue a la UI debe usar
las constantes (BG/CARD/TEXT/MUTED...) o entrar tambien
en _LIGHT_HEX, para no romper el modo claro.
"""
if "[6. MODO CLARO" not in t:
    t = t.replace("==============================================================\nFIN - metodologia",
                  sec + "==============================================================\nFIN - metodologia", 1)
    p.write_text(t, encoding="utf-8")
    print("METODOLOGIA: seccion [6] modo claro agregada")
else:
    print("METODOLOGIA: ya tenia la seccion")
