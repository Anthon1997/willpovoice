from __future__ import annotations

import argparse
import sys

from app.logger import setup_logging
from core.exceptions import TTSError
from core.tts_engine import TTSEngine


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="willpovoice",
        description="CLI para WillpoVoice TTS.",
    )

    parser.add_argument(
        "--text",
        type=str,
        help="Texto a reproducir. Usa '-' para leer desde stdin.",
    )

    parser.add_argument(
        "--voice",
        type=str,
        help="Nombre parcial de la voz a seleccionar.",
    )

    parser.add_argument(
        "--rate",
        type=int,
        default=0,
        help="Velocidad de voz entre -10 y 10.",
    )

    parser.add_argument(
        "--volume",
        type=int,
        default=100,
        help="Volumen entre 0 y 100.",
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="Muestra las voces disponibles.",
    )

    parser.add_argument(
        "--natural",
        action="store_true",
        help="Intenta seleccionar automáticamente una voz NaturalVoice.",
    )

    parser.add_argument(
        "--output",
        type=str,
        help="Ruta del archivo WAV para exportar el texto.",
    )

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    setup_logging()

    try:
        engine = TTSEngine()
    except TTSError as exc:
        print(f"Error al inicializar el motor TTS: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Error inesperado: {exc}", file=sys.stderr)
        return 1

    try:
        if args.voice:
            engine.select_voice(args.voice)
        elif args.natural:
            engine.select_natural_voice_if_available()

        engine.set_rate(args.rate)
        engine.set_volume(args.volume)

        if args.list:
            voices = engine.get_available_voices()

            if not voices:
                print("No hay voces disponibles.")
                return 0

            print("Voces disponibles:")
            for voice in voices:
                print("-", voice)

            current_voice = engine.current_voice_description

            if current_voice:
                print()
                print("Voz actual:")
                print("-", current_voice)

            return 0

        if args.text:
            text = args.text

            if text == "-":
                text = sys.stdin.read()

            if args.output:
                from core.audio_exporter import AudioExporter

                exporter = AudioExporter(adapter=engine.adapter)
                result = exporter.save_text_to_wav(text, args.output)
                print(f"Audio guardado en: {result}")
                return 0

            engine.speak(text)
            return 0

        parser.print_help()
        return 0

    except KeyboardInterrupt:
        print("\nOperación cancelada por el usuario.", file=sys.stderr)
        return 130

    except ValueError as exc:
        print(f"Error de validación: {exc}", file=sys.stderr)
        return 1

    except TTSError as exc:
        print(f"Error TTS: {exc}", file=sys.stderr)
        return 1

    except Exception as exc:
        print(f"Error inesperado: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
