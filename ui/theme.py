from PySide6.QtGui import QColor

PRESET_COLORS = [
    "#001F3F",
    "#0E639C",
    "#00B4D8",
    "#2A9D8F",
    "#7B2CBF",
    "#E63946",
    "#F77F00",
    "#FF4D6D",
]


def build_qss(accent_hex: str, dark: bool) -> str:
    accent = QColor(accent_hex)

    if not accent.isValid():
        accent = QColor("#0E639C")

    hue = accent.hslHue()

    if hue < 0:
        hue = 0

    sat = min(accent.hslSaturation(), 150)

    hover = accent.lighter(125).name()
    pressed = accent.darker(125).name()
    grad_top = accent.lighter(115).name()
    grad_bottom = accent.darker(115).name()

    if dark:
        bg = QColor.fromHsl(hue, sat, 30).name()
        panel = QColor.fromHsl(hue, sat, 38).name()
        border = QColor.fromHsl(hue, sat, 52).name()
        text = "#e8e8e8"
        muted = "#a8b0c0"
        group_border = border
    else:
        bg = "#f5f6fa"
        panel = "#ffffff"
        border = "#c8cdd8"
        text = "#1a1a2e"
        muted = "#5a6070"
        group_border = pressed

    return f"""
QMainWindow, QWidget {{
    background-color: {bg};
    color: {text};
    font-family: "Segoe UI", "Arial", sans-serif;
    font-size: 13px;
}}

QPlainTextEdit {{
    background-color: {panel};
    color: {text};
    border: 1px solid {border};
    border-radius: 6px;
}}

QPlainTextEdit:focus {{
    border: 1px solid {accent};
}}

QComboBox {{
    background-color: {panel};
    color: {text};
    border: 2px solid {border};
    border-radius: 8px;
    padding: 6px 10px;
    min-height: 26px;
    font-weight: 600;
}}

QComboBox:hover {{
    border-color: {hover};
}}

QComboBox:focus {{
    border-color: {accent};
}}

QGroupBox {{
    background-color: {panel};
    border: 2px solid {group_border};
    border-radius: 10px;
    margin-top: 14px;
    padding: 14px 8px 8px 8px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 2px 8px;
    color: {pressed};
    background-color: {bg};
    border-radius: 4px;
    font-weight: 700;
}}

QComboBox QAbstractItemView {{
    background-color: {panel};
    color: {text};
}}

QPushButton {{
    background-color: {accent};
    color: white;
    border: 1px solid {pressed};
    border-radius: 10px;
    padding: 8px 18px;
    font-size: 13px;
    font-weight: 600;
}}

QPushButton:hover {{
    background-color: {hover};
    border: 1px solid {hover};
}}

QPushButton:pressed {{
    background-color: {pressed};
}}

QSlider::groove:horizontal {{
    background: {border};
    height: 6px;
    border-radius: 3px;
}}

QSlider::handle:horizontal {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {grad_top}, stop:1 {grad_bottom});
    width: 14px;
    margin: -5px 0;
    border-radius: 7px;
    border: 1px solid {accent};
}}

QLabel {{
    color: {text};
}}

QStatusBar {{
    background-color: {bg};
    color: {muted};
}}
"""






