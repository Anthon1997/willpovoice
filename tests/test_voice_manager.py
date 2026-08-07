from unittest.mock import MagicMock

import pytest

from core.exceptions import VoiceNotFoundError
from core.voice_manager import VoiceManager


VOICES = [
    {"id": "1", "description": "Voz Uno"},
    {"id": "2", "description": "Voz Dos"},
]


@pytest.fixture
def manager():
    adapter = MagicMock()
    adapter.list_voices.return_value = VOICES
    adapter.set_voice.return_value = True
    return VoiceManager(adapter)


def test_get_available_voice_names(manager):
    assert manager.get_available_voice_names() == ["Voz Uno", "Voz Dos"]


def test_select_voice_empty_returns_false(manager):
    assert manager.select_voice("   ") is False


def test_select_voice_not_found_raises(manager):
    manager.adapter.find_voices.return_value = []
    with pytest.raises(VoiceNotFoundError):
        manager.select_voice("NoExiste")


def test_select_voice_found(manager):
    manager.adapter.find_voices.return_value = [VOICES[1]]
    assert manager.select_voice("Dos") is True
    manager.adapter.set_voice.assert_called_once_with("Voz Dos")


def test_select_first_available_without_voices():
    adapter = MagicMock()
    adapter.list_voices.return_value = []
    manager = VoiceManager(adapter)
    assert manager.select_first_available() is False
