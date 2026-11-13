from __future__ import annotations
import sys as _sys
import os as _os
# STDOUT/STDERR seguros en modo compilado (sin consola o redirigido):
# evita UnicodeEncodeError 'charmap' con emojis y crash con stdout=None.
for _name in ("stdout", "stderr"):
    _stream = getattr(_sys, _name, None)
    if _stream is None:
        setattr(_sys, _name, open(_os.devnull, "w", encoding="utf-8"))
    else:
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

import sys

from app.logger import setup_logging
from core.exceptions import TTSError


def _splash_image_path() -> str:
    from pathlib import Path
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    for rel in (
        ("assets", "icons", "splash.png"),
        ("assets", "splash.png"),
        ("assets", "icons", "logo_new.png"),
        ("assets", "logo_new.png"),
        ("assets", "icons", "logo.png"),
    ):
        p = base.joinpath(*rel)
        if p.exists():
            return str(p)
    return str(base.joinpath("assets", "icons", "logo.png"))


def main() -> int:
    setup_logging()

    try:
        from PySide6.QtWidgets import QApplication, QMessageBox
    except ImportError as exc:
        print(
            "Faltan dependencias para ejecutar la interfaz gráfica.\n"
            "Instala PySide6 con:\n\n"
            "pip install PySide6\n"
        )
        print(f"Detalle: {exc}")
        return 1

    app = QApplication(sys.argv)

    splash = None
    try:
        from ui.splash import WillpoSplash
        splash = WillpoSplash(_splash_image_path(), subtitle="WillpoVoice Premium")
        splash.show()
        app.processEvents()
    except Exception:
        splash = None

    def _status(msg, prog=None):
        if splash is not None:
            try:
                splash.set_status(msg, prog)
            except Exception:
                pass

    _status("Cargando interfaz...", 0.25)
    try:
        from ui.modern_window import MainWindow
    except Exception:
        from ui.main_window import MainWindow

    _status("Inicializando voces y motor de clonacion...", 0.55)
    try:
        window = MainWindow()
    except TTSError as exc:
        if splash is not None:
            splash.close()
        QMessageBox.critical(None, "Error TTS", str(exc))
        return 1
    except Exception as exc:
        if splash is not None:
            splash.close()
        QMessageBox.critical(
            None,
            "Error inesperado",
            f"Ocurrió un error inesperado al iniciar la aplicación:\n{exc}",
        )
        return 1

    _status("Preparando interfaz...", 0.9)
    if splash is not None:
        splash.finish(window)
    else:
        window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())