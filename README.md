# NaturalVoice TTS

Aplicación de escritorio para conversión de texto a voz

## Características

- Conversión de texto a voz.
- Selección de voces.
- Control de velocidad.
- Control de volumen.
- Interfaz gráfica con PySide6.
- Arquitectura modular.
- Pruebas automatizadas con pytest.
- Empaquetado con PyInstaller.

## Requisitos

- Windows 10/11
- Python 3.11 o superior
- NaturalVoiceSAPIAdapter instalado

## Instalación

```bash
python -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt