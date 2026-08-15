from __future__ import annotations

import logging
from typing import List, Optional

from adapters.naturalvoice_adapter import NaturalVoiceAdapter
from core.voice_manager import VoiceManager
from core.exceptions import VoiceNotFoundError


class TTSEngine:
    """
    Motor principal de texto a voz.

    Esta clase no debe conocer detalles de la interfaz gráfica.
    Solo expone operaciones simples:
    - obtener voces
    - seleccionar voz
    - hablar
    - detener
    - configurar velocidad/volumen
    """

    def __init__(
        self,
        adapter: Optional[NaturalVoiceAdapter] = None,
        logger: Optional[logging.Logger] = None,
    ):
        self.logger = logger or logging.getLogger("naturalvoice_tts.engine")

        self.adapter = adapter or NaturalVoiceAdapter(logger=self.logger)
        self.voice_manager = VoiceManager(self.adapter)

    def get_available_voices(self) -> List[str]:
        """
        Devuelve las descripciones de las voces disponibles.
        """
        return self.voice_manager.get_available_voice_names()

    def refresh_voices(self) -> None:
        """
        Recarga las voces disponibles.
        """
        self.adapter.refresh()
        self.logger.info("Lista de voces actualizada.")

    def select_voice(self, voice_query: str) -> bool:
        """
        Selecciona una voz por coincidencia parcial.
        """
        try:
            return self.voice_manager.select_voice(voice_query)
        except VoiceNotFoundError as exc:
            self.logger.warning(str(exc))
            return False

    def select_natural_voice_if_available(self) -> bool:
        """
        Intenta seleccionar automáticamente una voz NaturalVoice.
        """
        if hasattr(self.adapter, "select_first_natural_voice"):
            return self.adapter.select_first_natural_voice()

        return False

    @property
    def current_voice_description(self) -> Optional[str]:
        """
        Devuelve la descripción de la voz actual.
        """
        return self.adapter.current_voice_description

    def speak(self, text: str) -> None:
        """
        Reproduce texto de forma sincronizada.
        """
        if not text or not text.strip():
            raise ValueError("El texto no puede estar vacío.")

        self.logger.info("Reproduciendo texto de forma sincronizada.")
        self.adapter.speak(text, asynchronous=False)

    def speak_async(self, text: str) -> None:
        """
        Reproduce texto de forma asíncrona.
        """
        if not text or not text.strip():
            raise ValueError("El texto no puede estar vacío.")

        self.logger.info("Reproduciendo texto de forma asíncrona.")
        from core.text_normalizer import (
            needs_homograph_guard,
            normalize_for_tts,
        )
        desc = ""
        try:
            desc = self.adapter.sapi.Voice.GetDescription()
        except Exception:
            desc = ""
        text = normalize_for_tts(
            text, guard=needs_homograph_guard(desc))
        self.adapter.speak(text, asynchronous=True)

    def stop(self) -> None:
        """
        Detiene la reproducción.
        """
        self.adapter.stop()

    def set_rate(self, rate: int) -> None:
        """
        Establece la velocidad de voz.
        """
        self.adapter.set_rate(rate)

    def set_volume(self, volume: int) -> None:
        """
        Establece el volumen.
        """
        self.adapter.set_volume(volume)