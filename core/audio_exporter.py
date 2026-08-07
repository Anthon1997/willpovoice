from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

try:
    import win32com.client
except ImportError as exc:
    raise ImportError(
        "No está instalado pywin32. Instálalo con: pip install pywin32"
    ) from exc

from core.exceptions import AudioExportError

SSFM_CREATE_OVERWRITE = 3


class AudioExporter:
    """
    Exporta texto a archivo WAV usando SAPI.SpFileStream.
    """

    def __init__(self, adapter=None, logger: Optional[logging.Logger] = None):
        self.adapter = adapter
        self.logger = logger or logging.getLogger("naturalvoice_tts.exporter")

    def save_text_to_wav(
        self,
        text: str,
        output_path,
        voice_query: Optional[str] = None,
        rate: int = 0,
        volume: int = 100,
    ) -> Path:
        if not text or not text.strip():
            raise ValueError("El texto a exportar no puede estar vacío.")

        output_path = Path(output_path)

        if output_path.suffix.lower() != ".wav":
            output_path = output_path.with_suffix(".wav")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            sapi = win32com.client.Dispatch("SAPI.SpVoice")

            if self.adapter is not None:
                if voice_query:
                    self.adapter.set_voice(voice_query)

                try:
                    sapi.Voice = self.adapter.sapi.Voice
                except Exception:
                    self.logger.warning(
                        "No se pudo copiar la voz del motor; se usará la predeterminada."
                    )

            sapi.Rate = max(-10, min(10, int(rate)))
            sapi.Volume = max(0, min(100, int(volume)))

            stream = win32com.client.Dispatch("SAPI.SpFileStream")
            stream.Open(str(output_path), SSFM_CREATE_OVERWRITE, False)

            sapi.AudioOutputStream = stream
            sapi.Speak(text)
            stream.Close()
            sapi.AudioOutputStream = None

            self.logger.info("Audio exportado a: %s", output_path)
            return output_path

        except AudioExportError:
            raise
        except Exception as exc:
            self.logger.exception("Error exportando audio.")
            raise AudioExportError(
                f"No se pudo exportar el audio a {output_path}. Detalle: {exc}"
            ) from exc
