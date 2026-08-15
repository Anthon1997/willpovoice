from PySide6.QtGui import QColor

PRESET_COLORS = [
    "#4a7dff",
    "#4de3b0",
    "#ffd75e",
    "#7b5cff",
    "#ff4d6d",
    "#00b4d8",
    "#f77f00",
    "#e63946",
]


def build_qss(accent_hex: str, dark: bool) -> str:
    accent = QColor(accent_hex)

    if not accent.isValid():
        accent = QColor("#4a7dff")

    hover = accent.lighter(118).name()
    pressed = accent.darker(125).name()
    teal = "#4de3b0" if dark else "#0fa87a"

    if dark:
        bg_top = "#0c1222"
        bg_bottom = "#090e19"
        panel_top = "#161f36"
        panel_bottom = "#111828"
        inner_top = "#101a30"
        inner_bottom = "#0d1526"
        border = "#20304f"
        border_soft = "#182238"
        item_sel = "#1c2a4a"
        text = "#eef2fa"
        muted = "#8fa0bd"
    else:
        bg_top = "#f7f9fc"
        bg_bottom = "#eef1f6"
        panel_top = "#ffffff"
        panel_bottom = "#f2f5fa"
        inner_top = "#f4f7fb"
        inner_bottom = "#eaeef5"
        border = "#d5dcea"
        border_soft = "#e2e8f2"
        item_sel = "#e3ebff"
        text = "#1a2236"
        muted = "#5a6784"

    bg_grad = f"qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {bg_top}, stop:1 {bg_bottom})"
    panel_grad = f"qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {panel_top}, stop:1 {panel_bottom})"
    inner_grad = f"qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {inner_top}, stop:1 {inner_bottom})"
    btn_grad = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4de3b0, stop:1 #4a7dff)"
    btn_hover = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #5ff0c0, stop:1 #5a8dff)"

    return f"""
QMainWindow, QWidget {{
    background: {bg_grad};
    color: {text};
    font-family: "Segoe UI", "Arial", sans-serif;
    font-size: 13px;
}}

QLabel {{
    color: {text};
    background: transparent;
}}

QPlainTextEdit {{
    background: {inner_grad};
    color: {text};
    border: 1px solid {border};
    border-radius: 12px;
    padding: 10px 12px;
    selection-background-color: {accent.name()};
}}

QPlainTextEdit:focus {{
    border: 1px solid {accent.name()};
}}

QLineEdit {{
    background: {inner_grad};
    color: {text};
    border: 1px solid {border};
    border-radius: 10px;
    padding: 7px 12px;
    min-height: 28px;
}}

QLineEdit:focus {{
    border: 1px solid {accent.name()};
}}

QComboBox {{
    background: {inner_grad};
    color: {text};
    border: 1px solid {border};
    border-radius: 10px;
    padding: 7px 12px;
    min-height: 28px;
    font-weight: 600;
}}

QComboBox:hover {{
    border: 1px solid {accent.name()};
}}

QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: center right;
    border: none;
    width: 28px;
}}

QComboBox QAbstractItemView {{
    background: {panel_grad};
    color: {text};
    border: 1px solid {border};
    border-radius: 10px;
    padding: 6px;
    outline: none;
}}

QComboBox QAbstractItemView::item {{
    padding: 8px 10px;
    min-height: 26px;
    border-radius: 8px;
}}

QComboBox QAbstractItemView::item:selected {{
    background: {item_sel};
    color: {text};
}}

QGroupBox {{
    background: {panel_grad};
    border: 1px solid {border_soft};
    border-radius: 14px;
    margin-top: 18px;
    padding: 18px 12px 12px 12px;
    font-weight: 600;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 16px;
    padding: 0px 6px;
    color: {teal};
    background: transparent;
    font-weight: 700;
}}

QPushButton {{
    background: {btn_grad};
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    padding: 9px 18px;
    font-size: 13px;
    font-weight: 700;
}}

QPushButton:hover {{
    background: {btn_hover};
    border: 1px solid rgba(255, 255, 255, 0.18);
}}

QPushButton:pressed {{
    background: {pressed};
}}

QPushButton:disabled {{
    background: {inner_grad};
    color: {muted};
    border: 1px solid {border_soft};
}}

QSlider::groove:horizontal {{
    background: {inner_grad};
    height: 5px;
    border-radius: 3px;
    border: 1px solid {border_soft};
}}

QSlider::sub-page:horizontal {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {teal}, stop:1 {accent.name()});
    border-radius: 3px;
}}

QSlider::handle:horizontal {{
    background: {accent.name()};
    border: 2px solid {bg_bottom};
    width: 14px;
    height: 14px;
    margin: -6px 0;
    border-radius: 8px;
}}

QSlider::handle:horizontal:hover {{
    background: {hover};
}}

QProgressBar {{
    background: {inner_grad};
    border: 1px solid {border_soft};
    border-radius: 6px;
    height: 10px;
    color: transparent;
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {teal}, stop:1 {accent.name()});
    border-radius: 6px;
}}

QMenu {{
    background: {panel_grad};
    color: {text};
    border: 1px solid {border};
    border-radius: 12px;
    padding: 6px;
}}

QMenu::item {{
    padding: 8px 26px;
    border-radius: 8px;
    margin: 2px 4px;
}}

QMenu::item:selected {{
    background: {item_sel};
    color: {text};
}}

QMenu::separator {{
    height: 1px;
    background: {border_soft};
    margin: 4px 8px;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 8px;
}}

QScrollBar::handle:vertical {{
    background: {border};
    border-radius: 4px;
    min-height: 40px;
}}

QScrollBar::handle:vertical:hover {{
    background: {accent.name()};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 8px;
}}

QScrollBar::handle:horizontal {{
    background: {border};
    border-radius: 4px;
    min-width: 40px;
}}

QStatusBar {{
    background: transparent;
    color: {muted};
    border-top: 1px solid {border_soft};
}}

QToolTip {{
    background: {panel_bottom};
    color: {text};
    border: 1px solid {border};
    border-radius: 8px;
    padding: 6px 10px;
}}
"""
