from pathlib import Path
import re

p = Path("ui/main_window.py")
t = p.read_text(encoding="utf-8")

# 1. Recomendadas dorado en el combo de voces
t = t.replace(
    '"MULTILINGUAL - hablan cualquier idioma, ultra realistas"',
    '"Recomendadas - WillpoVoice Premium"',
)
t = t.replace('"multi": "#ff6a00",', '"multi": "#ffd75e",')

# 2. Fondos de grupos al estilo navy
t = t.replace('hot_color = QColor("#4a2c10")', 'hot_color = QColor("#2a2410")')
t = t.replace('"es": QColor("#123524"),', '"es": QColor("#101c33"),')
t = t.replace('"desktop": QColor("#1d2f45"),', '"desktop": QColor("#131a2b"),')
t = t.replace('"en": QColor("#2b2b33"),', '"en": QColor("#131a2b"),')
t = t.replace('hot_color = QColor("#ffe3c2")', 'hot_color = QColor("#fff6d8")')
t = t.replace('"es": QColor("#d7f0e0"),', '"es": QColor("#e8f0ff"),')
t = t.replace('"desktop": QColor("#dbe7f5"),', '"desktop": QColor("#eef1f6"),')
t = t.replace('"en": QColor("#e8e8ee"),', '"en": QColor("#eef1f6"),')

# 3. Menus al estilo navy
t = t.replace("#0e3a46", "#131a2b")
t = t.replace("#1f4a55", "#232f4b")
t = t.replace("#1f5a68", "#232f4b")
t = t.replace("#1596a8", "#1a2236")
t = t.replace("#eaf7f4", "#eef2fa")

# 4. Barra de progreso shine al estilo navy
t = t.replace('QColor("#0d222b")', 'QColor("#1a2236")')
t = t.replace('QColor("#1780a8")', 'QColor("#4a7dff")')

# 5. Botones con degradado teal->azul
t = re.sub(
    r"button_style = \([\s\S]*?\n        \)",
    '''button_style = (
            "QPushButton {"
            " background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #4de3b0, stop:1 #4a7dff);"
            " color: white;"
            " border: none;"
            " border-radius: 12px;"
            " padding: 8px 18px;"
            " font-size: 13px;"
            " font-weight: 700;"
            " }"
            " QPushButton:hover { background: #5a8dff; }"
            " QPushButton:pressed { background: #3a63d8; }"
            " QPushButton:disabled { background: #1a2236; color: #9aa7bd; }"
        )''',
    t,
    count=1,
)

# 6. Grupos navy con titulo teal
t = re.sub(
    r"if dark:\n\s*group_bg = QColor\.fromHsl\([\s\S]*?window_bg = \"#f5f6fa\"",
    '''if dark:
            group_bg = "#131a2b"
            group_border = "#232f4b"
            window_bg = "#0a0f1c"
        else:
            group_bg = "#ffffff"
            group_border = "#dfe4ee"
            window_bg = "#f5f7fa"''',
    t,
    count=1,
)

t = re.sub(
    r"group_style = \([\s\S]*?\n        \)",
    '''title_color = "#4de3b0" if dark else "#0fa87a"
        group_style = (
            "QGroupBox {"
            f" background-color: {group_bg};"
            f" border: 1px solid {group_border};"
            " border-radius: 14px;"
            " margin-top: 16px;"
            " padding: 16px 10px 10px 10px;"
            " }"
            " QGroupBox::title {"
            " subcontrol-origin: margin;"
            " subcontrol-position: top left;"
            " left: 14px;"
            " padding: 2px 10px;"
            " font-weight: 700;"
            f" color: {title_color};"
            f" background-color: {window_bg};"
            " border-radius: 6px;"
            " }"
        )''',
    t,
    count=1,
)

# 7. Buscador de voces
if "voice_search" not in t:
    t = t.replace(
        "self.voice_combo = QComboBox()",
        "self.voice_combo = QComboBox()\n"
        "        self.voice_search = QLineEdit()\n"
        '        self.voice_search.setPlaceholderText("Buscar voces...")\n'
        "        self.voice_search.textChanged.connect(self._filter_voices)",
        1,
    )
    t = t.replace(
        "voice_layout.addWidget(self.voice_combo, 1)",
        "voice_layout.addWidget(self.voice_combo, 1)\n"
        "        voice_layout.addWidget(self.voice_search, 1)",
        1,
    )
    t = t.replace(
        "    def refresh_voices(self) -> None:",
        "    def _filter_voices(self, text: str) -> None:\n"
        "        q = text.strip().lower()\n"
        "        view = self.voice_combo.view()\n"
        "        model = self.voice_combo.model()\n"
        "        for i in range(self.voice_combo.count()):\n"
        "            is_header = not model.item(i).isEnabled()\n"
        "            label = self.voice_combo.itemText(i).lower()\n"
        "            view.setRowHidden(i, bool(q) and not is_header and q not in label)\n"
        "\n"
        "    def refresh_voices(self) -> None:",
        1,
    )
    print("7. Buscador de voces agregado.")

p.write_text(t, encoding="utf-8")
print("main_window.py actualizado al estilo movil.")
