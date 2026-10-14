from PySide6.QtGui import QImage
from PySide6.QtCore import Qt
img = QImage("player_parent.png")
print("size:", img.width(), img.height())
# la barra ocupa el ancho; busco la fila blanca (barra) y muestreo debajo
w, h = img.width(), img.height()
def px(x, y):
    c = img.pixelColor(x, y)
    return (c.red(), c.green(), c.blue(), c.alpha())
# encontrar fila de la barra: blanco ~ (255,255,255)
bar_y = None
for y in range(h-1, -1, -1):
    c = px(w//2, y)
    if c[0] > 245 and c[1] > 245 and c[2] > 245:
        bar_y = y
        break
print("bar bottom y:", bar_y)
if bar_y:
    top = max(0, bar_y-70)
    for y in range(top, min(h, bar_y+30), 6):
        print(y, px(w//2, y), px(40, y), px(w-40, y))
