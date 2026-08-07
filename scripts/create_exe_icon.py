from __future__ import annotations

from pathlib import Path

from PIL import Image

LOGO = Path("assets") / "icons" / "logo.png"
ICO = Path("assets") / "icons" / "icon.ico"


def main() -> None:
    if not LOGO.exists():
        print("AVISO: no existe logo.png, se mantiene el icon.ico actual.")
        return

    src = Image.open(LOGO).convert("RGBA")

    side = max(src.width, src.height)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(src, ((side - src.width) // 2, (side - src.height) // 2), src)

    sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]

    ICO.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(ICO, sizes=sizes)

    print(f"icon.ico generado desde tu logo: {ICO}")


if __name__ == "__main__":
    main()
