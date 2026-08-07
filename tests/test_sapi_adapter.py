import pytest

from adapters.sapi_adapter import SAPIAdapter
from core.exceptions import VoiceNotFoundError


@pytest.fixture(scope="module")
def adapter():
    return SAPIAdapter()


def test_list_voices_not_empty(adapter):
    assert len(adapter.list_voices()) > 0


def test_find_natural_voices(adapter):
    assert len(adapter.find_voices("natural")) > 0


def test_set_voice_inexistente(adapter):
    with pytest.raises(VoiceNotFoundError):
        adapter.set_voice("voz_inexistente_xyz_123")
