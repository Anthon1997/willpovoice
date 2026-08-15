from pathlib import Path
import re

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

# 1. Botones con textura (borde sutil + degradado)
t = re.sub(
    r"button_style = \([\s\S]*?\n        \)",
    '''teal_btn = "#4de3b0" if dark else "#0fa87a"
        button_style = (
            "QPushButton {"
            f" background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {teal_btn}, stop:1 {accent_color.name()});"
            " color: white;"
            " border: 1px solid rgba(255,255,255,0.08);"
            " border-radius: 10px;"
            " padding: 9px 18px;"
            " font-size: 13px;"
            " font-weight: 700;"
            " }"
            f" QPushButton:hover {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {teal_btn}, stop:1 {hover}); border: 1px solid rgba(255,255,255,0.18); }}"
            f" QPushButton:pressed {{ background: {pressed}; }}"
            " QPushButton:disabled { background: #101a30; color: #8fa0bd; border: 1px solid #182238; }"
        )''',
    t,
    count=1,
)
print("1. Botones con textura.")

# 2. Grupos con degradado sutil
t = re.sub(
    r"if dark:\n\s*group_bg = [\s\S]*?window_bg = \"#f5f7fa\"",
    '''if dark:
            group_top = "#161f36"
            group_bottom = "#111828"
            group_border = "#182238"
        else:
            group_top = "#ffffff"
            group_bottom = "#f2f5fa"
            group_border = "#e2e8f2"''',
    t,
    count=1,
)

t = re.sub(
    r"group_style = \([\s\S]*?\n        \)",
    '''group_style = (
            "QGroupBox {"
            f" background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 {group_top}, stop:1 {group_bottom});"
            f" border: 1px solid {group_border};"
            " border-radius: 14px;"
            " margin-top: 18px;"
            " padding: 18px 12px 12px 12px;"
            " }"
            " QGroupBox::title {"
            " subcontrol-origin: margin;"
            " subcontrol-position: top left;"
            " left: 16px;"
            " padding: 0px 6px;"
            " font-weight: 700;"
            f" color: {title_color};"
            " background: transparent;"
            " }"
        )''',
    t,
    count=1,
)
print("2. Grupos con textura.")

# 3. Barra de progreso shine navy
t = t.replace('QColor("#0d222b")', 'QColor("#0d1526")')
t = t.replace('QColor("#1780a8")', 'QColor("#4a7dff")')

# 4. Menus con textura
t = t.replace("#0e3a46", "#111828")
t = t.replace("#1f4a55", "#20304f")
t = t.replace("border-radius: 6px; padding: 0px; }", "border-radius: 12px; padding: 6px; }")
t = t.replace("#1f5a68", "#182238")
t = t.replace("#1596a8", "#1c2a4a")
t = t.replace("#eaf7f4", "#eef2fa")
print("3. Menus y shine con textura.")

p.write_text(t, encoding="utf-8")
print("main_window con textura profesional.")
