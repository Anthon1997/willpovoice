from unittest.mock import MagicMock

import pytest

from core.tts_engine import TTSEngine


VOICES = [
    {"id": "1", "description": "Microsoft Dalia Online (Natural) - Spanish (Mexico)"},
    {"id": "2", "description": "Microsoft Helena Desktop - Spanish (Spain)"},
]


@pytest.fixture
def engine():
    adapter = MagicMock()
    adapter.list_voices.return_value = VOICES
    adapter.current_voice_description = VOICES[0]["description"]
    adapter.set_voice.return_value = True
    return TTSEngine(adapter=adapter)


def test_get_available_voices(engine):
    assert engine.get_available_voices() == [v["description"] for v in VOICES]


def test_speak_empty_text_raises(engine):
    with pytest.raises(ValueError):
        engine.speak("   ")


def test_speak_calls_adapter(engine):
    engine.speak("Hola")
    engine.adapter.speak.assert_called_once_with("Hola", asynchronous=False)


def test_speak_async_calls_adapter(engine):
    engine.speak_async("Hola")
    engine.adapter.speak.assert_called_once_with("Hola", asynchronous=True)


def test_select_voice_found(engine):
    engine.adapter.find_voices.return_value = [VOICES[0]]
    assert engine.select_voice("Dalia") is True
    engine.adapter.set_voice.assert_called_once_with(VOICES[0]["description"])


def test_select_voice_not_found_returns_false(engine):
    engine.adapter.find_voices.return_value = []
    assert engine.select_voice("NoExiste") is False


def test_stop_calls_adapter(engine):
    engine.stop()
    engine.adapter.stop.assert_called_once()
