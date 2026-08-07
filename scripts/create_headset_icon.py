from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

OUTPUT = Path("assets") / "icons" / "headset.png"

S = 32


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    d.arc([7, 5, 25, 23], 180, 360, fill=(255, 255, 255, 255), width=3)
    d.rounded_rectangle([5, 14, 11, 25], radius=3, fill=(255, 255, 255, 255))
    d.rounded_rectangle([21, 14, 27, 25], radius=3, fill=(255, 255, 255, 255))

    img.save(OUTPUT)
    print(f"Icono de soporte creado en: {OUTPUT}")


if __name__ == "__main__":
    main()
