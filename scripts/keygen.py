from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.license_manager import generate_key


def main() -> None:
    if len(sys.argv) > 1:
        machine_id = sys.argv[1].strip().upper()
    else:
        machine_id = input("ID de maquina: ").strip().upper()

    print(f"Clave para {machine_id}: {generate_key(machine_id)}")


if __name__ == "__main__":
    main()
