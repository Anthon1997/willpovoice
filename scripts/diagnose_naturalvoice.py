from __future__ import annotations

import argparse
import importlib.util
import json
import platform
import sys
from datetime import datetime
from pathlib import Path


KEYWORDS = [
    "naturalvoice",
    "natural voice",
    "natural",
]

SAPI_PROGID = "SAPI.SpVoice"


def section(title: str) -> None:
    print()
    print("=" * 75)
    print(title)
    print("=" * 75)


def check_python() -> dict:
    return {
        "version": platform.python_version(),
        "executable": sys.executable,
        "architecture": platform.architecture()[0],
        "is_64bit": sys.maxsize > 2**32,
        "platform": platform.platform(),
        "machine": platform.machine(),
    }


def check_packages() -> dict:
    modules = [
        ("pywin32/win32com", "win32com"),
        ("pythoncom", "pythoncom"),
        ("PySide6", "PySide6"),
        ("comtypes", "comtypes"),
        ("pyttsx3", "pyttsx3"),
    ]

    result = {}

    for label, module_name in modules:
        try:
            spec = importlib.util.find_spec(module_name)
            result[label] = spec is not None
        except Exception:
            result[label] = False

    return result


def check_sapi(args: argparse.Namespace) -> dict:
    result = {
        "ok": False,
        "progid": SAPI_PROGID,
        "error": None,
        "voices": [],
        "natural_voices": [],
        "current_voice": None,
        "selected_voice": None,
        "audio_output": None,
        "speak_test": None,
    }

    try:
        import pythoncom
        import win32com.client
    except ImportError as exc:
        result["error"] = (
            "No se pudo importar pywin32. "
            "Instala con: pip install pywin32. "
            f"Detalle: {exc}"
        )
        return result

    try:
        try:
            pythoncom.CoInitialize()
        except Exception:
            pass

        sapi = win32com.client.Dispatch(SAPI_PROGID)

        try:
            result["audio_output"] = str(sapi.AudioOutput.GetDescription())
        except Exception:
            result["audio_output"] = None

        voices = []

        for token in sapi.GetVoices():
            try:
                description = str(token.GetDescription())
            except Exception:
                description = "Voz sin descripción"

            try:
                voice_id = str(token.Id)
            except Exception:
                voice_id = description

            is_natural = any(
                keyword in description.lower()
                for keyword in KEYWORDS
            )

            voices.append(
                {
                    "id": voice_id,
                    "description": description,
                    "natural": is_natural,
                }
            )

        result["voices"] = voices
        result["natural_voices"] = [
            voice for voice in voices if voice["natural"]
        ]

        try:
            result["current_voice"] = str(sapi.Voice.GetDescription())
        except Exception:
            result["current_voice"] = None

        if args.voice:
            found = False

            for token in sapi.GetVoices():
                try:
                    description = str(token.GetDescription())
                except Exception:
                    continue

                if args.voice.lower() in description.lower():
                    try:
                        sapi.Voice = token
                        result["selected_voice"] = description
                        found = True
                        break
                    except Exception as exc:
                        result["selected_voice"] = f"Error seleccionando voz: {exc}"

            if not found and not result["selected_voice"]:
                result["selected_voice"] = (
                    f"No se encontró ninguna voz que coincida con: {args.voice}"
                )

        if args.speak:
            text = args.text or "Diagnóstico de NaturalVoice TTS completado."

            try:
                sapi.Speak(text, 0)
                result["speak_test"] = "OK"
            except Exception as exc:
                result["speak_test"] = f"Error: {exc}"

        result["ok"] = True

    except Exception as exc:
        result["error"] = str(exc)

    return result


def enumerate_registry_voices() -> tuple[list[dict], str | None]:
    try:
        import winreg
    except Exception as exc:
        return [], f"No se pudo importar winreg: {exc}"

    entries: list[dict] = []

    hives = [
        (winreg.HKEY_LOCAL_MACHINE, "HKLM"),
        (winreg.HKEY_CURRENT_USER, "HKCU"),
    ]

    base_paths = [
        r"SOFTWARE\Microsoft\Speech\Voices",
        r"SOFTWARE\Microsoft\Speech_OneCore\Voices",
        r"SOFTWARE\WOW6432Node\Microsoft\Speech\Voices",
        r"SOFTWARE\WOW6432Node\Microsoft\Speech_OneCore\Voices",
    ]

    access_views = [
        ("default", winreg.KEY_READ),
    ]

    if hasattr(winreg, "KEY_WOW64_64KEY"):
        access_views.append(
            ("64-bit view", winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
        )

    if hasattr(winreg, "KEY_WOW64_32KEY"):
        access_views.append(
            ("32-bit view", winreg.KEY_READ | winreg.KEY_WOW64_32KEY)
        )

    for hive, hive_name in hives:
        for base_path in base_paths:
            for access_name, access in access_views:
                try:
                    with winreg.OpenKey(hive, base_path, 0, access) as base_key:
                        index = 0

                        while True:
                            try:
                                token_name = winreg.EnumKey(base_key, index)
                            except OSError:
                                break

                            index += 1

                            entry = {
                                "hive": hive_name,
                                "base_path": base_path,
                                "token": token_name,
                                "access_view": access_name,
                                "values": {},
                                "attributes": {},
                            }

                            token_path = f"{base_path}\\{token_name}"

                            try:
                                with winreg.OpenKey(
                                    hive,
                                    token_path,
                                    0,
                                    access,
                                ) as token_key:
                                    value_index = 0

                                    while True:
                                        try:
                                            value_name, value_data, _ = winreg.EnumValue(
                                                token_key,
                                                value_index,
                                            )
                                        except OSError:
                                            break

                                        entry["values"][value_name or "(default)"] = str(value_data)
                                        value_index += 1
                            except OSError:
                                pass

                            attributes_path = f"{token_path}\\Attributes"

                            try:
                                with winreg.OpenKey(
                                    hive,
                                    attributes_path,
                                    0,
                                    access,
                                ) as attributes_key:
                                    attr_index = 0

                                    while True:
                                        try:
                                            value_name, value_data, _ = winreg.EnumValue(
                                                attributes_key,
                                                attr_index,
                                            )
                                        except OSError:
                                            break

                                        entry["attributes"][value_name or "(default)"] = str(value_data)
                                        attr_index += 1
                            except OSError:
                                pass

                            entries.append(entry)

                except OSError:
                    pass
                except Exception:
                    pass

    return entries, None


def entry_matches_keywords(entry: dict, keywords: list[str]) -> bool:
    try:
        blob = json.dumps(entry, ensure_ascii=False).lower()
    except Exception:
        blob = str(entry).lower()

    return any(keyword in blob for keyword in keywords)


def build_recommendations(report: dict, args: argparse.Namespace) -> list[str]:
    recommendations = []

    packages = report["packages"]
    sapi = report["sapi"]
    registry = report["registry"]
    python_info = report["python"]

    if not packages.get("pywin32/win32com"):
        recommendations.append(
            "Instala pywin32: pip install pywin32"
        )

    if not packages.get("pythoncom"):
        recommendations.append(
            "pythoncom no está disponible. Normalmente se instala con pywin32."
        )

    if python_info.get("is_64bit"):
        recommendations.append(
            "Python es de 64 bits. Si NaturalVoiceSAPIAdapter solo tiene componente x86, "
            "debes usar Python de 32 bits o instalar/registrar la versión x64 del adaptador."
        )
    else:
        recommendations.append(
            "Python es de 32 bits. Si NaturalVoiceSAPIAdapter tiene componente x64, "
            "debes usar Python de 64 bits o instalar/registrar la versión x86 del adaptador."
        )

    if not sapi.get("ok"):
        recommendations.append(
            "SAPI no pudo inicializarse. Verifica que Windows tenga SAPI disponible, "
            "que pywin32 esté instalado y que no haya un problema COM."
        )
    else:
        if not sapi.get("voices"):
            recommendations.append(
                "SAPI está activo pero no se encontraron voces. "
                "Revisa la instalación de voces de Windows o del adaptador TTS."
            )

        if not sapi.get("natural_voices"):
            if registry.get("natural"):
                recommendations.append(
                    "Hay rastros de NaturalVoice en el registro, pero SAPI no expone voces NaturalVoice. "
                    "Puede que el adaptador no esté registrado correctamente, que requiera reinicio, "
                    "o que haya un problema de arquitectura x86/x64."
                )
            else:
                recommendations.append(
                    "No se encontraron voces NaturalVoice en SAPI ni rastros claros en el registro. "
                    "Verifica la instalación de NaturalVoiceSAPIAdapter."
                )

        if args.speak and sapi.get("speak_test") != "OK":
            recommendations.append(
                "La prueba de reproducción falló. Revisa el dispositivo de audio predeterminado, "
                "el volumen del sistema y si otra aplicación está bloqueando el audio."
            )

    if registry.get("error"):
        recommendations.append(
            f"No se pudo leer completamente el registro: {registry['error']}"
        )

    return recommendations


def print_report(report: dict, args: argparse.Namespace) -> None:
    section("1. Python")

    for key, value in report["python"].items():
        print(f"{key}: {value}")

    section("2. Paquetes")

    for package_name, installed in report["packages"].items():
        status = "OK" if installed else "FALTA"
        print(f"[{status}] {package_name}")

    section("3. SAPI")

    sapi = report["sapi"]

    if not sapi.get("ok"):
        print(f"[ERROR] No se pudo inicializar SAPI.")
        print(f"Detalle: {sapi.get('error')}")
    else:
        print(f"[OK] SAPI inicializado usando ProgID: {sapi.get('progid')}")

        if sapi.get("audio_output"):
            print(f"Salida de audio: {sapi.get('audio_output')}")

        print()
        print(f"Voces encontradas: {len(sapi.get('voices', []))}")

        for voice in sapi.get("voices", []):
            tag = " [NaturalVoice]" if voice.get("natural") else ""
            print(f"- {voice.get('description')}{tag}")

        print()
        print(f"Voces NaturalVoice detectadas: {len(sapi.get('natural_voices', []))}")

        if sapi.get("current_voice"):
            print(f"Voz actual: {sapi.get('current_voice')}")

        if sapi.get("selected_voice"):
            print(f"Voz seleccionada para prueba: {sapi.get('selected_voice')}")

        if args.speak:
            print(f"Prueba de reproducción: {sapi.get('speak_test')}")

    section("4. Registro de Windows")

    registry = report["registry"]

    if registry.get("error"):
        print(f"[ERROR] {registry.get('error')}")
    else:
        print(f"Entradas de registro relacionadas con voces: {len(registry.get('all', []))}")
        print(f"Entradas con coincidencias NaturalVoice: {len(registry.get('natural', []))}")

        if args.verbose:
            natural_entries = registry.get("natural", [])

            if natural_entries:
                print()
                print("Coincidencias NaturalVoice en registro:")

                for entry in natural_entries[:20]:
                    print(json.dumps(entry, indent=2, ensure_ascii=False))
                    print("-" * 40)

                if len(natural_entries) > 20:
                    print("Se mostraron solo las primeras 20 coincidencias.")
            else:
                print("No se mostraron coincidencias porque no se encontraron.")

    section("5. Recomendaciones")

    recommendations = report.get("recommendations", [])

    if not recommendations:
        print("[OK] No hay recomendaciones adicionales.")
    else:
        for recommendation in recommendations:
            print("-", recommendation)


def save_report(report: dict, output_path: str) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print()
    print(f"Reporte guardado en: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Diagnóstico para NaturalVoiceSAPIAdapter y SAPI."
    )

    parser.add_argument(
        "--speak",
        action="store_true",
        help="Realiza una prueba real de reproducción de voz.",
    )

    parser.add_argument(
        "--voice",
        type=str,
        help="Texto parcial para seleccionar una voz antes de la prueba.",
    )

    parser.add_argument(
        "--text",
        type=str,
        help="Texto personalizado para la prueba de voz.",
    )

    parser.add_argument(
        "--json",
        type=str,
        help="Guarda el reporte completo en un archivo JSON.",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Muestra detalles adicionales del registro.",
    )

    args = parser.parse_args()

    report = {
        "timestamp": datetime.now().astimezone().isoformat(),
        "python": check_python(),
        "packages": check_packages(),
    }

    report["sapi"] = check_sapi(args)

    registry_all, registry_error = enumerate_registry_voices()

    registry_natural = [
        entry
        for entry in registry_all
        if entry_matches_keywords(entry, KEYWORDS)
    ]

    report["registry"] = {
        "all": registry_all,
        "natural": registry_natural,
        "error": registry_error,
    }

    report["recommendations"] = build_recommendations(report, args)

    print_report(report, args)

    if args.json:
        save_report(report, args.json)

    if report["sapi"].get("ok"):
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())