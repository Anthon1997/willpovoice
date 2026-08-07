from __future__ import annotations

from typing import Dict, List, Optional

from adapters.sapi_adapter import SAPIAdapter
from core.exceptions import VoiceNotFoundError


class VoiceManager:
    """
    Administra voces disponibles y selección de voz.
    """

    def __init__(self, adapter: SAPIAdapter):
        self.adapter = adapter

    def get_available_voice_names(self) -> List[str]:
        """
        Devuelve solo los nombres/descripciones de voces.
        """
        return [
            voice["description"]
            for voice in self.adapter.list_voices()
        ]

    def search(self, query: str = "") -> List[Dict[str, str]]:
        """
        Busca voces por texto.
        """
        return self.adapter.find_voices(query)

    def select_voice(self, query: str) -> bool:
        """
        Selecciona la primera voz que coincida con query.
        """
        query = query.strip()

        if not query:
            return False

        voices = self.adapter.find_voices(query)

        if not voices:
            raise VoiceNotFoundError(
                f"No se encontró ninguna voz para: {query}"
            )

        return self.adapter.set_voice(voices[0]["description"])

    def select_first_available(self) -> bool:
        """
        Selecciona la primera voz disponible.
        """
        voices = self.adapter.list_voices()

        if not voices:
            return False

        return self.adapter.set_voice(voices[0]["description"])

    @property
    def current_voice_description(self) -> Optional[str]:
        """
        Devuelve la voz actual.
        """
        return self.adapter.current_voice_description