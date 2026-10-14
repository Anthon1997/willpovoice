from __future__ import annotations

import logging
import os
from typing import Dict, List, Optional

from adapters.sapi_adapter import SAPIAdapter


class NaturalVoiceAdapter(SAPIAdapter):
    """
    Adaptador orientado a NaturalVoiceSAPIAdapter.

    Por ahora funciona sobre SAPI estándar, pero deja puntos de extensión
    para detectar voces NaturalVoice o usar un ProgID personalizado.
    """

    DEFAULT_PROGID = os.getenv("NATURALVOICE_SAPI_PROGID", "SAPI.SpVoice")
    DEFAULT_KEYWORDS = (
        "naturalvoice",
        "natural voice",
        "natural",
    )

    def __init__(
        self,
        progid: Optional[str] = None,
        keywords: Optional[tuple[str, ...]] = None,
        logger: Optional[logging.Logger] = None,
    ):
        self.natural_keywords = tuple(
            keyword.lower() for keyword in (keywords or self.DEFAULT_KEYWORDS)
        )

        super().__init__(
            progid=progid or self.DEFAULT_PROGID,
            logger=logger or logging.getLogger("naturalvoice_tts.naturalvoice"),
        )

    def is_natural_voice(self, description: str) -> bool:
        """
        Indica si una voz parece ser NaturalVoice según palabras clave.
        """
        normalized_description = description.lower()

        return any(keyword in normalized_description for keyword in self.natural_keywords)

    def find_natural_voices(self) -> List[Dict[str, str]]:
        """
        Devuelve voces que coinciden con NaturalVoice.
        """
        try:
            voices = self.list_voices()
        except Exception as e:
            self.logger.error(f"Error al listar voces: {e}")
            return []

        return [voice for voice in voices if self.is_natural_voice(voice["description"])]

    def select_first_natural_voice(self) -> bool:
        """
        Intenta seleccionar la primera voz NaturalVoice disponible.
        """
        voices = self.find_natural_voices()

        if not voices:
            self.logger.info("No se encontraron voces NaturalVoice.")
            return False

        try:
            return self.set_voice(voices[0]["description"])
        except Exception as e:
            self.logger.error(f"Error al seleccionar la voz: {e}")
            return False
