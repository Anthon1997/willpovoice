from __future__ import annotations

import argparse
import sys


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prueba mínima de SAPI para aislar el problema."
    )

    parser.add_argument(
        "--speak",
        action="store_true",
        help="Realiza una prueba real de reproducción de voz.",
    )

    args = parser.parse_args()

    try:
        import pythoncom
        import win32com.client
    except ImportError as exc:
        print("[ERROR] No se pudo importar pywin32.")
        print("Instala con:")
        print("pip install pywin32")
        print()
        print(f"Detalle: {exc}")
        return 1

    try:
        pythoncom.CoInitialize()
        print("[OK] pythoncom.CoInitialize()")
    except Exception as exc:
        print(f"[WARN] No se pudo inicializar COM explícitamente: {exc}")

    # 1. Crear objeto SAPI
    try:
        sapi = win32com.client.Dispatch("SAPI.SpVoice")
        print("[OK] win32com.client.Dispatch('SAPI.SpVoice')")
    except Exception as exc:
        print("[ERROR] No se pudo crear el objeto SAPI.SpVoice.")
        print(f"Detalle: {exc}")
        return 2

    # 2. Enumerar voces
    try:
        tokens = sapi.GetVoices()
        print("[OK] sapi.GetVoices()")

        count = 0

        print()
        print("Voces encontradas:")

        for token in tokens:
            count += 1
            try:
                description = token.GetDescription()
                print(f"- {description}")
            except Exception as exc:
                print(f"- Voz sin descripción. Error: {exc}")

        print()
        print(f"Total de voces: {count}")

        if count == 0:
            print("[WARN] SAPI respondió, pero no devolvió voces.")

    except Exception as exc:
        print("[ERROR] No se pudieron enumerar las voces.")
        print(f"Detalle: {exc}")
        return 3

    # 3. Consultar salida de audio, pero sin romper la prueba
    try:
        audio_output = sapi.AudioOutput.GetDescription()
        print(f"[OK] Salida de audio: {audio_output}")
    except Exception as exc:
        print("[WARN] No se pudo consultar la salida de audio.")
        print(f"Detalle: {exc}")
        print()
        print("Esto puede indicar un problema con el dispositivo de audio")
        print("predeterminado, el servicio de audio de Windows o una máquina")
        print("virtual/sesión remota sin audio.")

    # 4. Prueba de voz opcional
    if args.speak:
        try:
            sapi.Speak("Prueba de voz SAPI.")
            print("[OK] sapi.Speak() completado.")
        except Exception as exc:
            print("[ERROR] No se pudo reproducir la voz.")
            print(f"Detalle: {exc}")
            return 4
    else:
        print()
        print("Puedes probar la reproducción con:")
        print("python scripts/check_sapi_min.py --speak")

    return 0


if __name__ == "__main__":
    sys.exit(main())