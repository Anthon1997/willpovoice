import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """
    Configura el logger principal de la aplicación.

    Crea logs en consola y en logs/app.log.
    """
    log_dir = Path("logs")
    try:
        log_dir.mkdir(exist_ok=True)
    except Exception:
        # Si no se puede crear la carpeta de logs, seguimos sin archivo de log.
        pass

    logger = logging.getLogger("naturalvoice_tts")
    logger.setLevel(logging.DEBUG)

    # Evitar agregar handlers múltiples si setup_logging se llama varias veces.
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    try:
        file_handler = RotatingFileHandler(
            log_dir / "app.log",
            maxBytes=1_000_000,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception:
        logger.debug("No se pudo crear el handler de archivo de logs.")

    return logger