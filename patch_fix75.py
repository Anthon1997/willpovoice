from pathlib import Path
import re

# 1. theme.py y widgets.py: degradado de botones fijo teal->azul
for f in ("ui/theme.py", "ui/widgets.py"):
    p = Path(f)
    t = p.read_text(encoding="utf-8")

    t = t.replace(
        'btn_grad = f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {teal}, stop:1 {accent.name()})"',
        'btn_grad = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4de3b0, stop:1 #4a7dff)"',
    )
    t = t.replace(
        'btn_hover = f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {teal}, stop:1 {hover})"',
        'btn_hover = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #5ff0c0, stop:1 #5a8dff)"',
    )
    p.write_text(t, encoding="utf-8")
    print(f"1. {f}: botones fijos teal->azul.")

# 2. main_window.py: button_style fijo + barra de titulo con color del tema
p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

t = re.sub(
    r"button_style = \([\s\S]*?\n        \)",
    '''button_style = (
            "QPushButton {"
            " background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #4de3b0, stop:1 #4a7dff);"
            " color: white;"
            " border: 1px solid rgba(255,255,255,0.08);"
            " border-radius: 10px;"
            " padding: 8px 18px;"
            " font-size: 13px;"
            " font-weight: 700;"
            " }"
            " QPushButton:hover { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #5ff0c0, stop:1 #5a8dff); border: 1px solid rgba(255,255,255,0.18); }"
            " QPushButton:pressed { background: #3a63d8; }"
            " QPushButton:disabled { background: #1a2236; color: #9aa7bd; border: 1px solid #182238; }"
        )''',
    t,
    count=1,
)
print("2. button_style fijo como foto 2.")

# 3. Metodo para pintar la barra de titulo (Windows 11)
if "_apply_titlebar" not in t:
    t = t.replace(
        "    def on_swatch_clicked(self) -> None:",
        '''    def _apply_titlebar(self) -> None:
        try:
            import ctypes

            dark = self.settings.get("dark_mode", True)
            if dark:
                caption = 0x001C0F0A
                textcol = 0x00FAF2EE
            else:
                caption = 0x00FAF7F5
                textcol = 0x0036221A
            hwnd = int(self.winId())
            dwm = ctypes.windll.dwmapi
            dwm.DwmSetWindowAttribute(
                hwnd, 35, ctypes.byref(ctypes.c_uint32(caption)), 4
            )
            dwm.DwmSetWindowAttribute(
                hwnd, 36, ctypes.byref(ctypes.c_uint32(textcol)), 4
            )
        except Exception:
            pass

    def on_swatch_clicked(self) -> None:''',
        1,
    )
    print("3. Metodo _apply_titlebar agregado.")

# 4. Llamarlo al aplicar tema
if "self._apply_titlebar()" not in t:
    t = t.replace(
        "        self.setStyleSheet(build_qss(accent, dark))",
        "        self.setStyleSheet(build_qss(accent, dark))\n        self._apply_titlebar()",
        1,
    )
    print("4. Barra de titulo sincronizada con el tema.")

p.write_text(t, encoding="utf-8")
print("Listo.")
