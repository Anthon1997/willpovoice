from pathlib import Path
import re

path = Path("ui") / "main_window.py"
text = path.read_text(encoding="utf-8")

text = text.replace('"Guardar WAV"', '"Exportar"')

wizard_class = '''class HelpWizard(QDialog):
    STEPS = [
        ("Bienvenido a WillpoVoice", "Esta guia te ensena paso a paso como convertir texto en voz con las 321 voces disponibles."),
        ("1. Elige una voz", "En el desplegable superior selecciona la voz que quieras: las MULTILINGUAL hablan cualquier idioma, las de Espanol y las estandar que funcionan sin internet."),
        ("2. Escribe tu texto", "En el cuadro central escribe o pega el texto que quieres escuchar. Tambien puedes pulsar 'Abrir TXT' para cargar un archivo de texto completo."),
        ("3. Ajusta velocidad y volumen", "Con las barras inferiores controlas que tan rapido habla la voz y que tan fuerte suena."),
        ("4. Pulsa Reproducir", "Se abrira una ventana con una barra de carga mientras la voz prepara, y luego comenzara a hablar con el espectro animado."),
        ("5. Detener", "Si quieres interrumpir la reproduccion, pulsa el boton Detener de la barra inferior o el de la ventana emergente."),
        ("6. Exportar", "Pulsa 'Exportar' para guardar el audio de tu texto en un archivo WAV y usarlo donde quieras."),
        ("7. Historial y personalizacion", "Tus ultimos textos quedan guardados en el Historial. Con la paleta de colores y 'Modo claro' personalizas la apariencia a tu gusto."),
        ("8. Soporte y ayuda", "El boton verde Soporte te conecta por WhatsApp. Y este boton '? Ayuda' te vuelve a mostrar esta guia cuando lo necesites."),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.step = 0
        self.setWindowTitle("Ayuda de WillpoVoice")
        self.setModal(True)
        self.setFixedWidth(440)

        layout = QVBoxLayout(self)

        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 17px; font-weight: 700;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        self.text_label = QLabel()
        self.text_label.setWordWrap(True)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.text_label)

        self.progress_label = QLabel()
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.progress_label)

        row = QHBoxLayout()
        self.prev_button = QPushButton("<- Anterior")
        self.prev_button.clicked.connect(self.prev_step)
        row.addWidget(self.prev_button)

        self.next_button = QPushButton("Siguiente ->")
        self.next_button.clicked.connect(self.next_step)
        row.addWidget(self.next_button)
        layout.addLayout(row)

        self.show_step()

    def show_step(self):
        title, body = self.STEPS[self.step]
        self.title_label.setText(title)
        self.text_label.setText(body)
        self.progress_label.setText(
            f"Paso {self.step + 1} de {len(self.STEPS)}"
        )
        self.prev_button.setEnabled(self.step > 0)

        if self.step == len(self.STEPS) - 1:
            self.next_button.setText("Finalizar")
        else:
            self.next_button.setText("Siguiente ->")

    def prev_step(self):
        if self.step > 0:
            self.step -= 1
            self.show_step()

    def next_step(self):
        if self.step < len(self.STEPS) - 1:
            self.step += 1
            self.show_step()
        else:
            self.accept()


'''

if "class HelpWizard" not in text:
    text = text.replace(
        "class BannerDelegate", wizard_class + "class BannerDelegate", 1
    )

if "def show_help" not in text:
    method = '''    def show_help(self) -> None:
        wizard = HelpWizard(self)
        wizard.exec()

'''
    text = text.replace(
        "    def showEvent(self, event):",
        method + "    def showEvent(self, event):",
        1,
    )

if "help_button" not in text:
    m = re.search(r"[^\n]*self\.support_button\s*=\s*QPushButton\([^\n]*", text)
    m2 = re.search(r"[^\n]*(\w+)\.addWidget\(self\.support_button\)[^\n]*", text)

    if m and m2:
        layout_name = m2.group(1)

        create_line = m.group(0)
        ind = " " * (len(create_line) - len(create_line.lstrip()))
        help_create = (
            create_line
            + f"\n{ind}self.help_button = QPushButton(\"? Ayuda\")"
            + f"\n{ind}self.help_button.setToolTip(\"Guia paso a paso de WillpoVoice\")"
            + f"\n{ind}self.help_button.clicked.connect(self.show_help)"
        )
        text = text.replace(create_line, help_create, 1)

        add_line = m2.group(0)
        ind2 = " " * (len(add_line) - len(add_line.lstrip()))
        help_add = add_line + f"\n{ind2}{layout_name}.addWidget(self.help_button)"
        text = text.replace(add_line, help_add, 1)

        print("Boton de ayuda creado junto a Soporte.")
    else:
        print("AVISO: no se encontro el boton Soporte para anclar la ayuda.")

path.write_text(text, encoding="utf-8")
print("Parche de ayuda y exportar aplicado.")
