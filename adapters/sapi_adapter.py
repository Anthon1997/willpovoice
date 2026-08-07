from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

try:
    import pythoncom
    import win32com.client
except ImportError as exc:
    raise ImportError(
        "No está instalado pywin32. "
        "Instálalo con: pip install pywin32"
    ) from exc

from core.exceptions import (
    EngineInitializationError,
    SpeechError,
    VoiceNotFoundError,
)


class SAPIAdapter:
    """
    Adaptador base para motores TTS compatibles con SAPI.
    """

    DEFAULT_PROGID = "SAPI.SpVoice"

    # Flags SAPI
    SVSFlagsAsync = 1
    SVSFPurgeBeforeSpeak = 2

    def __init__(
        self,
        progid: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ):
        self.progid = progid or self.DEFAULT_PROGID
        self.logger = logger or logging.getLogger("naturalvoice_tts.sapi")

        self.sapi: Any = None
        self._voices_cache: List[Dict[str, Any]] = []

        self._initialize_com()
        self._initialize_sapi()
        self._refresh_voices()

    def _initialize_com(self) -> None:
        """
        Inicializa COM si es necesario.

        En aplicaciones GUI puede que COM ya esté inicializado por el hilo principal.
        Por eso se ignora cualquier error leve.
        """
        try:
            pythoncom.CoInitialize()
        except Exception:
            self.logger.debug(
                "COM ya estaba inicializado o no fue posible inicializarlo explícitamente."
            )

    def _initialize_sapi(self) -> None:
        """
        Crea el objeto SAPI principal.
        """
        try:
            self.sapi = win32com.client.Dispatch(self.progid)
            self.logger.info("Objeto SAPI inicializado correctamente.")
        except Exception as exc:
            self.logger.exception("No se pudo crear el objeto SAPI.")
            raise EngineInitializationError(
                f"No se pudo inicializar SAPI con ProgID '{self.progid}'. "
                "Verifica que SAPI esté disponible en Windows y que la arquitectura "
                "de Python coincida con el componente TTS que estás usando."
            ) from exc

    def _refresh_voices(self) -> None:
        """
        Recarga las voces disponibles desde SAPI.
        """
        try:
            self._voices_cache = []

            for token in self.sapi.GetVoices():
                try:
                    description = str(token.GetDescription())
                except Exception:
                    description = "Voz sin descripción"

                try:
                    voice_id = str(token.Id)
                except Exception:
                    voice_id = description

                self._voices_cache.append(
                    {
                        "id": voice_id,
                        "description": description,
                        "token": token,
                    }
                )

            self.logger.info("Voces SAPI cargadas: %s", len(self._voices_cache))

        except Exception as exc:
            self.logger.exception("No se pudieron enumerar las voces SAPI.")
            raise EngineInitializationError(
                "No se pudieron cargar las voces SAPI."
            ) from exc

    def list_voices(self) -> List[Dict[str, str]]:
        """
        Devuelve metadatos de las voces disponibles.
        """
        return [
            {
                "id": voice["id"],
                "description": voice["description"],
            }
            for voice in self._voices_cache
        ]

    def find_voices(self, query: str = "") -> List[Dict[str, str]]:
        """
        Busca voces por coincidencia parcial.
        """
        if not query:
            return self.list_voices()

        normalized_query = query.strip().lower()

        if not normalized_query:
            return self.list_voices()

        return [
            {
                "id": voice["id"],
                "description": voice["description"],
            }
            for voice in self._voices_cache
            if normalized_query in voice["description"].lower()
        ]

    def _get_voice_token(self, query: str) -> Optional[Any]:
        """
        Busca el token COM de una voz usando coincidencia parcial.
        """
        normalized_query = query.strip().lower()

        if not normalized_query:
            return None

        for voice in self._voices_cache:
            if normalized_query in voice["description"].lower():
                return voice["token"]

        return None

    def set_voice(self, query: str) -> bool:
        """
        Selecciona una voz por coincidencia parcial.
        """
        token = self._get_voice_token(query)

        if token is None:
            raise VoiceNotFoundError(
                f"No se encontró una voz que coincida con: {query}"
            )

        try:
            self.sapi.Voice = token
            self.logger.info("Voz seleccionada: %s", query)
            return True
        except Exception as exc:
            self.logger.exception("No se pudo seleccionar la voz.")
            raise VoiceNotFoundError(
                f"No se pudo seleccionar la voz: {query}"
            ) from exc

    @property
    def current_voice_description(self) -> Optional[str]:
        """
        Devuelve la descripción de la voz actualmente seleccionada.
        """
        try:
            return str(self.sapi.Voice.GetDescription())
        except Exception:
            return None

    def speak(self, text: str, asynchronous: bool = False) -> None:
        """
        Reproduce texto.

        Si asynchronous=True, la reproducción no bloquea el hilo actual.
        """
        if not text or not text.strip():
            raise ValueError("El texto a reproducir no puede estar vacío.")

        flags = 0

        if asynchronous:
            flags |= self.SVSFlagsAsync

        try:
            self.sapi.Speak(text, flags)
        except Exception as exc:
            self.logger.exception("Error al reproducir texto.")
            raise SpeechError("No se pudo reproducir el texto.") from exc

    def stop(self) -> None:
        """
        Detiene la reproducción actual.
        """
        try:
            flags = self.SVSFlagsAsync | self.SVSFPurgeBeforeSpeak
            self.sapi.Speak("", flags)
            self.logger.info("Reproducción detenida.")
        except Exception:
            self.logger.exception("No se pudo detener la reproducción.")

    def set_rate(self, rate: int) -> None:
        """
        Establece la velocidad de la voz.

        Normalmente SAPI acepta valores entre -10 y 10.
        """
        try:
            self.sapi.Rate = max(-10, min(10, int(rate)))
        except Exception:
            self.logger.exception("No se pudo establecer la velocidad.")

    def set_volume(self, volume: int) -> None:
        """
        Establece el volumen.

        Normalmente SAPI acepta valores entre 0 y 100.
        """
        try:
            self.sapi.Volume = max(0, min(100, int(volume)))
        except Exception:
            self.logger.exception("No se pudo establecer el volumen.")

    def refresh(self) -> None:
        """
        Recarga las voces disponibles.
        """
        self._refresh_voices()