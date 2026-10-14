from PySide6.QtWidgets import QApplication, QWidget
import ui.modern_window as m

app = QApplication([])
print("=== D) LIGHT_MODE:", m.LIGHT_MODE)
print("suspend attr:", hasattr(m, "_LIGHT_SUSPEND"))

w = QWidget()
if m.LIGHT_MODE and hasattr(m, "_LIGHT_SUSPEND"):
    m._LIGHT_SUSPEND = True
    w.setStyleSheet("QFrame { background: #0d1220; color: #e6edf3; }")
    print("E) con suspend  :", w.styleSheet())
    m._LIGHT_SUSPEND = False
w2 = QWidget()
w2.setStyleSheet("QFrame { background: #0d1220; color: #e6edf3; }")
print("F) sin suspend  :", w2.styleSheet())

if hasattr(m, "_translate_light_qss"):
    print("=== G) traductor sobre patrones de planes ===")
    for s in [
        "background: #10f5b301;",
        "background: #f5b30110;",
        "background: #a855f712;",
        "background: rgba(245,179,1,18);",
        "border: 1.5px solid #f5b301;",
        "background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #f5b301, stop:1 #ffdd00);",
    ]:
        print(repr(s), "->", repr(m._translate_light_qss(s)))
