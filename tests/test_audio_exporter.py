import pytest

from adapters.sapi_adapter import SAPIAdapter
from core.audio_exporter import AudioExporter


@pytest.fixture(scope="module")
def exporter():
    adapter = SAPIAdapter()
    return AudioExporter(adapter=adapter)


def test_export_wav_creates_file(exporter, tmp_path):
    try:
        exporter.adapter.set_voice("Helena")
    except Exception:
        pytest.skip("No hay voz Desktop disponible para exportar.")

    out = tmp_path / "prueba.wav"
    result = exporter.save_text_to_wav(
        "Hola, esta es una prueba de exportacion.", out
    )

    assert result.exists()
    assert result.stat().st_size > 1000


def test_export_empty_text_raises(exporter, tmp_path):
    with pytest.raises(ValueError):
        exporter.save_text_to_wav("   ", tmp_path / "x.wav")
