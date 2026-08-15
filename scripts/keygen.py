from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.license_manager import generate_key, generate_key_v2


def main() -> None:
    args = [a.strip().upper() for a in sys.argv[1:]]
    if args and args[0] in ("M", "A", "L"):
        print(f"Clave de venta ({args[0]}): {generate_key_v2(args[0])}")
    else:
        mid = args[0] if args else input("ID de maquina: ").strip().upper()
        print(f"Clave legacy para {mid}: {generate_key(mid)}")


if __name__ == "__main__":
    main()
