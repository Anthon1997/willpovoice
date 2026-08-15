from __future__ import annotations

import sys

from app.logger import setup_logging
from core.exceptions import TTSError


def main() -> int:
    setup_logging()

    try:
        from PySide6.QtWidgets import QApplication, QMessageBox

        try:

            from ui.modern_window import MainWindow

        except Exception:

            from ui.main_window import MainWindow
    except ImportError as exc:
        print(
            "Faltan dependencias para ejecutar la interfaz gráfica.\n"
            "Instala PySide6 con:\n\n"
            "pip install PySide6\n"
        )
        print(f"Detalle: {exc}")
        return 1

    app = QApplication(sys.argv)

    try:
        window = MainWindow()
    except TTSError as exc:
        QMessageBox.critical(
            None,
            "Error TTS",
            str(exc),
        )
        return 1
    except Exception as exc:
        QMessageBox.critical(
            None,
            "Error inesperado",
            f"Ocurrió un error inesperado al iniciar la aplicación:\n{exc}",
        )
        return 1

    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())