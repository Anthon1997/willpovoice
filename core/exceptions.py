class TTSError(Exception):
    """Error general del sistema TTS."""


class EngineInitializationError(TTSError):
    """Error al inicializar el motor TTS."""


class VoiceNotFoundError(TTSError):
    """No se encontró la voz solicitada."""


class SpeechError(TTSError):
    """Error durante la reproducción de voz."""


class AudioExportError(TTSError):
    """Error al exportar audio."""